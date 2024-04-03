# imports
import os
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, url_for, redirect

# make flask instance
app = Flask(__name__)  

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


# Handle logging client traffic
def accessed(page):
    # log client access
    _newlog = logging.getLogger('logs')
    _newlog.info(
        f"Client: {request.remote_addr}, just accessed the {page} page"
    )


# Home page
@app.route('/')
def home():
    accessed("home") # log request
    return render_template('home.html')


# Error page
@app.route('/error')
def error():
    accessed("error") # log request
    return render_template('error.html')


'''
    =======================================
            Server Firewall and IDS
    =======================================
'''

# handle rate limiting
def rate_limit():
    logs = 'utils/logfile'

    # allowed requests per minute
    rate_limit_window = 60

    # allowed requests per 3 minutes
    rate_limit_window_b = 180

    # calculate the time threshold (1 minutes ago)
    window_1 = datetime.now() - timedelta(seconds=rate_limit_window)
    # calculate the time threshold (3 minutes ago)
    window_3 = datetime.now() - timedelta(seconds=rate_limit_window_b)

    # read logfile and count website requests from the same client address within the time window
    _requests = 0
    with open(logs, 'r') as log_file:
        for line in log_file:
            timestamp_str = line.split(' - ')[0]
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            if timestamp > window_1:
                _requests += 1


    # check if site page requests exceeds threshold
    threshold = 10
    if _requests >= threshold:
        pass
    
    '''
        log that the client has exceeded their threshold, (block them for x amount of time)
        if the client exceeded the second threshold, block them (log it)
        [send to the front-end terminal]:
            1. suspecious activty: clients that are on hold
            2. clients blocked
            3. amount of traffic within last x minutes
            4.

    '''


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

    # will return information from logged server content
    match command:
        case "help":
            result['message'] = "showing help"
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