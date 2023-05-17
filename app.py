from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
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
  


@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "main":
    app.run(debug=True)    


