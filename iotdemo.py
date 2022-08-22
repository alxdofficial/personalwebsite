from app import db,app
from flask import request, render_template, flash, redirect, jsonify

@app.route('/iotdemo', methods = ['GET','POST'])
def iotdemo():
    from models import Iotdevice,Iotinterface
    # test
    return "iotdemo"

@app.route('/report-to-server', methods = ['GET','POST'])
def report_to_server():
    from models import Iotdevice,Iotinterface
    content = request.get_json()
    print(content)
    deviceid = content['deviceid']
    print(deviceid)


