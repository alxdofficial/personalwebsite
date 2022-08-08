from app import db
from models import User
from flask import request, render_template, flash, redirect
from app import app

@app.route('/',methods = ['get'])
def hello_world():
    return render_template('index.html')


