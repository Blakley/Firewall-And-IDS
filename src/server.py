
import os
from flask import Flask, request, render_template, jsonify, url_for, redirect, make_response

# make flask instance
app = Flask(__name__)  


'''
    =======================================
            Handle 'GET' routes 
    =======================================
'''

# project home page
@app.route('/')
def home():
    return render_template('home.html')


# project information page
@app.route('/information')
def learn():
    return render_template('information.html')


# project demonstration page
@app.route('/demonstration')
def learn():
    return render_template('demonstration.html')


# start
if __name__ == '__main__':
    # start web app/server
    app.run()