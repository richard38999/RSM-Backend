from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///' + "param.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'richard'
db = SQLAlchemy(app)

class Menu(db.Model):
    __tablename__ = "Menu"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    children = db.Column(db.String(50))
    path = db.Column(db.String(50))

class Menu_one(db.Model):
    __tablename__ = "Menu_one"
    id = db.Column(db.Integer, primary_key=True)
    authName = db.Column(db.String(50))
    children = db.Column(db.String(50))
    path = db.Column(db.String(50))

class Menu_two(db.Model):
    __tablename__ = "Menu_two"
    id = db.Column(db.Integer, primary_key=True)
    authName = db.Column(db.String(50))
    children = db.Column(db.String(50))
    path = db.Column(db.String(50))

class Menu_three(db.Model):
    __tablename__ = "Menu_three"
    id = db.Column(db.Integer, primary_key=True)
    authName = db.Column(db.String(50))
    children = db.Column(db.String(50))
    path = db.Column(db.String(50))

# command
db.session.commit()

# Query
Menu.query.get('')