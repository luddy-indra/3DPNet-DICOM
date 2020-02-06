from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import os
import pathlib

from werkzeug.utils import secure_filename

from StlConverter import *

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'LIP123!'
app.config['MYSQL_DB'] = 'lip-project'

app.config['PATH_HZIP'] = '/home/jupyter-luddy/Luddy_Project/data/history_zip/'
app.config['PATH_HSTL'] = '/home/jupyter-luddy/Luddy_Project/data/history_stl/'
#app.config['PATH_HGCODE'] = '/home/jupyter-luddy/Luddy_Project/data/history_gcode/'
app.config['PATH_TSTL'] = '/home/jupyter-luddy/Luddy_Project/data/temporary_stl/'
#app.config['PATH_TGCODE'] = '/home/jupyter-luddy/Luddy_Project/data/temporary_gcode/'
app.config['PATH_T3D'] = '/home/jupyter-luddy/Luddy_Project/data/temporary_3d_images/'

ALLOWED_EXTENSIONS = set(['zip', 'stl'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Intialize MySQL
mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['customer_name'] = account['customer_name']
            session['customer_email'] = account['customer_email']
            #es = EmailSender()
            #print(account['customer_email'])
            #es.send_mail('luddybejo@gmail.com',account['customer_email'],'3DIRL Email','Anda berhasil login','app.py')
            #yag = yagmail.SMTP('luddybejo@gmail.com',oauth2_file='client_secret.json')
            #yag.send(to=account['customer_email'], subject='3DIRL EMail', contents='Anda berhasil login')
            # Redirect to home page
            return redirect(url_for('home'))
            #return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg='')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('customer_name', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'customer_name' in request.form and 'customer_handphone' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        customer_name = request.form['customer_name']
        customer_handphone = request.form['customer_handphone']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not customer_name or not customer_handphone:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts(username, password, customer_name, customer_email, customer_handphone)  VALUES ( %s, %s, %s, %s, %s)', (username, password, customer_name, email, customer_handphone,))
            mysql.connection.commit()
            msg = msg + 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', customer_name=session['customer_name'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/upload")
def upload():
    return render_template('fileform.html')

@app.route("/fileupload", methods=['GET', 'POST'])
def fileupload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'datafile' not in request.files:
            msg = 'No file part to upload!'
            return render_template('fileform.html', msg=msg)
        file = request.files['datafile']
        if file.filename == '':
            msg = 'No file selected for uploading'
            return render_template('fileform.html', msg=msg)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #print(app.config['PATH_HZIP']+filename)
            file.save(os.path.join(app.config['PATH_HZIP'], str(session['username']+'_'+filename)))
            #file.save(os.path.join(app.config['PATH_HZIP'], str(filename)))
            msg = 'File  ' + filename + '  successfully uploaded'
            converter = StlConverter()
            ext = filename.rfind('.')
            stl_file = str(filename)[:ext] + '.stl'
            stl_path = os.path.join(app.config['PATH_HSTL'], str(session['username']+'_'+stl_file))
            stl1_path = os.path.join(app.config['PATH_TSTL'], str(session['username']+'_'+stl_file))
            converter.convert_to_stl(os.path.join(app.config['PATH_HZIP'], str(session['username']+'_'+filename))).save(stl_path)
            converter.convert_to_stl(os.path.join(app.config['PATH_HZIP'], str(session['username']+'_'+filename))).save(stl1_path)
            #converter.convert_to_stl(os.path.join(app.config['PATH_HZIP'], filename)).save(stl_path)
            #msg = msg + ' and converted to STL file' 
            print("STL process finish")
            #es = EmailSender()
            #es.send_mail('gcoded747@gmail.com',session['customer_email'],'3DIRL System',msg,stl_path)
            #gconverter = GcodeConverter()
            #gcode_file = str(filename)[:ext] + '.gcode'
            #gcode_path = os.path.join(app.config['PATH_HGCODE'], gcode_file)
            #gconverter.convert_to_gcode(stl_path).save(gcode_path)
            return render_template('fileform.html', msg=msg)
        else:
            msg = 'Allowed file types are zip and stl'
            return render_template('fileform.html', msg=msg)

if __name__ == '__main__':
   app.run(host='0.0.0.0')
