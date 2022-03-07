from logging import exception
from flask import Flask, redirect, url_for, request, render_template, send_file, session
from flask_session import Session
import sqlite3
from sqlite3 import Error
from datetime import date
from flask.templating import render_template_string

import sys
app = Flask(__name__)
app.secret_key = 'privateUser'

@app.route('/deletePost', methods = ['POST', 'GET'])
def deletePost():
    if (request.method == 'POST'):
        method = request.form['delete']
        activeUser = method
        postID = session.pop('postID')
        database = r"data.sqlite"
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Delete the post
        cur.execute(f"""
                    DELETE FROM posts
                    WHERE   
                        p_id = {postID}
                    """)
        conn.commit()
        
        # Now delete the replies associated with this post
        cur.execute(f"""
                    DELETE FROM replies
                    WHERE
                        r_id = {postID}
                    """)
        conn.commit()
        return redirect("/refresh")
        

@app.route('/submitReply', methods = ['POST', 'GET'])
def submitReply():
    if (request.method == 'POST'):
        method = request.form['submit']
        postID = eval(method)
        postUsername = session.pop('nameID')
        session['nameID'] = postUsername
        database = r"data.sqlite"
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        
        cur.execute(f"""
                        SELECT
                            r_repID
                        FROM
                            replies
                        WHERE
                            r_id = {postID}
                        """)
        prevIDs = cur.fetchall()
        newID = 0
        status = "Failed"
        while(True):
            if (prevIDs):
                # Check if newly generated ID exists in previous replies
                for val in prevIDs:
                    if newID == val[0]:
                        status = "Failed"
                        break
                    else:
                        status = "Success"
                if (status == "Failed"):
                    newID = newID + 1
                else:
                    break
            else:
                status = "Success"
                break
            if newID > 9999:
                break
        
        # Contents of the message
        entry = request.form['message']
        todaysDate = date.today()
        # pop is used to get username/author name
        # post ID is r_id
        
        cur.execute(f"""
                    INSERT INTO replies (r_contents, r_date, r_author, r_id, r_repID)
                    VALUES ("{entry}", "{todaysDate}", "{postUsername}", "{postID}", "{newID}");
                    """)
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
                postTitle = row[0]
                postContents = row[1]
                postDate = row[2]
                postUsername = row[3]
                postID = row[4]
                cur.execute(f"""
                            SELECT
                                COUNT(DISTINCT(r_repID))
                            FROM
                                replies
                            WHERE
                                r_id = {postID}                              
                                """)
                num = cur.fetchall()
                totComments = num[0][0]
                session['postID'] = postID
                activeUser = session.pop('nameID')
                session['nameID'] = activeUser
                deleteString = ""
                if (activeUser == postUsername):
                    deleteString = f"""
                                    <form action = "/deletePost" method = "POST">
                                        <button type="submit" name="delete" value={activeUser}>Delete Post</button>
                                    </form>
                                    """
                result.append(f"""
                            <div class = "entry">
                                <h3>{postTitle}</h3>
                                <table>
                                    <tr>
                                        <td><em>Author: {postUsername}</em> | <em>Date posted: {postDate}</em></td>
                                    </tr>
                                </table>
                                <p>{postContents}</p>
                                <table>
                                    <tr>
                                        <td>
                                            <form action = "/replyHandler" method = "POST">
                                                <button type="submit" name="reply" value={postID}>Comment</button>
                                            </form>
                                        </td>
                                        <td>
                                            {totComments} comment(s)
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>{deleteString}</td>
                                    </tr>
                                </table>
                            </div>""")
        else:
            result.append("<p>No activity yet.. Start a conversation!</p>")
        contents = ''
        for i in result:
            contents = (i + '\n') + contents
            
        activeUser = session.pop('nameID')
        session['nameID'] = activeUser
        return render_template_string("""
                                    {% extends "forumMain.html" %}
                                    
                                    {% block welcome %}
                                    <h2>Welcome {{name}}!</h2>
                                    {% endblock %}
                                    
                                    {% block oldPost %}
                                    {% autoescape off %}
                                    {{string2html}}
                                    {% endautoescape %}
                                    {% endblock %}
                                    """, string2html = contents, name = activeUser)
        

@app.route('/replyHandler', methods = ['POST', 'GET'])
def replyHandler():
    if (request.method == 'POST'):
        # method will be equal to the postID
        method = request.form['reply']
        postKey = eval(method)
        postUsername = session.pop('nameID')
        session['nameID'] = postUsername
        database = r"data.sqlite"
        conn = sqlite3.connect(database)
        cur = conn.cursor() 
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
        
        # Get the reply section of the post that was selected.
        replyResult = []
        cur.execute(f"""
            SELECT
                r_contents,
                r_date,
                r_author,
                r_id,
                r_repID
            FROM
                replies
            WHERE
                r_id = {postKey}
            """)
        replyData = cur.fetchall()
        
        if (replyData):
            for i in replyData:
                replyContents = i[0]
                replyDate = i[1]
                replyAuthor = i[2]
                replyResult.append(f"""
                                    <table id="replies">
                                        <tr>
                                            <td><em>{replyAuthor}</em> | <em>Posted: {replyDate}</em></td>
                                        </tr>
                                        <tr>
                                            <td>{replyContents}</td>
                                        </tr>
                                    </table>
                                    """)
        else:
            replyResult.append("No comments available. Be the first to join the discussion!")
        
        result = []
        if (data):
            for row in data:
                postTitle = row[0]
                postContents = row[1]
                postDate = row[2]
                postUsername = row[3]
                postID = row[4]
                
                cur.execute(f"""
                            SELECT
                                COUNT(DISTINCT(r_repID))
                            FROM
                                replies
                            WHERE
                                r_id = {postID}                              
                                """)
                num = cur.fetchall()
                totComments = num[0][0]
                session['postID'] = postID
                deleteString = ""
                if (postID == postKey):
                    replyString = ""
                    # Get the replies into a string with the newest tables in front
                    for i in replyResult:
                        replyString = (i + '\n') + replyString
                        # Div is to ensure that the comments are wrapped as part of the post.
                    replyString += "</div>"
                    
                    activeUser = session.pop('nameID')
                    session['nameID'] = activeUser
                    if (activeUser == postUsername):
                        deleteString = f"""
                                        <form action = "/deletePost" method = "POST">
                                            <button type="submit" name="delete" value={activeUser}>Delete Post</button>
                                        </form>
                                        """
                    # Collect the post into a string
                    post2append =f"""
                                <div class = "entry">
                                    <h3>{postTitle}</h3>
                                    <table>
                                        <tr>
                                            <td><em>Author: {postUsername}</em> | <em>Date posted: {postDate}</em></td>
                                        </tr>
                                    </table>
                                    <p>{postContents}</p>
                                    <table>
                                        <tr>
                                            <td>
                                                <form action = "/replyHandler" method = "POST">
                                                    <button type="submit" name="reply" value={postID}>Comment</button>
                                                </form>
                                            </td>
                                            <td>
                                                {totComments} comment(s)
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>{deleteString}</td>
                                        </tr>
                                    </table> 
                                    <form action = "/submitReply" method="POST">
                                        <table>
                                            <tr>
                                                <td><textarea type="text" name="message" id="txtbox"></textarea></td>
                                            </tr>
                                            <tr>
                                                <td><button type="submit" name="submit" value={postKey}>Reply</button></td>
                                            </tr>
                                        </table>
                                    </form>
                                        
                                """
                                # Div is in the replyString
                    # Combine the post string and the reply string
                    post2append += replyString
                    result.append(post2append)
                    
                else:
                    activeUser = session.pop('nameID')
                    session['nameID'] = activeUser
                    if (activeUser == postUsername):
                        deleteString = f"""
                                        <form action = "/deletePost" method = "POST">
                                            <button type="submit" name="delete" value={activeUser}>Delete Post</button>
                                        </form>
                                        """
                    result.append(f"""
                                <div class = "entry">
                                    <h3>{postTitle}</h3>
                                    <table>
                                        <tr>
                                            <td><em>Author: {postUsername}</em> | <em>Date posted: {postDate}</em></td>
                                        </tr>
                                    </table>
                                    <p>{postContents}</p>
                                    <table>
                                        <tr>
                                            <td>
                                                <form action = "/replyHandler" method = "POST">
                                                    <button type="submit" name="reply" value={postID}>Comment</button>
                                                </form>
                                            </td>
                                            <td>
                                                {totComments} comment(s)
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>{deleteString}</td>
                                        </tr>
                                    </table>
                                </div>""")
            contents = ""
            for i in result:
                contents = (i + "\n") + contents
            activeUser = session.pop('nameID')
            session['nameID'] = activeUser
            return render_template_string("""
                                            {% extends "forumMain.html" %}
                                            
                                            {% block welcome %}
                                            <h2>Welcome {{name}}!</h2>
                                            {% endblock %}
                                            
                                            {% block oldPost %}
                                            {% autoescape off %}
                                            {{string2html}}
                                            {% endautoescape %}
                                            {% endblock %}
                                            """, string2html = contents, name = activeUser)
            
@app.route('/createUser', methods = ['POST', 'GET'])
def createUser():
    if (request.method == 'POST'):
        method = request.form['submit']
        if (method == 'back'):
            return render_template('login.html')
        elif (method == 'register'):
            email = request.form['email']
            username = request.form['username']
            password1 = request.form['password']
            password2 = request.form['confirmPassword']
            if (password1 != password2):
                return render_template_string("""
                                        {% extends "register.html" %}
                                       
                                        {% block warning %}
                                        <h2>Passwords did not match</h3>
                                        {% endblock %}
                                       
                                       """)
            else:
                database = r"data.sqlite"
                conn = sqlite3.connect(database)
                cur = conn.cursor()
                
                cur.execute(f"""
                            SELECT u_username
                            FROM users
                            WHERE u_username = "{username}"
                            """)
                data = cur.fetchall()
                if (data):
                    return render_template_string("""
                                        {% extends "register.html" %}
                                       
                                        {% block warning %}
                                        <h2>Username exists!</h3>
                                        {% endblock %}
                                       """)
                else:
                    cur.execute(f"""
                                INSERT INTO users (u_username, u_pass, u_email)
                                VALUES ("{username}", "{password1}", "{email}");
                                """)
                    conn.commit()
                    return render_template("login.html")
                
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
            
            newID = 0
            status = "Failed"
            cur.execute(f"""
                            SELECT
                                p_id
                            FROM
                                posts
                            """)
            prevIDs = cur.fetchall()
            while(True):
                if (prevIDs):
                    # Check if newly generated ID exists in previous posts
                    for val in prevIDs:
                        if newID == val[0]:
                            status = "Failed"
                            break
                        else:
                            status = "Success"
                    if (status == "Failed"):
                        newID = newID + 1
                    else:
                        break
                else:
                    status = "Success"
                    break
                if newID > 9999:
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
                        postTitle = row[0]
                        postContents = row[1]
                        postDate = row[2]
                        postUsername = row[3]
                        postID = row[4]
                        cur.execute(f"""
                                    SELECT
                                        COUNT(DISTINCT(r_repID))
                                    FROM
                                        replies
                                    WHERE
                                        r_id = {postID}                              
                                        """)
                        num = cur.fetchall()
                        totComments = num[0][0]
                        session['postID'] = postID
                        activeUser = session.pop('nameID')
                        session['nameID'] = activeUser
                        deleteString = ""
                        if (activeUser == postUsername):
                            deleteString = f"""
                                <form action = "/deletePost" method = "POST">
                                    <button type="submit" name="delete" value={activeUser}>Delete Post</button>
                                </form>
                                """
                        result.append(f"""
                                    <div class = "entry">
                                        <h3>{postTitle}</h3>
                                        <table>
                                            <tr>
                                                <td><em>Author: {postUsername}</em> | <em>Date posted: {postDate}</em></td>
                                            </tr>
                                        </table>
                                        <p>{postContents}</p>
                                        <table>
                                            <tr>
                                                <td>
                                                    <form action = "/replyHandler" method = "POST">
                                                        <button type="submit" name="reply" value={postID}>Comment</button>
                                                    </form>
                                                </td>
                                                <td>
                                                    {totComments} comment(s)
                                                </td>
                                            </tr>   
                                            <tr>
                                                <td>{deleteString}</td>
                                            </tr>
                                        </table>
                                    </div>""")
                else:
                    result.append("<p>No activity yet.. Start a conversation!</p>")
                contents = ''
                for i in result:
                    contents = (i + '\n') + contents
                activeUser = session.pop('nameID')
                session['nameID'] = activeUser
                return render_template_string("""
                                            {% extends "forumMain.html" %}
                                            
                                            {% block welcome %}
                                            <h2>Welcome {{name}}!</h2>
                                            {% endblock %}
                                            
                                            {% block oldPost %}
                                            <p id='confirm'>Your message has been posted.</p>
                                            {% autoescape off %}
                                            {{string2html}}
                                            {% endautoescape %}
                                            {% endblock %}
                                            """, string2html = contents, name = activeUser)
            elif (status == "Failed"):
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
                        postTitle = row[0]
                        postContents = row[1]
                        postDate = row[2]
                        postUsername = row[3]
                        postID = row[4]
                        
                        cur.execute(f"""
                                    SELECT
                                        COUNT(DISTINCT(r_repID))
                                    FROM
                                        replies
                                    WHERE
                                        r_id = {postID}                              
                                        """)
                        num = cur.fetchall()
                        totComments = num[0][0]
                        session['postID'] = postID
                        deleteString = ""
                        activeUser = session.pop('nameID')
                        session['nameID'] = activeUser
                        if (activeUser == postUsername):
                            deleteString = f"""
                                            <form action = "/deletePost" method = "POST">
                                                <button type="submit" name="delete" value={activeUser}>Delete Post</button>
                                            </form>
                                            """
                        result.append(f"""
                                    <div class = "entry">
                                        <h3>{postTitle}</h3>
                                        <table>
                                            <tr>
                                                <td><em>Author: {postUsername}</em> | <em>Date posted: {postDate}</em></td>
                                            </tr>
                                        </table>
                                        <p>{postContents}</p>
                                        <table>
                                            <tr>
                                                <td>
                                                    <form action = "/replyHandler" method = "POST">
                                                        <button type="submit" name="reply" value={postID}>Comment</button>
                                                    </form>
                                                </td>
                                                <td>
                                                    {totComments} comment(s)
                                                </td>
                                            </tr>
                                        </table>
                                    </div>""")
                else:
                    result.append("<p>No activity yet.. Start a conversation!</p>")
                contents = ''
                for i in result:
                    contents = (i + '\n') + contents
                return render_template_string("""
                                            {% extends "forumMain.html" %}
                                            
                                            {% block welcome %}
                                            <h2>Welcome {{name}}!</h2>
                                            {% endblock %}
                                            
                                            {% block oldPost %}
                                            <p id='confirm'>There was an error completing your request!</p>
                                            {% autoescape off %}
                                            {{string2html}}
                                            {% endautoescape %}
                                            {% endblock %}
                                            """, string2html = contents, name = activeUser)
            
@app.route('/login-verify', methods = ['POST', 'GET'])
def getCredentials():
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
                    activeUser = session.pop('nameID')
                    session['nameID'] = activeUser
                    if (data):
                        for row in data:
                            postTitle = row[0]
                            postContents = row[1]
                            postDate = row[2]
                            postUsername = row[3]
                            postID = row[4]
                            cur.execute(f"""
                                        SELECT
                                            COUNT(DISTINCT(r_repID))
                                        FROM
                                            replies
                                        WHERE
                                            r_id = {postID}                              
                                            """)
                            num = cur.fetchall()
                            totComments = num[0][0]
                            session['postID'] = postID
                            deleteString = ""
                            if (activeUser == postUsername):
                                deleteString = f"""
                                                <form action = "/deletePost" method = "POST">
                                                    <button type="submit" name="delete" value={activeUser}>Delete Post</button>
                                                </form>
                                                """
                            result.append(f"""
                                        <div class = "entry">
                                            <h3>{postTitle}</h3>
                                            <table>
                                                <tr>
                                                    <td><em>Author: {postUsername}</em> | <em>Date posted: {postDate}</em></td>
                                                </tr>
                                            </table>
                                            <p>{postContents}</p>
                                            <table>
                                                <tr>
                                                    <td>
                                                        <form action = "/replyHandler" method = "POST">
                                                            <button type="submit" name="reply" value={postID}>Comment</button>
                                                        </form>
                                                    </td>
                                                    <td>
                                                        {totComments} comment(s)
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td>{deleteString}</td>
                                                </tr>
                                            </table>
                                        </div>""")
                    else:
                        result.append("<h2 id='empty'>No activity yet.. Start a conversation!</h2>")
                    contents = ''
                    for i in result:
                        contents = (i + '\n') + contents
                    return render_template_string("""
                                                {% extends "forumMain.html" %}
                                                
                                                {% block welcome %}
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
        
        if (method == 'register'):
            return render_template('register.html')
@app.route('/refresh', methods = ['POST', 'GET'])
def refresh():
    database = r"data.sqlite"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
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
    activeUser = session.pop('nameID')
    session['nameID'] = activeUser
    if (data):
        for row in data:
            postTitle = row[0]
            postContents = row[1]
            postDate = row[2]
            postUsername = row[3]
            postID = row[4]
            session['postID'] = postID
            cur.execute(f"""
                        SELECT
                            COUNT(DISTINCT(r_repID))
                        FROM
                            replies
                        WHERE
                            r_id = {postID}                              
                            """)
            num = cur.fetchall()
            totComments = num[0][0]
            deleteString = ""
            if (activeUser == postUsername):
                deleteString = f"""
                                <form action = "/deletePost" method = "POST">
                                    <button type="submit" name="delete" value={activeUser}>Delete Post</button>
                                </form>
                                """
            result.append(f"""
                        <div class = "entry">
                            <h3>{postTitle}</h3>
                            <table>
                                <tr>
                                    <td><em>Author: {postUsername}</em> | <em>Date posted: {postDate}</em></td>
                                </tr>
                            </table>
                            <p>{postContents}</p>
                            <table>
                                <tr>
                                    <td>
                                        <form action = "/replyHandler" method = "POST">
                                            <button type="submit" name="reply" value={postID}>Comment</button>
                                        </form>
                                    </td>
                                    <td>
                                        {totComments} comment(s)
                                    </td>
                                </tr>
                                <tr>
                                    <td>{deleteString}</td>
                                </tr>
                            </table>
                        </div>""")
    else:
        result.append("<h2 id='empty'>No activity yet.. Start a conversation!</h2>")
    contents = ''
    for i in result:
        contents = (i + '\n') + contents
    return render_template_string("""
                                {% extends "forumMain.html" %}
                                
                                {% block welcome %}
                                <h2>Welcome {{name}}!</h2>
                                {% endblock %}
                                
                                {% block oldPost %}
                                {% autoescape off %}
                                {{string2html}}
                                {% endautoescape %}
                                {% endblock %}
                                """, string2html = contents, name = activeUser)

@app.route('/', methods = ['POST', 'GET'])
def main():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug = True)
    