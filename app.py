from flask import Flask, render_template, url_for, request, redirect, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#this is for the json convertable class Event
from dataclasses import dataclass
from flask_cors import CORS
import uuid


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
#dataclass decorateor for easy turning 
@dataclass
class Event(db.Model):
    #these are for @dataclass object!!
    id: int
    name: str
    date_created: str
    tickets: object
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    tickets = db.relationship('Ticket', backref='event')
    
@dataclass
class Ticket(db.Model):
    id: int
    uuid: str
    owner_id: str
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(120), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    def __repr__(self):
        return '<Pet %r>' % self.owner_id



@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        new_event = Event(name=data['name'])
        try:
            db.session.add(new_event)
            for i in range(1,data['amount']):
                db.session.add(Ticket(uuid=str(uuid.uuid4()), event=new_event))
            db.session.commit()
            return data
        except:
            return 'There was an issue adding your task'

    else:
        return jsonify(Event.query.all())

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Event.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Event.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True)
