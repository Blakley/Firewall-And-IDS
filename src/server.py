# imports
import os
import time
import logging
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