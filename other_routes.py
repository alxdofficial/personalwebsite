from app import db
from app import app
from flask import request, render_template, flash, redirect,jsonify
from app import socketio
import json
from flask_socketio import emit


@app.route('/2',methods = ['GET','POST'])
def fn2():
    return render_template('chatdemo.html')



@app.route('/chatdemo',methods = ['GET','POST'])
def chat_demo():
    return render_template('chatdemo.html')

@socketio.on('user-connected', namespace='/chatdemo')
def handle_user_connected(json,methods=['GET','POST']):
    name = json['name']
    print(name + ' user connected')
    emit('new-user-joined')


# @socketio.on('chat-sent')
# def handle_chat_sent(json,methods=['GET','POST']):
#     print('someone sent chat')
#     print(str(json))
#     socketio('new-message-available',json)



