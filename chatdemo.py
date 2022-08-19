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
    user = User.query.get(userid)
    login_user(user)

    # find all rooms user is assigned to
    roomassignments = Roomassignment.query.filter(Roomassignment.userid == current_user.id)
    chatrooms = []
    for roomassignment in roomassignments:
        chatrooms.append(Chatroom.query.get(roomassignment.roomid))

    # the global var socketroomnames is for handle_user_connected() to have access to the socketrooms, so it
    # can call join_room() for each room of the user. when the page is reloaded to change users, this list needs to be wiped.
    socketroomnames.clear()

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
    # taking the last 10 sent between now and 4 hours ago, which the sql retrieves in latest to earlist order, but reversed
    # in order to display in chronological order
    messages = Chatmessage.query.filter(Chatmessage.roomid == defaultroom.id).filter(Chatmessage.timesent >= datetime.utcnow() - timedelta(hours=4)).order_by(Chatmessage.timesent.desc()).limit(10).all()
    messages.reverse()

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
                           messages=chatmessages_,
                           currentroomcutofftime=messages[0].timesent.strftime("%Y/%m/%d %H:%M:%S"))
    #the current room cut off times are used for when a user clicks to load ealier texts. it decides how far back of texts to load
    #when the user changes rooms, the value gets set to utcnow, and each time the user loads more texts, the time decrements

@socketio.on('client-connected')
def handle_user_connected(json,methods=['GET','POST']):
    # print(current_user.name + ' user connected')
    for socketroomname in socketroomnames:
        join_room(socketroomname)
        print('joining socketroom: ' + socketroomname)
    print("clinet signed in: " + request.sid)
    socketio.emit('display-new-user-joined',{'id':current_user.id,'name':current_user.name,'color':current_user.color,
                                             'socketroomnames':socketroomnames})


@socketio.on('chat-sent')
def handle_chat_sent(json,methods=['GET','POST']):
    print('someone sent chat')
    from models import Chatmessage, Chatroom
    # create a instance of the Chatroom class to add to database
    id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    timesent = datetime.utcnow()
    timesenttext = timesent.strftime("%b %d %H:%M")
    newchatmessage = Chatmessage(id=id,fromuserid=json['userid'],roomid=json['roomid'],messagetext=json['messagetext'],
                                 timesent = timesent)
    db.session.add(newchatmessage)
    Chatroom.query.get(json['roomid']).mostrecentmessageid = id
    db.session.commit()
    # prepare a dict of a list of messages to emit to client, who has a socket that expects a list of messages
    username = json['username']
    socketroomname = Chatroom.query.get(json['roomid']).socketroomname
    messagesdict = {'messages':[]}
    messagesdict['messages'].append({'username':username,'roomid':json['roomid'],'messagetext':json['messagetext'],'timesent':timesenttext})
    #only emit to relevant users in room
    socketio.emit('display-new-messages',messagesdict,room=socketroomname)

@socketio.on('change-room')
def handle_change_room(json,methods=['GET','POST']):
    print('user wants to change rooms')
    from models import Chatmessage, Chatroom,User,Roomassignment
    newroom = Chatroom.query.get(json['newroomid'])
    if Roomassignment.query.filter(Roomassignment.userid == current_user.id).filter(Roomassignment.roomid == newroom.id).first() is not None:
        #if users is authorized to be in this new room

        # taking the last 10 sent between now and 4 hours ago, which the sql retrieves in latest to earlist order, but reversed
        # in order to display in chronological order
        messages = Chatmessage.query.filter(Chatmessage.roomid == newroom.id).filter(
            Chatmessage.timesent >= datetime.utcnow() - timedelta(hours=4)).order_by(Chatmessage.timesent.desc()).limit(
            10).all()
        messages.reverse()
        # prepare a dict of a list of messages to emit to client, who has a socket that expects a list of messages
        messagesdict = {'messages': []}
        for message in messages:
            username = User.query.get(message.fromuserid).name

            messagesdict['messages'].append(
                {'username': username, 'roomid': message.roomid, 'messagetext': message.messagetext,
                 'timesent': message.timesent.strftime('%b %d %H:%M')})
        # only emit to user who requested to change rooms, which is named by their session id
        socketio.emit('clear-current-room-display',room=request.sid)
        socketio.emit('display-new-messages', messagesdict, room=request.sid)
        socketio.emit('change-room-cutoff-time', {'cutofftime':datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")})
        print("telling user to change room: " + request.sid)
    else:
        #user shoudnt be here
        return "you haven't been added to this chat group yet"

