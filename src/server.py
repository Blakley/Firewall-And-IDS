# imports
import os
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, url_for, redirect

# make flask instance
app = Flask(__name__)  

# {client_address : requests_within_last_minute}
client_activity = {}

# blocked ip addresses
blocked_clients = []

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
            Handle HTTP routes 
    =======================================
'''

# Handle blocking addresses
@app.before_request
def restrict_ips():
    client_ip = request.remote_addr
    if request.endpoint != 'error' and client_ip in blocked_clients:
        return redirect(url_for('error'))


# Handles logging client traffic/messages
def log_message(msg):
    _newlog = logging.getLogger('logs')
    _newlog.info(
        f"{msg}"
    )


# Home page
@app.route('/')
def home():
    # track client requests
    client = request.remote_addr
    result = rate_limit(client)

    # log access
    msg = f'Client: {client}, just accessed the home page'
    log_message(msg) 

    # client exceeded request threshold
    if result:
        msg = f'Client: {client} has been blocked. Sent {client_activity[client]} requests in within the last minute'
        log_message(msg)
        return render_template('error.html')
    
    # check if client is suspicious
    if client_activity[client] >= 100:
        msg = f'[Suspicious activity deteacted] : Client {client}, has made {client_activity[client]} requests within the last minute'
        log_message(msg)

    return render_template('home.html')


# Error page
@app.route('/error')
def error():
    # log access
    client = request.remote_addr
    msg = f'Client: {client}, just accessed the error page'
    log_message(msg) 
    
    return render_template('error.html')


'''
    =======================================
            Server Firewall and IDS
    =======================================
'''

# handle rate limiting
def rate_limit(client):
    logs = 'utils/logfile'

    # allowed requests per minute
    rate_limit_window = 60

    # calculate the time threshold (1 minute ago)
    window_1 = datetime.now() - timedelta(seconds=rate_limit_window)

    # read logfile and count website requests from the same client address within the time window
    _requests = 0
    with open(logs, 'r') as log_file:
        for line in log_file:
            if "Client: {}".format(client) in line:
                timestamp_str, client_info = line.split(' - ')
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                if timestamp > window_1:
                    _requests += 1

    # update client_activity dictionary
    if client not in client_activity:
        client_activity[client] = 1
    else:
        client_activity[client] += _requests

    # check if client exceeded request threshold
    if client_activity[client] >= 500:
        blocked_clients.append(client)
        return True
    
    return False


'''
    =======================================
              Terminal Back-end
    =======================================
'''

# returns the output of the specified command
def terminal_output(command):
    '''
        allow for input commands: [clear, current: policies, 
        firewall details, ids details, alerts (block ips, suspicious activity, etc)]
    '''

    # handle various commands
    result = {
        'message' : ''
    }

    '''
        iterate logs, show all clients in the last minute that is suspicious
        iterate logs, show all clients that have been blocked
    '''

    # will return information from logged server content
    match command:
        case "help":
            result['message'] = "showing help"
        case "suspicious":
            pass
        case "blocked":
            pass
        case _:
            result['message'] = "random message"
    
    return jsonify(result)


# handle terminal command submissions
@app.route('/terminal_submit', methods=['POST'])
def terminal():
    # get terminal input
    command = request.form['terminal_input']
    return terminal_output(command)


'''
    =======================================
                   Start
    =======================================
'''

if __name__ == '__main__':
    # setup packet/client logging
    _logger()

    # start web app/server
    app.run(port= 9000)