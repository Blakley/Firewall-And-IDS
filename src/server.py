# imports
import os
import logging
from flask import Flask, request, render_template, jsonify, url_for, redirect, make_response

# make flask instance
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
            Handle 'GET' routes 
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
    # start web app/server
    logging()
    app.run()

