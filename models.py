from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.VARCHAR(10), primary_key=True, unique=True, index=True)
    name = db.Column(db.VARCHAR(50), index=True)
    color = db.Column(db.VARCHAR(8))
    email = db.Column(db.VARCHAR(120), index=True, nullable=False)
    password_hash = db.Column(db.VARCHAR(128))
    __table_args__ = {'extend_existing': True}
    __table_name__ = 'User'

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Chatmessage(db.Model):
    id = db.Column(db.VARCHAR(10), primary_key=True, unique=True, index=True)
    fromuserid = db.Column(db.VARCHAR(10), index=True)
    roomid = db.Column(db.VARCHAR(10), index=True)
    messagetext = db.Column(db.VARCHAR(600))
    timesent = db.Column(db.DateTime(timezone=False), index=True)
    __table_args__ = {'extend_existing': True}
    __table_name__ = 'chatmessage'

    def __repr__(self):
        return '<message {}>'.format(str(self.timesent) + ' ' + self.messagetext)


class Roomassignment(db.Model):
    id = db.Column(db.VARCHAR(10), primary_key=True, unique=True, index=True)
    userid = db.Column(db.VARCHAR(10), index=True)
    roomid = db.Column(db.VARCHAR(10), index=True)
    __table_args__ = {'extend_existing': True}
    __table_name__ = 'roomassignment'

    def __repr__(self):
        return '<room assignment {}>'.format(self.id)


class Chatroom(db.Model):
    id = db.Column(db.VARCHAR(10), primary_key=True, unique=True, index=True)
    roomname = db.Column(db.VARCHAR(70))
    numusers = db.Column(db.INT)
    socketroomname = db.Column(db.VARCHAR(10), index=True, unique=True)
    mostrecentmessageid = db.Column(db.VARCHAR(10), index=True)
    __table_args__ = {'extend_existing': True}
    __table_name__ = 'chatroom'

    def __repr__(self):
        return '<chatroom {}>'.format(self.roomname)

class Iotdevice(db.Model):
    id = db.Column(db.VARCHAR(10), primary_key=True, unique=True, index=True)
    name = db.Column(db.VARCHAR(70))
    currentip = db.Column(db.VARCHAR(20))
    groupid = db.Column(db.VARCHAR(10), index=True)
    kind = db.Column(db.VARCHAR(35))
    __table_args__ = {'extend_existing': True}
    __table_name__ = 'iotdevice'

    def __repr__(self):
        return '<iotdevice {}>'.format(self.name)

class Iotinterface(db.Model):
    id = db.Column(db.VARCHAR(10), primary_key=True, unique=True, index=True)
    name = db.Column(db.VARCHAR(70))
    deviceid = db.Column(db.VARCHAR(10), index=True)
    type = db.Column(db.VARCHAR(35))
    __table_args__ = {'extend_existing': True}
    __table_name__ = 'iotinterface'

    def __repr__(self):
        return '<interface {}>'.format(self.name)

# db.create_all()

