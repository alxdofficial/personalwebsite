from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.VARCHAR(10), primary_key=True, unique=True,index=True)
    name = db.Column(db.String(50),index=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.VARCHAR(128))
    type = db.Column(db.VARCHAR(20),index=True)
    test = db.Column(db.VARCHAR(20), index=True)
    __table_args__ = {'extend_existing': True}
    __table_name__ = 'User'
    def __repr__(self):
        return '<User {}>'.format(self.name)

# db.create_all()