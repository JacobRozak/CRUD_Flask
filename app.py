from flask import Flask, render_template, url_for, request, redirect, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
    reedeemed: bool
    owner_id: str
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(120), unique=True, nullable=False)
    reedeemed = db.Column(db.Boolean, unique=False, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('event.id'))



@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        new_event = Event(name=data['name'])
        try:
            db.session.add(new_event)
            for i in range(1,data['amount']+1):
                db.session.add(Ticket(uuid=str(uuid.uuid4()), event=new_event))
            db.session.commit()
            return data
        except:
            return 'There was an issue adding your task'

    else:
        return jsonify(Event.query.all())

@app.route('/event/<int:id>')
def event(id):
    data = Event.query.all()
    for element in data:
        if element.id == int(id):
           return jsonify(element)

@app.route('/redeem/<int:id>')
def redeem(id):
    uuid = request.args.get('uuid')
    task = Event.query.get_or_404(id)
    for ticket in task.tickets:
        try:
            if ticket.uuid == uuid:
                ticket.reedeemed = True
                db.session.commit()
                return jsonify(task.tickets)
        except:
            return 'Ticket doesnt exist or its already redeemed'
    

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Event.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return jsonify(task_to_delete)
    except:
        return 'There was a problem deleting that task'

@app.route('/deleteTicket/<int:id>')
def deleteTicket(id):
    uuid = request.args.get('uuid')
    ticket_to_delete = Event.query.get_or_404(id)
    #return jsonify(ticket_to_delete.tickets)
    for i in ticket_to_delete.tickets:
        try:
            if i.uuid == uuid:
                db.session.delete(i)
                db.session.commit()
                return jsonify(ticket_to_delete.tickets)
        except:
            return 'whoopsie, something went wrong'    
    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Event.query.get_or_404(id)
    data = request.get_json()
    
    try:
        task.name = data['name']
        for i in range(1, int(data['amount']) + 1):
            db.session.add(Ticket(uuid=str(uuid.uuid4()), event=task))
        db.session.commit()
        return jsonify(task)
    except:
        return 'There was an issue updating your task'

@app.route('/reset/<int:id>')
def reset(id):
    task = Event.query.get_or_404(id)
    for i in task.tickets:
        i.reedeemed = False
    db.session.commit()
    return jsonify(task.tickets)
    
if __name__ == "__main__":
    app.run(debug=True)
