from flask_login import UserMixin
from datetime import datetime
from app import db

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(20), unique=False, nullable=True)
    last_name = db.Column(db.String(20), unique=False, nullable=True)
    organization = db.Column(db.String(20), unique=False, nullable=True)
    phone = db.Column(db.String(20), unique=False, default="")
    location = db.Column(db.String(20), unique=False, default="")
    website = db.Column(db.String(128), unique=False, default="")
    interests = db.Column(db.String(512), unique=False, default="")
    bio = db.Column(db.Text, nullable=True, default="")
    email = db.Column(db.String(100), nullable=True, default="")
    profile_picture = db.Column(db.String(256), nullable=False, default="")
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

    # Birds submitted by the user
    birds = db.relationship('Bird', backref='user', lazy=True)
    
    # Votes submitted by the user
    votes = db.relationship('BirdVote', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.date_registered}')"

    def get_id(self):
        return str(self.id)
    
class Bird(db.Model):
    __tablename__ = "bird"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=False, nullable=False)
    picture_reference = db.Column(db.Text, unique=False, nullable=False)
    description = db.Column(db.Integer())
    # Geolocation data
    latitude = db.Column(db.Float(), unique=False, nullable=False)
    longitude = db.Column(db.Float(), unique=False, nullable=False)
    
    positive_votes = db.Column(db.Integer(), default=0)
    negative_votes = db.Column(db.Integer(), default=0)
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    votes = db.relationship('BirdVote', backref='bird', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f"Bird('{self.name}', '{self.description}')"

    def get_id(self):
        return str(self.id)

class BirdVote(db.Model):
    __tablename__ = "birdvotes"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Implement a unique constraint on bird_id and user_id
    # to prevent duplicate votes
    
    # Bird ID which relates back to the original bird
    bird_id = db.Column(db.Integer, db.ForeignKey('bird.id'), nullable=False)
    # User ID which relates back to the voting user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Actual vote data
    rating = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"BirdVote('{self.bird_id}', '{self.vote}')"

    def get_id(self):
        return str(self.id)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(1024), unique=True, nullable=False)
    visits = db.Column(db.Integer())
    errors = db.Column(db.Integer())
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f"Link('{self.link}', '{self.visits}')"

    def get_id(self):
        return str(self.id)
