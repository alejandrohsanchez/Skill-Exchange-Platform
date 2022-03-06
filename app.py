from logging import exception
from flask import Flask, redirect, url_for, request, render_template, send_file, session
from flask_session import Session
import sqlite3
from sqlite3 import Error

from flask.templating import render_template_string

import sys
app = Flask(__name__)

@app.route('/login-verify', methods = ['POST', 'GET'])
def getCredentials():
    """
    To add credentials, use the following (testing only)
    INSERT INTO users (u_username, u_pass)
    VALUES ('ajsin', 'balls007'); 
    """
    if (request.method == 'POST'):
        method = request.form['submit']
        if (method == 'login'):
            username = request.form['username']
            password = request.form['password']
            
            database = r"data.sqlite"
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute(f"""
                     SELECT
                        u_username,
                        u_pass
                     FROM
                        users
                     WHERE
                        u_username = '{username}' AND
                        u_pass = '{password}';
                     """)
            data = cur.fetchall()
            if (data):
                if (username == data[0][0] and password == data[0][1]):
                    session[f'{nameID}'] = username
                    session[f'{passID}'] = password
                    return render_template('forumMain.html')
            else:
                return render_template('login.html')

@app.route('/', methods = ['POST', 'GET'])
def main():
    return render_template('login.html')

if __name__ == '__main__':
   app.run(debug = True)