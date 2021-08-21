from flask import Flask, request, render_template, url_for, redirect, session
from flask_mysqldb import MySQL
import hashlib
import MySQLdb.cursors
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'toor1234'
app.config['MYSQL_DB'] = 'pythonflask'

mysql = MySQL(app)


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'loggedin' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        usr = request.form['username']
        pwd = request.form['password']
        psw = hashlib.md5(pwd.encode())

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM akun WHERE username = %s AND password = %s', (usr, psw.hexdigest()))
        akun = cursor.fetchone()

        if akun:
            session['loggedin'] = True
            session['username'] = akun['username']
            return redirect(url_for('home'))
        else:
            return render_template('index.html', info='Invalid username/password')

    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    msg = ''
    if 'loggedin' in session:
        return redirect(url_for('home'))

    if request.method == "POST" and 'username' in request.form and 'password1' in request.form and 'password2' in request.form:
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM akun WHERE username = %s', [username])
        akun = cursor.fetchone()

        if akun:
            msg = 'Akun Sudah terdaftar!'
            return render_template('register.html', info=msg)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username hanya terdiri dari Huruf dan Angka!'
            return render_template('register.html', info=msg)
        elif password1 != password2:
            msg = 'Password tidak cocok'
            return render_template('register.html', info=msg)
        elif not username or not password1 or not password2:
            msg = 'Harap isi Form secara lengkap!'
            return render_template('register.html', info=msg)
        else:
            psw = hashlib.md5(password1.encode())
            cursor.execute(
                'INSERT INTO akun VALUES (%s,%s)', (username, psw.hexdigest()))
            mysql.connection.commit()
            msg = 'Anda Berhasil Mendaftar!'
            return render_template('register.html', info=msg)

    elif request.method == "POST" and 'username' not in request.form and 'password1' not in request.form and 'password2' not in reques.form:
        msg = 'Harap isi Form secara lengkap!'
        return render_template('register.html', info=msg)
    return render_template('register.html', info=msg)


@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', name=session['username'])
    else:
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    if 'loggedin' in session:
        session.pop('loggedin')
        session.pop('username')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
