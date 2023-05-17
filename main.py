import os, random
from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from twilio.rest import Client
from functools import wraps

app = Flask(__name__)
app.secret_key = 'otp'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///projects.db"
db = SQLAlchemy(app)

class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_id = db.Column(db.Integer, nullable=False)
    is_running = db.Column(db.Boolean, default=True) 


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(100))
    state_id = db.Column(db.Integer, nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=True)

    election = db.relationship('Election', backref=db.backref('elections', lazy=True))

class Voter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aadhar_number = db.Column(db.String(12), unique=True)
    phone_number = db.Column(db.String(10), unique=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=True)
    state_id = db.Column(db.Integer, nullable=False)
    is_voted = db.Column(db.Boolean, default=False) 

    candidate = db.relationship('Candidate', backref=db.backref('voters', lazy=True))

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('admin') == 'ADMIN':
            return redirect("/login_voter")
        elif  request.form.get('voter') == 'VOTER':
            return redirect("/login_admin")
        else:
            return redirect("/") 
    elif request.method == 'GET':
        return render_template("index.html")


@app.route("/login_voter", methods=["GET", "POST"])
def login_voter():
    session.clear()

    if request.method == "POST" :

        if not request.form.get("aadhar_no"):
            return render_template("login_voter.html")

        elif not request.form.get("phone_no"):
            return render_template("login_voter.html")
        
        aadhar_no = request.form['aadhar_no']
        phone_no =  request.form['phone_no']

        row = db.execute("SELECT * FROM voters WHERE aadhar_number=?", aadhar_no)
        if len(row) != 1 or row[0]["phone_no"] != phone_no:
            return render_template("login_voter.html")
        
        session["user_id"] = row[0]["voter_id"]
        
        val=authorization(phone_no)
        if val: 
            return render_template("otp_verify.html")
        else:
            return render_template("login_voter.html")
        
    else:
        return render_template("login_voter.html")
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST" :
        otp = request.form['otp']
        if 'response' in session:
            s = session['response']
            session.pop('response', None)
            if s == otp:
                return render_template("vote.html")
            else:
                return redirect("/login_voter")
    else:
        return redirect("/login_voter")


@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    session.clear()
    if request.method == "POST" :
        if not request.form.get("user_id"):
            return render_template("login_admin.html")

        elif not request.form.get("password"):
            return render_template("login_admin.html")
        
        return render_template("admin_portal.html")
    else:
        return render_template("login_admin.html")
    

    
def generate_otp() :
    return random.randrange(100000,999999)    

def authorization(phone_no) :
    account_sid = "AC7d24198dd5dcf94ca67625e4ef58031b"
    auth_token = os.environ["d83a82680d3ed4cfdff62741ca93da39"]
    client = Client(account_sid, auth_token)
    otp = generate_otp()
    session['response'] = str(otp)
    body = "your otp for phone number verification is" + str(otp)
    message = client.messages.create(
        body=body,
        from_="+12542496883",
        to=phone_no
    )
    print(message.sid)

    if message.sid:
        return True
    else:
        False