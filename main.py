from website import create_app, db
from website.models import User, Message, ips, DevMessage
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask_socketio import SocketIO, emit
import socket

app = create_app()
socketio = SocketIO(app)

@app.route('/chat')
@login_required
def index():
    messages = Message.query.all()
    return render_template('./chat.html', user=current_user, nickname=current_user.nick_name, messages=messages)

@app.route('/store_user_data', methods=['POST'])
def store_user_data():
    data = request.get_json()
    ip = data['ip_address']
    time = data['time']

    # Create a new user object and store it in the database
    IPS = ips(ip=ip, time=time) # type: ignore
    db.session.add(IPS)
    db.session.commit()

    return jsonify({'message': 'User data stored successfully'})

@app.route('/home')
@login_required
def home():
    IPS = ips.query.all()
    return render_template("home.html", user=current_user, ips=IPS)

@app.route('/')
def home_signed_out():
    IPS = ips.query.all()
    return render_template("home.html", user=current_user, ips=IPS)

@app.route('/devʯʘʍʚ')
def devhome():
    IPS = ips.query.all()
    return render_template("devhome.html", ips=IPS, user=current_user)

@app.route('/dev')
def dev():
    return render_template('checkaccess.html')

@app.route('/devʕʯʌʇ')
def devchat():
    messages = Message.query.all()
    return render_template('devchat.html', user=current_user, nickname=current_user.nick_name, messages=messages)

@app.route('/devsʕʯʌʇ')
def devchat2():
    devmessages = DevMessage.query.all()
    return render_template('devschat.html', user=current_user, messages=devmessages)
    
@socketio.on('connected')
def conn(msg):
    return {'data': 'Ok'}

@socketio.on('dev_message')
def receive_devmessage(data):
    message = DevMessage(nickname=data['nickname'], message=data['message'])
    db.session.add(message)
    db.session.commit()
    emit('dev_server_message', data, broadcast=True)

@socketio.on('client_message')
def receive_message(data):
    message = Message(nickname=data['nickname'], message=data['message'])
    db.session.add(message)
    db.session.commit()
    emit('server_message', data, broadcast=True)

if __name__ == '__main__':
  socketio.run(app,
                 host='0.0.0.0',
                 port=81,
                 debug=True,
                 use_reloader=True,
                 log_output=True)
