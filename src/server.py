# imports
import os
import time
import socket
import logging
import paramiko
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
def _logger():
    # logs to terminal
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.addFilter(_filter)
    root_logger.addHandler(console_handler)

    # logs to a file
    _logs = logging.getLogger('logs')
    logs_handler = logging.FileHandler('utils/logfile') 
    logs_handler.setLevel(logging.INFO)
    login_formatter = logging.Formatter('%(asctime)s - %(message)s')
    logs_handler.setFormatter(login_formatter)
    _logs.addHandler(logs_handler)


# filter out login-logs from terminal logger
def _filter(record):
    string_to_exclude = "/terminal" 
    return string_to_exclude not in record.getMessage()


'''
    =======================================
          Configure additional ports
    =======================================
'''

# todo, setup ftp, ssh, smtp port
# remove shh and udp port, monitor all through the flask tcp port

# Handle UDP connections to port 9001
def udp_server():
    global new_logs

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', 9001))  
    
    print("UDP server listening on port 9001...")
    
    while True:
        data, address = udp_socket.recvfrom(1024) 
        print(f"Received UDP packet from {address}: {data.decode('utf-8')}")

        # send test log to file
        new_logs = True

        _newlog = logging.getLogger('logs')
        _newlog.info(
            f"Client: {address}, just message UDP port 9001"
        )
        

    # view server's open udp ports: sudo nmap -sU localhost
    # send udp packet method 1: echo "Your packet data" | nc -u localhost 9001
    # send udp packet method 2: 
    '''
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(MESSAGE, (HOST, PORT))
    '''


# Function to handle incoming SSH connections
def handle_ssh(client, addr):
    logging.info(f"SSH connection established from {addr}")
    # Add your SSH handling logic here
    client.close()


# Start SSH server function
def start_ssh_server():
    # Create a new SSH server instance
    ssh_server = paramiko.Transport(('0.0.0.0', 2222)) 
    ssh_server.add_server_key(paramiko.RSAKey.generate(2048))
    
    # Start accepting SSH connections
    try:
        ssh_server.start_server(server=handle_ssh)
        print("SSH server started successfully")
    except Exception as e:
        logging.error(f"Error starting SSH server: {e}")
        return

    # Keep the server running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping SSH server...")
        ssh_server.close()


    # scan for ssh ports: sudo nmap -p 2222 localhost


'''
    =======================================
            Handle HTTP 'GET' routes 
    =======================================
'''

# todo:
# add random routes with a blank page "saying random route {index}"
# to test packet sending

# project home page
@app.route('/')
def home():
    new_logs = True

    # send test log to file
    _newlog = logging.getLogger('logs')
    _newlog.info(
        f"Client: {request.remote_addr}, just accessed the home page."
    )

    return render_template('home.html')


# 403 error page
@app.route('/error')
def error():
    return render_template('error.html')



'''
    =======================================
            Server/Client functions
    =======================================
'''

# handle sending messages to client's terminal
new_logs = False

@app.route('/terminal')
def log_to_terminal():
    global new_logs 

    # todo:
    # output the last line inside logfile

    if new_logs:
        new_logs = False
        return jsonify({'message' : 'This is a test.'})    
    else:
        return jsonify({'message' : ''})


'''
    =======================================
                   Start
    =======================================
'''

if __name__ == '__main__':
    # setup packet/client logging
    _logger()

    # udp server thread
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.start()

    # ssh server thread
    ssh_thread = threading.Thread(target=start_ssh_server)
    ssh_thread.start()

    # start web app/server
    app.run(port= 9000)