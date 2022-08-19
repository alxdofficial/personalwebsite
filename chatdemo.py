from app import db
from app import app
from flask import request, render_template, flash, redirect,jsonify
from app import socketio
from flask_login import LoginManager ,login_user, login_required, current_user, logout_user
import json
from flask_socketio import emit,join_room,leave_room
from datetime import datetime, timedelta
import random,string
# global var to add users to socketio rooms when they connect
socketroomnames = []

@app.route('/chatdemo/<userid>',methods = ['GET','POST'])
def chat_demo(userid):
    from models import User,Chatroom, Roomassignment, Chatmessage
    # log into default user, alex if no user specified
    if userid == '':
        user = User.query.get('alexid')
        login_user(user)
    else:
        user = User.query.get(userid)
        login_user(user)

    # find all rooms user is assigned to
    roomassignments = Roomassignment.query.filter(Roomassignment.userid == current_user.id)
    chatrooms = []
    for roomassignment in roomassignments:
        chatrooms.append(Chatroom.query.get(roomassignment.roomid))
    #the chatrooms array is of model.Chatroom object, which doesnt contain the text of its most recent message, only the id.
    #here a new 'info' class and array is created, denoted by '_', to be passed into jinja templates for display

    class Chatroom_:
        def __init__(self, id, roomname, socketroomname,mostrecentmessagetext,mostrecentmessagetime):
            self.id = id
            self.roomname = roomname
            self.socketroomname = socketroomname
            self.mostrecentmessagetext = mostrecentmessagetext
            self.mostrecentmessagetime = mostrecentmessagetime

    chatrooms_ = []

    for chatroom in chatrooms:
        recentmessage = Chatmessage.query.get(chatroom.mostrecentmessageid)
        chatrooms_.append(Chatroom_(chatroom.id,chatroom.roomname,chatroom.socketroomname,recentmessage.messagetext,
                                    recentmessage.timesent.strftime("%b %d %H:%M")))
        socketroomnames.append(chatroom.socketroomname)

    # get room with most recent message, and fetch 10 of its recent existing messages in decreasing order(from new to
    # old)
    chatrooms.sort(key= lambda roomvar : Chatmessage.query.get(roomvar.mostrecentmessageid).timesent, reverse=True)
    defaultroom = chatrooms[0]

    messages = Chatmessage.query.filter(Chatmessage.roomid == defaultroom.id).filter(Chatmessage.timesent >= datetime.utcnow() - timedelta(hours=4)).order_by(Chatmessage.timesent.desc()).limit(10).all()
    messages.reverse() #taking the last 10 sent between now and 4 hours ago, which the sql retrieves in latest to earlist order, but reversed
    # in order to display in chronological order
    # print(datetime.utcnow() - timedelta(hours=4))
    # print(messages)

    # like before the messages here are just sql query items, the stored senttime is in UTC, and arent formatted, and
    # the user is stored just by id, so another  info class is created denoted by '_'

    class Chatmessage_:
        def __init__(self, id, username, messagetext, timesent):
            self.id = id
            self.username = username
            self.messagetext = messagetext
            self.timesent = timesent

    chatmessages_ = []
    for message in messages:
        chatmessages_.append(Chatmessage_(message.id,User.query.get(message.fromuserid).name,message.messagetext,
                                          message.timesent.strftime("%b %d %H:%M")))

    return render_template('chatdemo.html', user=current_user,chatrooms=chatrooms_,room=defaultroom,
                           messages=chatmessages_)


@socketio.on('client-connected')
def handle_user_connected(json,methods=['GET','POST']):
    # print(current_user.name + ' user connected')

    for socketroomname in socketroomnames:
        join_room(socketroomname)
        print('joining socketroom: ' + socketroomname)

    socketio.emit('display-new-user-joined',{'id':current_user.id,'name':current_user.name,'color':current_user.color,
                                             'socketroomnames':socketroomnames})


@socketio.on('chat-sent')
def handle_chat_sent(json,methods=['GET','POST']):
    print('someone sent chat')
    from models import Chatmessage, Chatroom
    # create a instance of the Chatroom class to add to database
    id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    timesent = datetime.utcnow()
    newchatmessage = Chatmessage(id=id,fromuserid=json.userid,roomid=json.roomid,messagetext=json.messagetext,
                                 timesent = timesent)
    db.session.add(newchatmessage)
    db.session.commit()
    # prepare a dict of a list of messages to emit to client, who has a socket that expects a list of messages
    username = json.username
    socketroomname = Chatroom.query.get(json.roomid).socketroomname
    messagesdict = {'messages':[]}
    messagesdict['messages'].append({'username':username,'roomid':json.roomid,'messagetext':json.messagetext})
    socketio.emit('display-new-messages',messagesdict)


