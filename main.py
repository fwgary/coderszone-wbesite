from website import create_app, db
from website.models import User, Message
from flask import Flask, render_template
from flask_login import login_required, current_user
from flask_socketio import SocketIO, emit

app = create_app()
socketio = SocketIO(app)

@app.route('/chat')
@login_required
def index():
    messages = Message.query.all()
    return render_template('./chat.html', user=current_user, nickname=current_user.nick_name, messages=messages)

@app.route('/devchat')
@login_required
def devchat():
    messages = Message.query.all()
    return render_template('./devchat.html', user=current_user, nickname=current_user.nick_name, messages=messages)

@socketio.on('connected')
def conn(msg):
    return {'data': 'Ok'}


@socketio.on('client_message')
def receive_message(data):
    message = Message(nickname=data['nickname'], message=data['message'])
    db.session.add(message)
    db.session.commit()
    emit('server_message', data, broadcast=True)

if __name__ == '__main__':
  socketio.run(app, debug=True, use_reloader=True, log_output=True, allow_unsafe_werkzeug=True)
