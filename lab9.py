import datetime

from flask import Flask, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///development.db')
app.config["DEBUG"] = False if os.getenv("DEBUG", "true").lower() == "false" else True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    message = db.Column(db.String(512))
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, username, message):
        self.username = username
        self.message = message

    def tostring(self):
        return "<%s @ %s> %s" % (self.username, (self.created - datetime.timedelta(hours=4)).strftime("%b/%d/%Y %I:%M %p"), self.message)

    def __repr__(self):
        return '<User %r>' % self.username



@app.route('/postmessage', methods=["POST"])
def post_message():

    if "chatMessage" in request.values and "chatUsername" in request.values:
        message = Message(request.values["chatUsername"], request.values["chatMessage"])
        db.session.add(message)
        db.session.commit()
        return "success"

    # Invalid request
    return "Make sure your parameters are correct! I need 'chatMessage' and " + \
           "'chatUsername' with a ContentType of APPLICATION_FORM_URLENCODED."


@app.route('/getmessages', methods=["GET"])
def get_messages():
    messages = Message.query.order_by(asc(Message.created)).limit(15).all()
    resp = ""
    for message in messages:
        resp += (message.tostring() + ",")
    return resp[:-1]


if __name__ == '__main__':
    app.run()
