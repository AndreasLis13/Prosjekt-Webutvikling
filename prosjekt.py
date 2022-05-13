from distutils.command import check
from urllib import response
from flask import Flask, make_response, redirect, url_for, render_template, request, session, flash
from flask_login import login_required
import mysql.connector
from datetime import timedelta
from ConvertData import *
from Attachment import Attachment, Comment
from filearchive import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import uuid 
import socket


app = Flask(__name__)
app.secret_key = "76v4cxmdv963d4tl849on432sk"
app.permanent_session_lifetime = timedelta(minutes=60)
app.config['MAX_CONTENT_LEMGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'gif', 'mp4', 'webm', 'ogg', 'zip'}
app.config['MAIL_SERVER'] = 'smtpserver.uit.no'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'Ali094@uit.no'
mail = Mail(app)


dbconfig = { 'host': 'kark.uit.no',
    'user': 'stud_v22_lislelidand',
    'password': '63D4tl84',
    'database': 'stud_v22_lislelidand', }


#Hovedside
@app.route("/")
@app.route('/index')
def home():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """SELECT * FROM Dokument ORDER BY Dato DESC""";
    cursor.execute(_SQL)
    result = cursor.fetchall()
    attachments = [Attachment(*x) for x in result]

    _SQL_TWO = """SELECT * FROM Kommentar""";
    cursor.execute(_SQL_TWO)
    results_two = cursor.fetchall()
    comments = [Comment(*x) for x in results_two]

    return render_template("/index.html", attachments = attachments, comments = comments)


#Registrering av bruker 
@app.route('/register', methods = ["GET", "POST"])
def register():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()

    if request.method == "GET":
        return render_template('/register.html')

    else:
        brukernavn = request.form["brukernavn"].encode('utf-8')
        passord = request.form["passord"]
        hashed_password = generate_password_hash(passord)
        email = request.form["email"].encode('utf-8')
        random_uuid = str(uuid.uuid4())
        _SQL =  """INSERT INTO Bruker 
                       (BrukerId, BrukerNavn, Passord, Mail_Adresse, EmailId) 
                       VALUES (Null, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (brukernavn, hashed_password, email, random_uuid))
        conn.commit()
        session['brukernavn'] = brukernavn
        session['email'] = email
        session['innlogget'] = True

        msg = Message('Registration', sender = "Ali094@uit.no", recipients = [email.decode('utf-8')])
        msg.body = 'Confirmation of registration'
        msg.html = '<b> Please click this link to confirm</b>' + '<a href="http://127.0.0.1:5000/confirm.html" >Klikk her</a>'
        with app.app_context():
            mail.send(msg)

        flash('Successfull registration, please check your email')
        return redirect(url_for('home'))


#Innlogging av eksisterende bruker 
@app.route('/')
@app.route('/login', methods = ['GET', 'POST'])
def login():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()

    if request.method == "GET": 
        return render_template('/login.html')

    elif request.method == "POST":
        brukernavn = request.form["brukernavn"].encode('utf-8')
        passord = request.form["passord"]
        _SQL = """SELECT * FROM Bruker where BrukerNavn = %s"""
        cursor.execute(_SQL, (brukernavn,))
        bruker = cursor.fetchone()
        hashed = bruker[2]

        checked = check_password_hash(hashed, passord)

        if bruker and checked:
            session['innlogget'] = True
            session['brukernavn'] = brukernavn
            flash("Successfully logged in")
            return redirect(url_for('home'))

        else:
            flash("Wrong username or password, or user does not exist")
            return render_template('/login.html')

#Utlogging av innlogget bruker, fjerne session og redirecte til index/home
@app.route('/logout')
def logout():
    session.pop('Innlogget', None)
    session.pop('id', None)
    session.pop('Brukernavn', None)
    session.clear()
    return redirect(url_for('home'))

#Informasjonsside, veldig enkel
@app.route('/about')
def about():
    return render_template('/about.html')

#Legge til ny video, lydfil el bilde 
@app.route('/addnew', methods = ['GET', 'POST'])
def addnew():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()

    username = session['brukernavn'].decode('utf-8')
    USR_SQL = """SELECT BrukerID FROM Bruker WHERE BrukerNavn = %s """;
    cursor.execute(USR_SQL, (username,))
    userid = cursor.fetchone()
    brukerid = userid[0]

    if request.method == 'GET':
        return render_template('/addnew.html')
    
    elif request.method == 'POST' and session['innlogget'] is True:
        
        kategori = request.form['kategori']
        tittel = request.form['tittel']
        beskrivelse = request.form['beskrivelse']
        fil = request.files['innlegg']
        mimetype = fil.mimetype
        blob = request.files['innlegg'].read()
        size = len(blob)

        _SQL = """INSERT INTO Dokument 
                              (BrukerId, KategoriId, Tittel, Beskrivelse, File, Mimetype, Size)
                              VALUES(%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (brukerid, kategori, tittel, beskrivelse, blob, mimetype, size))
        conn.commit()
        return redirect(url_for('home'))

#Vise BLOB fila 
@app.route('/download/<id>')
def download_file(id):
    with FileArchive() as db: 
        attachment = Attachment(*db.get(id))

    if attachment is None:
        pass 
    else:
        response = make_response(attachment.File)
        response.headers.set('Content-Type', attachment.mimetype)
        response.headers.set('Content-length', attachment.size)
        response.headers.set('Conent-Disposition', 'inline', filename = attachment.Tittel)
        return response

#Kategori Video(1)
@app.route('/video')
def video():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """SELECT * FROM Dokument WHERE KategoriId = 1 ORDER BY Dato DESC""";
    cursor.execute(_SQL)
    result = cursor.fetchall()
    videos = [Attachment(*x) for x in result]

    return render_template("video.html", videos = videos)

@app.route('/music')
def music():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """SELECT * FROM Dokument WHERE KategoriId = 2 ORDER BY Dato DESC""";
    cursor.execute(_SQL)
    result = cursor.fetchall()
    music = [Attachment(*x) for x in result]

    return render_template("music.html", music = music)

@app.route('/picture')
def picture():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """SELECT * FROM Dokument WHERE KategoriId = 3 ORDER BY Dato DESC""";
    cursor.execute(_SQL)
    result = cursor.fetchall()
    pictures = [Attachment(*x) for x in result]

    return render_template("picture.html", pictures = pictures)


@app.route('/delete/<string:id>', methods=['POST'])
def delete(id):
    if session['innlogget'] == True:
        conn = mysql.connector.connect(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Dokument WHERE id = (%s)", (id,))
        conn.commit()
        flash('Successfully deleted')
        return redirect(url_for('home'))

@app.route('/deleteComment/<string:id>', methods = ['POST'])
def deleteComment(id):
    if session['innlogget'] == True:
        try:
            conn = mysql.connector.connect(**dbconfig)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Kommentar WHERE KommentarId = (%s)", (id,))
            conn.commit()
            return redirect(url_for('home'))
        
        except:
            flash("You have no autorithy to delete this comment")
            return redirect(url_for('home'))

@app.route('/comment/<id>', methods = ['POST'])
def comment(id):

    if session['innlogget'] != True:
        flash("You need to be logged in to leave a comment")
        return redirect(url_for('home'))

    if session['innlogget'] == True:
        conn = mysql.connector.connect(**dbconfig)
        cursor = conn.cursor()

        username = session['brukernavn'].decode('utf-8')
        USR_SQL = """SELECT BrukerID FROM Bruker WHERE BrukerNavn = %s """;
        cursor.execute(USR_SQL, (username,))
        userid = cursor.fetchone()
        brukerid = userid[0]
        kommentar = request.form['kommentar']

        if kommentar:

            _SQL = """INSERT INTO Kommentar 
            (PostId, Kommentar, BrukerId) VALUES(%s, %s, %s)"""
            cursor.execute(_SQL, (id, kommentar, brukerid))
            conn.commit()
            return redirect(url_for('home'))
        
        else:
            flash('Comment cannot be empty')
            return redirect(url_for('home'))


@app.route('/confirm<string:id>', methods = ["POST", "GET"])
def confirm(id):

    if request.method == "GET":
        return render_template('confirm.html')

    else:
        conn = mysql.connector.connect(**dbconfig)
        cursor = conn.cursor()
        _SQL = """SELECT EmailId FROM Bruker where BrukerNavn = %s"""
        cursor.execute(_SQL, (id,))
        emailid = cursor.fetchone()

        if emailid:
            flash('Du har når registrert emailadressen din')
            return redirect(url_for('home'))
        
        else:
            flash('Noe gikk galt')

if __name__ == "__main__":
    app.run(debug=True)



