from flask import Flask
from flask import request, render_template, flash, redirect

from flask_socketio import SocketIO

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)
app.config['SECRET_KEY'] = '7671'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://alexremote:Alex020109u!m@192.168.1.96/personalwebsitedata' # use for velopment
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Alex020109u!m@localhost/personalwebsitedata'  # use for deploy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

socketio = SocketIO(app,cors_allowed_origins='*')

@app.route('/',methods = ['GET'])
def index():
    return render_template('index.html')


from other_routes import *

if __name__ == '__main__':
    socketio.run(app, debug=True)
