from logging import exception
from flask import Flask, redirect, url_for, request, render_template,send_file
import sqlite3
from sqlite3 import Error
from werkzeug.utils import secure_filename

from flask.templating import render_template_string
import sys
app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def start():
  return render_template('login.html')



@app.route('/upload_to_dir', methods = ['POST', 'GET'])
def upload():
  if(request.method == "POST"):
    uploaded_file = request.files['file']
    num = open("curr","r").read()
    num = int(num)
    num = num + 1
    
    if uploaded_file.filename != '' and uploaded_file.filename.endswith(".zip"):
        uploaded_file.save(f"uploads/{num}.zip")

    open("curr","w").write(str(num))
    return f"OK, your ID is {num}"
  else:
    return render_template("upload.html")

@app.route('/download/<id>', methods = ['POST', 'GET'])
def download(id):

  secure_filename(f"uploads/{id}.zip")

  return send_file(f"uploads/{id}.zip", as_attachment=True, download_name="BetaDownload.zip")


@app.route("/homepage")
def home():
  return render_template("homepage.html")
  
# Godly debugging tool don't forget!
# print(variable, file=sys.stderr)

if __name__ == '__main__':
   app.run(debug = True)
