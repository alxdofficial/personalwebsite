from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)
app.config['SECRET_KEY'] = '7671'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://alexremote:Alex020109u!m@192.168.1.96:/personalwebsitedata' # use for testing
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Alex020109u!m@localhost:/personalwebsitedata'  # use for deploy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import basic_routes


if __name__ == '__main__':
    app.run()
