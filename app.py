from logging import exception
from flask import Flask, redirect, url_for, request, render_template, send_file, session
from flask_session import Session
import sqlite3
from sqlite3 import Error
from datetime import date
from flask.templating import render_template_string
import random

import sys
app = Flask(__name__)
app.secret_key = 'privateUser'

@app.route('/handleNewPost', methods = ['POST', 'GET'])
def handleNewPost():
    todaysDate = date.today()
    if (request.method == 'POST'):
        method = request.form['post']
        if (method == 'mainPost'):
            postTitle = request.form['title']
            postMessage = request.form['content']
            postDate = todaysDate
            postUsername = session.pop('nameID')
            session['nameID'] = postUsername
            
            database = r"data.sqlite"
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            
            timeout = 0
            status = "Failed"
            while(True):
                newID = random.randrange(0, 10)
                cur.execute(f"""
                            SELECT
                                p_id
                            FROM
                                posts
                            """)
                prevIDs = cur.fetchall()
                # Check if newly generated ID exists in previous posts
                if newID not in prevIDs:
                    status = "Success"
                    break
                else:
                    timeout = timeout + 1
                
                if timeout > 20000:
                    break
            
            if (status == "Success"):
                postID = newID
                cur.execute(f"""INSERT OR REPLACE INTO posts (p_title, p_contents, p_date, p_username, p_id)
                                VALUES ("{postTitle}", "{postMessage}", "{postDate}", "{postUsername}", "{postID}")""")
                conn.commit()
                
                cur.execute(f"""
                        SELECT
                            p_title,
                            p_contents,
                            p_date,
                            p_username,
                            p_id
                        FROM
                            posts
                        """)
                data = cur.fetchall()
                result = []
                if (data):
                    for row in data:
                        result.append(f"""<table><tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></table>""")
                else:
                    result.append("<p>No activity yet.. Start a conversation!</p>")
                contents = ''
                for i in result:
                    contents += (i + '\n')
                
                return render_template_string("""
                                            {% extends "forumMain.html" %}
                                            
                                            {% block newPost %}
                                            <h2>Welcome {{name}}!</h2>
                                            <p>Your message has been posted.</p>
                                            {% endblock %}
                                            
                                            {% block oldPost %}
                                            {% autoescape off %}
                                            {{string2html}}
                                            {% endautoescape %}
                                            {% endblock %}
                                            """, string2html = contents, name = postUsername)
            elif (status == "Failed"):
                return render_template_string("""
                                            {% extends "forumMain.html" %}
                                            
                                            {% block newPost %}
                                            <h2>Welcome {{name}}!</h2>
                                            <p>There was an error completing your request!</p>
                                            {% endblock %}
                                            
                                            {% block oldPost %}
                                            {% autoescape off %}
                                            {{string2html}}
                                            {% endautoescape %}
                                            {% endblock %}
                                            """, string2html = contents, name = postUsername)
            

@app.route('/login-verify', methods = ['POST', 'GET'])
def getCredentials():
    """
    To add credentials, use the following (testing only)
    INSERT INTO users (u_username, u_pass)
    VALUES ('ajsin', 'pass'); 
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
                    session['nameID'] = username
                    session['passID'] = password
                    
                    cur.execute(f"""
                                SELECT
                                    p_title,
                                    p_contents,
                                    p_date,
                                    p_username,
                                    p_id
                                FROM
                                    posts
                                """)
                    data = cur.fetchall()
                    result = []
                    if (data):
                        for row in data:
                            result.append(f"""<table><tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></table>""")
                    else:
                        result.append("<p>No activity yet.. Start a conversation!</p>")
                    contents = ''
                    for i in result:
                        contents += (i + '\n')
                        
                    activeUser = session.pop('nameID')
                    session['nameID'] = activeUser
                    return render_template_string("""
                                                {% extends "forumMain.html" %}
                                                
                                                {% block newPost %}
                                                <h2>Welcome {{name}}!</h2>
                                                {% endblock %}
                                                
                                                {% block oldPost %}
                                                {% autoescape off %}
                                                {{string2html}}
                                                {% endautoescape %}
                                                {% endblock %}
                                                """, string2html = contents, name = activeUser)
            else:
                return render_template('login.html')

@app.route('/', methods = ['POST', 'GET'])
def main():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug = True)
    