from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from app import db
from datetime import datetime
import uuid

class VotingSession(db.Model):
    __tablename__ = 'voting_session'
    session_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    option_list = db.Column(db.Text, nullable=True)  # Multiple lines text with each line an option
    is_active = db.Column(db.Boolean, default=True)
    vote_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    creator_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='voting_session', lazy=True)
    # Add a relationship to the User model
    creator = db.relationship('User', backref='created_voting_sessions')

class Task(db.Model):
    __tablename__ = 'task'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    option_list = db.Column(db.Text, nullable=True)  # Multiple lines text with each line an option
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_id = db.Column(db.String(36), db.ForeignKey('voting_session.session_id'), nullable=False)

class Vote(db.Model):
    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(36), db.ForeignKey('voting_session.session_id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.task_id'), nullable=True)
    task = db.relationship('Task', backref='votes', lazy=True)

    vote_value = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    votes = db.relationship('Vote', backref='user', lazy=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Flask-Login integration
    def get_id(self):
        return str(self.id)  # Convert the ID to a string
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
42     # For estimation: estimated points; for options_voting: selected option
