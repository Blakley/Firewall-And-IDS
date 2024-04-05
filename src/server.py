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
    root_logger.addHandler(console_handler)

    # logs to a file
    _logs = logging.getLogger('logs')
    logs_handler = logging.FileHandler('utils/logfile') 
    logs_handler.setLevel(logging.INFO)
    login_formatter = logging.Formatter('%(asctime)s - %(message)s')
    logs_handler.setFormatter(login_formatter)
    _logs.addHandler(logs_handler)


# Handles logging client traffic/messages
def log_message(msg):
    _newlog = logging.getLogger('logs')
    _newlog.info(
        f"{msg}"
    )


'''
    =======================================
            Handle HTTP routes 
    =======================================
'''

# Home page
@app.route('/')
def home():
    # track client requests
    client = request.remote_addr
    rate_limit(client)

    # log access
    msg = f'Client: {client}, just accessed the home page'
    log_message(msg) 

    return render_template('home.html')


# Page A
@app.route('/a')
def route_a():
    # track client requests
    client = request.remote_addr
    rate_limit(client)

    # log access
    msg = f'Client: {client}, just accessed page A'
    log_message(msg) 

    return render_template('route_a.html')


# Page B
@app.route('/b')
def route_b():
    # track client requests
    client = request.remote_addr
    rate_limit(client)

    # log access
    msg = f'Client: {client}, just accessed page B'
    log_message(msg) 

    return render_template('route_b.html')


# Page C
@app.route('/c')
def route_c():
    # track client requests
    client = request.remote_addr
    rate_limit(client)

    # log access
    msg = f'Client: {client}, just accessed page C'
    log_message(msg) 

    return render_template('route_c.html')


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

# handle blocking addresses
@app.before_request
def restrict_ips():
    client_ip = request.remote_addr
    if request.endpoint != 'error' and client_ip in blocked_clients:
        return redirect(url_for('error'))


# handle rate limiting
def rate_limit(client):
    logs = 'utils/logfile'

    # allowed requests per minute
    rate_limit_window = 60

    # calculate the time threshold (1 minute ago)
    window = datetime.now() - timedelta(seconds=rate_limit_window)

    # check if a minute has elapsed since the last update for the client
    if client in client_activity:
        last_update_time = client_activity[client]["timestamp"]
        if datetime.now() - last_update_time >= timedelta(seconds=rate_limit_window):
            # reset request count for the client
            client_activity[client]["requests"] = 0

    # read logfile and count website requests from the same client address within the time window
    _requests = 0
    with open(logs, 'r') as log_file:
        for line in log_file:
            if "Client: {}".format(client) in line:
                timestamp_str, client_info = line.split(' - ')
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                if timestamp > window:
                    _requests += 1

    # update client_activity dictionary
    if client not in client_activity:
        client_activity[client] = {"requests": 1, "timestamp": datetime.now()}
    else:
        client_activity[client]["requests"] += 1
        client_activity[client]["timestamp"] = datetime.now()

    # check if client exceeded request threshold
    if client_activity[client]["requests"] >= 500:
        if client not in blocked_clients:
            blocked_clients.append(client)
    
   
'''
    =======================================
              Terminal Back-end
    =======================================
'''

# returns the output of the specified command
def terminal_output(command):
    # Initialize the result dictionary
    result = {
        'message' : ''
    }

    # Get information from logged server content
    match command:
        case "help":
            # handle various commands
            help_menu = '''
            ==========================================================================
            ______________________________𝗛𝗘𝗟𝗣 𝗠𝗘𝗡𝗨_______________________________
            $ >
            $ : [help]       Displays terminal command information
            $ : [clear]      Clears the terminal screen
            $ : [traffic]    Shows Server traffic statistics
            $ : [suspicious] Show clients with suspicious activity
            $ : [blacklist]  Show clients that have been blacklisted
            $ : [firewall]   Shows the current firewall configuration
            $ : [ids]        Shows the current IDS configuration
            ==========================================================================
            '''
            result['message'] = help_menu
        
        case "traffic":
            # use f-string to insert traffic stats for each route
            # x amount of requests made to route y in the last minute

            traffic = '''
            ============================================
            _________________Traffic____________________
            $ >
            $ >
            $ >
            $ >
            ============================================
            '''
            result['message'] = traffic

        case "suspicious":
            msg_body = ""
            for client, data in client_activity.items():
                if data["requests"] >= 100 and client not in blocked_clients:
                    msg = f'[Suspicion Alert]: Client {client} is showcasing suspicious behavior due to having sent {data["requests"]} requests within the last minute\n'
                    msg_body += msg

            if msg_body == "":
                msg_body = f'No suspicious activities to report'

            result['message'] = msg_body
        
        case "blocked":
            msg_body = ""
            for _ip in blocked_clients:
                msg = f'[Blacklist Alert]: Client {_ip} has been blacklisted due to sending more than 500 requests within a minute\n'    
                msg_body += msg

            if msg_body == "":
                msg_body = f'No blocked clients to report'

            result['message'] = msg_body
        
        case "firewall":
            # use f-string to insert current firewall config values
            firewall_config = '''
            ============================================
            __________𝗙𝗶𝗿𝗲𝘄𝗮𝗹𝗹 𝗖𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗮𝘁𝗶𝗼𝗻_________
            $ >
            $ >
            ============================================
            '''
            result['message'] = firewall_config

        case "ids":
            # use f-string to insert current ids config values
            ids_config = '''
            ============================================
            ____________𝗜𝗗𝗦  𝗖𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗮𝘁𝗶𝗼𝗻___________
            $ >
            $ >
            ============================================
            '''
            result['message'] = ids_config

        case _:
            result['message'] = "invalid command entered"

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