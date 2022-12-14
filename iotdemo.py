from app import db,app
from flask import request, render_template, flash, redirect, jsonify
import random, string
from app import socketio
from flask_socketio import emit, join_room, leave_room
from datetime import datetime

@app.route('/iotdemo', methods = ['GET','POST'])
def iotdemo():
    from models import Iotdevice,Iotinterface
    return render_template("iotdemo.html")

@app.route('/iottest', methods = ['GET','POST'])
def test():
    print("connected")
    return "test"

@app.route('/report-to-server', methods = ['GET','POST'])
def report_to_server():
    from models import Iotdevice,Iotinterface
    json = request.json
    deviceid = json['deviceid']
    name = json['name']
    kind = json['kind']
    deviceip = json['currentip']
    print('connected')
    # check if this is the first time this device is reporting
    devicequery = Iotdevice.query.get(deviceid)
    if (devicequery is None):
        newdevice = Iotdevice(id=deviceid,name=name,kind=kind,currentip=deviceip)
        db.session.add(newdevice)
        db.session.commit()
        return "added new device to db: " + deviceid
    else:
        # existing device just rebooted
        devicequery.currentip = deviceip
        db.session.commit()
        return "updating existing devices ip: " + deviceid

@app.route('/iot-receive-num-data', methods = ['GET','POST'])
def receive_num_data():
    json = request.json
    name = json['name']
    value = json['value']
    deviceid = json['deviceid']
    timestamp = datetime.utcnow().strftime("%H:%M:%S")

    print(name + ": " + value + ", " + timestamp)

    if name == "temp celsius":
        socketio.emit('update-temp-chart', {'temp':value,'time':timestamp})
    elif name == "humidity":
        socketio.emit('update-hum-chart', {'hum':value,'time':timestamp})
    return "received data"