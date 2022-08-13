from app import db
from app import app
from flask import request, render_template, flash, redirect



@app.route('/2',methods = ['GET'])
def fn2():
    return "2"


