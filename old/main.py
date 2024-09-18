#! /usr/bin/python
# -*- encoding: utf-8 -*-

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit
import json

db = SQLAlchemy()
DB_NAME = "database.db"

app = Flask(__name__,
                                                template_folder='templates',
                                                static_url_path='/static/',
                                                static_folder='static')

app.config['SECRET_KEY'] = 'ines'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
socketio = SocketIO(app)

def create_app():
    app = Flask(__name__,
        template_folder='templates',
        static_url_path='/static/',
        static_folder='static')
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    socketio = SocketIO(app)


    @socketio.on('connected')
    def conn(msg):
      return {'data': 'Ok'}


    @socketio.on('client_message')
    def receive_message(data):
      emit('server_message', data, broadcast=True)

    from .models import User, Note

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')

@app.route('/chat')
def index():
    return render_template('./index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('auth.login'))


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        nick_name = request.form.get('nickName')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif nick_name is not None:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='scrypt'), nick_name=nick_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='scrypt'), nick_name=first_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@app.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=True, log_output=True)
