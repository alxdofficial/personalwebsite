from app import db,app
from flask import request, render_template, flash, redirect, jsonify

@app.route('/iotdemo', methods = ['GET','POST'])
def iotdemo():
    from models import Iotdevice,Iotinterface
    return ''

@app.route('/report-to-server', methods = ['POST'])
def report_to_server():
    from models import Iotdevice,Iotinterface
    content = request.get_json()
    deviceid = content['deviceid']
    print(deviceid)


