# imports
import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, url_for, redirect

'''
    =======================================
                  Globals
    =======================================
'''

# make flask instance
app = Flask(__name__)  

# {client_address : requests_within_last_minute}
client_activity = {}

# blocked ip addresses
blocked_clients = []

# load firewall configuration
firewall_config = {}
with open('static/json/firewall_config.json') as f:
    firewall_config = json.load(f)

# load ids configuration
ids_config = {}
with open('static/json/ids_config.json') as f:
    ids_config = json.load(f)

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
    rate_limit(client, "home")

    # log access
    msg = f'Client: {client}, just accessed the home page'
    log_message(msg) 

    return render_template('home.html')


# Page A
@app.route('/a')
def route_a():
    # track client requests
    client = request.remote_addr
    rate_limit(client, "a")

    # log access
    msg = f'Client: {client}, just accessed page A'
    log_message(msg) 

    return render_template('route_a.html')


# Page B
@app.route('/b')
def route_b():
    # track client requests
    client = request.remote_addr
    rate_limit(client, "b")

    # log access
    msg = f'Client: {client}, just accessed page B'
    log_message(msg) 

    return render_template('route_b.html')


# Page C
@app.route('/c')
def route_c():
    # track client requests
    client = request.remote_addr
    rate_limit(client, "c")

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
def rate_limit(client, page):
    # skip host client
    if client == "127.0.0.1":
        return

    logs = 'utils/logfile'

    # allowed requests per minute
    rate_limit_window = 60

    # calculate the time threshold (1 minute ago)
    window = datetime.now() - timedelta(seconds=rate_limit_window)

    # check if a minute has elapsed since the last update for the client
    if client in client_activity:
        last_update_time = client_activity[client]["timestamp"]
        if datetime.now() - last_update_time >= timedelta(seconds=rate_limit_window):
            # reset request count and pages array for the client
            client_activity[client] = {"requests": 0, "timestamp": datetime.now(), "pages": []}

    # read logfile and count website requests from the same client address within the time window
    _requests = 0
    with open(logs, 'r') as log_file:
        for line in log_file:
             if f"Client: {client}" in line:
                timestamp_str, client_info = line.split(' - ')
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                if timestamp > window:
                    _requests += 1

    # update client_activity dictionary
    if client not in client_activity:
        client_activity[client] = {"requests": 1, "timestamp": datetime.now(), "pages": [page]}
    else:
        client_activity[client]["requests"] += 1
        client_activity[client]["timestamp"] = datetime.now()
        client_activity[client]["pages"].append(page)

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
    # initialize the result dictionary
    result = {
        'message' : ''
    }

    # Get information from logged server content
    match command:
        # shows the help menu for the terminal
        case "help":
            help_menu = '''
            =================================================================================
            __________________________𝗙𝗜𝗥𝗘𝗪𝗔𝗟𝗟 & 𝗜𝗗𝗦 𝗠𝗘𝗡𝗨____________________________
            $ >
            $ : [help]       Displays terminal command information
            $ : [clear]      Clears the terminal screen
            $ : [traffic]    Shows server traffic statistics
            
            $ : [alerts]            Shows statistics for each alert type
            $ : [alerts suspicious] Show clients with suspicious activity
            $ : [alerts blacklist]  Show clients that have been blacklisted

            $ : [move all list_a list_b]  Moves all clients from one list to another
            $ : [move N list_a list_b]    Moves the first N clients from one list to another

            $ : [remove all suspicious] Removes all clients from the given alert list
            $ : [remove all blacklist]  Removes all clients from the given alert list
            $ : [remove N list_name]    Removes the first N clients from the given list
        
            $ : [firewall]   Shows the current firewall configuration
            $ : [ids]        Shows the current IDS configuration
            =================================================================================
            '''
            result['message'] = help_menu
        
        # shows statistics for server traffic
        case "traffic":
            # calculate total page statistics across all clients
            page_statistics = {}
            for data in client_activity.values():
                for page, count in Counter(data.get("pages", [])).items():
                    page_statistics[page] = page_statistics.get(page, 0) + count
            
            # construct the traffic message
            traffic = "\n============================================\n"
            traffic += "_________________Traffic____________________\n"
            traffic += "$ : Requests made within the last minute\n"
            traffic += "$ >\n"
            
            for page, total_requests in page_statistics.items():
                traffic += f"{total_requests} requests made to {page} route\n"
            
            traffic += "============================================\n"
            result['message'] = traffic

        # shows statistics for alert types
        case "alerts":
            '''
                show overall statistics for suspicious and blacklist alerts
                1. total number of suspicious alerts
                2. total number of blacklist alerts
            '''
            msg_body = ""
            result['message'] = msg_body

        # shows the clients that've been marked as suspicious
        case "alerts suspicious":
            msg_body = ""
            for client, data in client_activity.items():
                if data["requests"] >= 100 and client not in blocked_clients:
                    msg = f'[Suspicion Alert]: Client {client} is showcasing suspicious behavior due to having sent {data["requests"]} requests within the last minute\n'
                    msg_body += msg

            if msg_body == "":
                msg_body = f'No suspicious activities to report'

            result['message'] = msg_body

        # shows the clients in blocked_clients
        case "alerts blacklist":
            msg_body = ""
            for _ip in blocked_clients:
                msg = f'[Blacklist Alert]: Client {_ip} has been blacklisted due to sending more than 500 requests within a minute\n'    
                msg_body += msg

            if msg_body == "":
                msg_body = f'No blocked clients to report'

            result['message'] = msg_body

        # moves all clients from suspicious to blacklist
        case "move all suspicious blacklist":
            msg_body = ""
            result['message'] = msg_body

        # moves all clients from blacklist to suspicious
        case "move all blacklist suspicious":
            msg_body = ""
            result['message'] = msg_body

        # moves the first N clients from one list to another list
        # case

        # resets all clients, 'requests' value from client_activity, clear logfile
        case "remove all suspicious":
            msg_body = ""
            result['message'] = msg_body

        # removes all clients from blocked_clients 
        case "remove all blacklist":
            msg_body = ""
            result['message'] = msg_body

        # removes the first N clients from the given list
        # case 

        # show the Firewall configuration
        case "firewall":
            # use f-string to insert the dict key, values from firewall_config variable
            _config = '''
            \n============================================
            __________𝗙𝗶𝗿𝗲𝘄𝗮𝗹𝗹 𝗖𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗮𝘁𝗶𝗼𝗻_________
            $ >
            $ >
            ============================================
            '''
            result['message'] = _config

        # show the IDS configuration
        case "ids":
            # use f-string to insert the dict key, values from ids_config variable
            _config = '''
            \n============================================
            ____________𝗜𝗗𝗦  𝗖𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗮𝘁𝗶𝗼𝗻___________
            $ >
            $ >
            ============================================
            '''
            result['message'] = _config

        # default case: handle invalid commands
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