from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Note, ips, devNote
from flask_socketio import SocketIO, emit
from . import db
import json
import requests

views = Blueprint('views', __name__)


@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')  #Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(
                data=note,
                user_id=current_user.id)  #providing the schema for the note
            db.session.add(new_note)  #adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("notes.html", user=current_user)


@views.route('/requests', methods=['GET', 'POST'])
def requestspage():
    if request.method == 'POST':
        url = "https://discord.com/api/webhooks/1286054108431913062/x_WFUbY2Amti2W_5XIaisGmRiaJkZuTaO7YjhQbDQW1FTMMTJZVINt9z8dCh-vQqXiAQ"
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('request')
        data = {
                "content" : f"<@&1286018937607164054> \n**A NEW REQUEST CAME IN!**\n**Name:**```{name}```\n**Email:** ```{email}```\n**Message:**```{message}```",
                "username": "Request bot"
            }
        requests.post(url, json = data)
        flash("You're request was received!", category='success')
        return redirect(url_for('views.home'))
    return render_template("requests.html", user=current_user)

@views.route('/devtesting', methods=['GET', 'POST'])
def devtesting():
    return render_template("testing.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(
        request.data)  # this function expects a JSON from the INDEX.js file
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
