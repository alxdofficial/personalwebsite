from app import db
from models import User
from flask import request, render_template, flash, redirect
from app import app

@app.route('/',methods = ['GET'])
def index():
    return render_template('index.html')


