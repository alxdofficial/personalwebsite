from app import db
from app import app
from flask import request, render_template, flash, redirect, jsonify
from app import socketio
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import json
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import random, string

# global var to add users to socketio rooms when they connect
socketroomnames = []


@app.route('/chatdemo/<userid>', methods=['GET', 'POST'])
def chat_demo(userid):
    from models import User, Chatroom, Roomassignment, Chatmessage
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

    # the chatrooms array is of model.Chatroom object, which doesnt contain the text of its most recent message, only the id.
    # here a new 'info' class and array is created, denoted by '_', to be passed into jinja templates for display
    class Chatroom_:
        def __init__(self, id, roomname, socketroomname, mostrecentmessagetext, mostrecentmessagetime):
            self.id = id
            self.roomname = roomname
            self.socketroomname = socketroomname
            self.mostrecentmessagetext = mostrecentmessagetext
            self.mostrecentmessagetime = mostrecentmessagetime

    chatrooms_ = []
    for chatroom in chatrooms:
        recentmessage = Chatmessage.query.get(chatroom.mostrecentmessageid)
        chatrooms_.append(Chatroom_(chatroom.id, chatroom.roomname, chatroom.socketroomname, recentmessage.messagetext,
                                    recentmessage.timesent.strftime("%b %d %H:%M")))
        socketroomnames.append(chatroom.socketroomname)

    # get room with most recent message
    chatrooms.sort(key=lambda roomvar: Chatmessage.query.get(roomvar.mostrecentmessageid).timesent)
    defaultroom = chatrooms[0]
    # get the latest chat senttime of default room, and 10 chats before it
    cutofftime = Chatmessage.query.get(defaultroom.mostrecentmessageid).timesent
    messages = query_messages_before_cutoff_time(defaultroom.id,cutofftime,querysize=4)

    # we need to update the cutoff time to the earliest chat send time that we loaded, so that when the user asks to
    # more chats, we dont load repeatedly
    newcutofftime = cutofftime
    if (len(messages) > 0):
        newcutofftime = messages[0].timesent

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
        chatmessages_.append(Chatmessage_(message.id, User.query.get(message.fromuserid).name, message.messagetext,
                                          message.timesent.strftime("%b %d %H:%M")))
    return render_template('chatdemo.html', user=current_user, chatrooms=chatrooms_, room=defaultroom,
                           messages=chatmessages_,
                           currentroomcutofftime=newcutofftime.strftime('%Y/%m/%d %H:%M:%S'))
    # the current room cut off times are used for when a user clicks to load ealier texts. it decides how far back of texts to load
    # when the user changes rooms, the value gets set to utcnow, and each time the user loads more texts, the time decrements


@socketio.on('client-connected')
def handle_user_connected(json, methods=['GET', 'POST']):
    # print(current_user.name + ' user connected')
    for socketroomname in socketroomnames:
        join_room(socketroomname)
        print('joining socketroom: ' + socketroomname)
    print("clinet signed in: " + request.sid)

@socketio.on('chat-sent')
def handle_chat_sent(json, methods=['GET', 'POST']):
    from models import Chatmessage, Chatroom
    if check_user_belong_in_chatroom(json['roomid']):
        # create a instance of the Chatroom class to add to database
        id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        timesent = datetime.utcnow()
        newchatmessage = Chatmessage(id=id, fromuserid=json['userid'], roomid=json['roomid'],
                                     messagetext=json['messagetext'],
                                     timesent=timesent)
        db.session.add(newchatmessage)
        Chatroom.query.get(json['roomid']).mostrecentmessageid = id
        db.session.commit()
        # prepare a dict of a list of messages to emit to client, who has a socket that expects a list of messages
        messages = [newchatmessage]
        socketroomname = Chatroom.query.get(json['roomid']).socketroomname
        messagesdict = generate_message_dictionary(messages, False)
        # only emit to relevant users in room
        socketio.emit('display-new-messages', messagesdict, room=socketroomname)
    else:
        print('send chat not authorized')
        return 'send chat not authorized'

@socketio.on('change-room')
def handle_change_room(json, methods=['GET', 'POST']):
    # print('user wants to change rooms')
    from models import Chatmessage, Chatroom, User, Roomassignment
    if check_user_belong_in_chatroom(json['newroomid']):
        newroom = Chatroom.query.get(json['newroomid'])

        # get the last message send time in this room, find 10 earlier chats including it.
        cutofftime = Chatmessage.query.get(newroom.mostrecentmessageid).timesent
        messages = query_messages_before_cutoff_time(newroom.id, cutofftime,querysize=4)
        # we need to update the cutoff time to the earliest chat send time that we loaded, so that when the user asks to
        # more chats, we dont load repeatedly. if no messages come up, it is likely that no correct user is logged in,
        # because all rooms have at least one message, and we are querying all messages
        newcutofftime = cutofftime
        if (len(messages) > 0):
            newcutofftime = messages[0].timesent
        else:
            return 'no messages found during query, you may not have been added to this chat'

        # prepare a dict of a list of messages to emit to client, who has a socket that expects a list of messages
        messagesdict = generate_message_dictionary(messages, False)
        # only emit to user who requested to change rooms, which is named by their session id
        socketio.emit('clear-current-room-display', room=request.sid)
        socketio.emit('display-new-messages', messagesdict, room=request.sid)
        socketio.emit('change-room-cutoff-time', {'cutofftime': newcutofftime.strftime("%Y/%m/%d %H:%M:%S")},
                      room=request.sid)
        # print("telling user to change room: " + request.sid)
    else:
        print('change room not authorized')
        return 'change room not authorized'


@socketio.on('load-earlier-chats')
def handle_load_earlier_chats(json, methods=['GET', 'POST']):
    from models import Chatmessage, Chatroom, User
    currentcutofftime = datetime.strptime(json['currentcutofftime'], "%Y/%m/%d %H:%M:%S")
    # query earlier messages
    messages = query_messages_before_cutoff_time(json['roomid'], currentcutofftime,inclusive=False,
                                                 querysize=3)
    # we need to update the cutoff time to the earliest chat send time that we loaded, so that when the user asks to
    # more chats, we dont load repeatedly
    newcutofftime = currentcutofftime
    if (len(messages) > 0):
        newcutofftime = messages[0].timesent
    # notice that it is allowed for messages list to be empty because we are querying earlier messages again and again

    # now we generate messages dictionary and send it only to current client.
    # notice the list of messages is reversed again because javascript prepend loop essentially reverses the list
    # when displaying
    messages.reverse()
    messagesdict = generate_message_dictionary(messages, True)
    socketio.emit('display-new-messages', messagesdict, room=request.sid)
    socketio.emit('change-room-cutoff-time', {'cutofftime': newcutofftime.strftime("%Y/%m/%d %H:%M:%S")},
                  room=request.sid)


# returns a list of messages queryd by roomid and gets 1 messages on and before cutoff time.
# - inclusive means wether to include entry timed at cutofftime, usually true when we are loading chats into a chatroom
# for the first time, but it needs to be false when loading earlier chats so that there are no duplicates

def query_messages_before_cutoff_time(roomid, cutofftime,inclusive=True,querysize = 10):
    from models import Chatmessage, Chatroom, User, Roomassignment
    messages = []
    if inclusive:
        messages = Chatmessage.query.filter(Chatmessage.roomid == roomid).filter(
            Chatmessage.timesent <= cutofftime).order_by(Chatmessage.timesent.desc()).limit(
            querysize).all()
    else:
        messages = Chatmessage.query.filter(Chatmessage.roomid == roomid).filter(
            Chatmessage.timesent < cutofftime).order_by(Chatmessage.timesent.desc()).limit(
            querysize).all()
    messages.reverse()
    return messages


# returns dictionary of messages in the form of a list of messages, and a indicator of whether this is loading earlier
# messages, which determines if frontend prepends or appends messages in display
def generate_message_dictionary(messages, loadingearlier):
    from models import User, Chatroom, Chatmessage
    messagesdict = {'messages': [], 'loadingearlier': loadingearlier}
    for message in messages:
        username = User.query.get(message.fromuserid).name
        messagesdict['messages'].append(
            {'username': username, 'roomid': message.roomid, 'messagetext': message.messagetext,
             'timesent': message.timesent.strftime('%b %d %H:%M')})
    return messagesdict

# returns if a record can be found in db's roomassignment table containing both current user and room
def check_user_belong_in_chatroom(roomid):
    from models import Chatroom, User, Roomassignment
    return Roomassignment.query.filter(Roomassignment.userid == current_user.id
                                       ).filter(Roomassignment.roomid == roomid).first() is not None
