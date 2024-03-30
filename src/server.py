# imports
import os
import socket
import logging
import threading
from flask import Flask, request, render_template, jsonify, url_for, redirect, make_response


# make flask instance
# runs an HTTP server which listens on TCP/IP sockets.
app = Flask(__name__)  


# 
locked_clients = []
blocked_clients = []
locked_threshold = 5

'''
    =======================================
            Configure server logging
    =======================================
'''

# setups up terminal and file logging
def logging():
    pass


'''
    =======================================
          Configure additional ports
    =======================================
'''

# Handle UDP connections to port 9001
def udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', 9001))  
    
    print("UDP server listening on port 9001...")
    
    while True:
        data, address = udp_socket.recvfrom(1024) 
        print(f"Received UDP packet from {address}: {data.decode('utf-8')}")

    # view server's open udp ports: sudo nmap -sU localhost
    # send udp packet method 1: echo "Your packet data" | nc -u localhost 9001
    # send udp packet method 2: 
    '''
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(MESSAGE, (HOST, PORT))
    '''


'''
    =======================================
            Handle HTTP 'GET' routes 
    =======================================
'''

# project home page
@app.route('/')
def home():
    return render_template('home.html')


# 403 error page
@app.route('/error')
def error():
    return render_template('error.html')


# start
if __name__ == '__main__':
    # setup packet/client logging
    logging()

    # udp server thread
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.start()

    # start web app/server
    app.run(port= 9000)

