from flask import Flask
from flask import request, render_template, flash, redirect
from flask_socketio import SocketIO
from flask_login import LoginManager ,login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)
app.config['SECRET_KEY'] = '7671'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://alexremote:Alex020109u!m@192.168.1.96/personalwebsitedata' # use for velopment
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Alex020109u!m@localhost/personalwebsitedata'  # use for deploy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app,cors_allowed_origins='*')

@app.route('/',methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/dbinit')
def dbinit():
    from models import User,Chatroom,Chatmessage,Roomassignment,\
        Iotdevice,Iotinterface,Iotnumericaldata
    testdb = Roomassignment()
    return "db init ran"

from chatdemo import *
from iotdemo import *

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(user_id)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)
