from app import db,app
from flask import request, render_template, flash, redirect, jsonify
from app import socketio
import socket
import string
import sys


@app.route('/mldemo', methods = ['GET','POST'])
def mldemo():
    return render_template('mldemo.html')

@socketio.on('form-submit')
def handle_form(json, methods = ['GET', 'POST']):
    inputstring = json['inputasstring']
    print(inputstring)
    # add a random id to inputstring cuz my weka package wants one since it was designed for batch classifcation
    responseraw = send_data_to_weka("xabc," + inputstring)
    displayresponse = responseraw.replace("Server: ", "").replace("#end","")
    print(displayresponse)
    socketio.emit('show-ml-result',{'result':displayresponse})

def send_data_to_weka(inputstring):
    # Create a TCP/IP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 12069)
    # print >>sys.stderr, 'connecting to %s port %s' % server_address
    client.connect(server_address)
    try:
        # Send data
        print("trying to send: ")
        print(inputstring)
        client.send(bytes(inputstring+'\n','ascii'))
        print('sent')

        # Look for the response
        keepreading = True
        response = ""
        while (keepreading):
            response += client.recv(128).decode('ascii')
            if response.find('#end') != -1:
                keepreading = False
            print(response)
        return response
    finally:
        print("closing socket")
        client.close()