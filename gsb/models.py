from gsb import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

terms = db.Table('terms',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('term_id', db.Integer, db.ForeignKey('term.id'), primary_key=True),
    db.Column('balance', db.Numeric(20, 2), nullable=False),
    db.Column('timestamp', db.DateTime, nullable=False, default=datetime.utcnow)
    )


bonds = db.Table('bonds',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('bond_id', db.Integer, db.ForeignKey('bond.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('timestamp', db.DateTime, nullable=False, default=datetime.utcnow)
    )


buys = db.Table('buys',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('bond_id', db.Integer, db.ForeignKey('bond.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('bid', db.Numeric(6, 2), nullable=False)
    )


sells = db.Table('sells',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('bond_id', db.Integer, db.ForeignKey('bond.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('offer', db.Numeric(6, 2), nullable=False)
    )



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    account = db.Column(db.BigInteger, unique=True, nullable=False)
    cash = db.Column(db.Numeric(20, 2), nullable=False)
    admin =  db.Column(db.Boolean, default=False, nullable=False)
    image = db.Column(db.Integer, default=1, nullable=False)
    term = db.Column(db.Numeric(20, 2), nullable=False)
    bond = db.Column(db.Numeric(20, 2), nullable=False)
    total = db.Column(db.Numeric(20, 2), nullable=False)
    terms = db.relationship('Term', secondary=terms, lazy='dynamic', backref=db.backref('owners', lazy=True))
    bonds = db.relationship('Bond', secondary=bonds, lazy='dynamic', backref=db.backref('owners', lazy=True))
    buys = db.relationship('Bond', secondary=buys, lazy='dynamic', backref=db.backref('buyers', lazy=True))
    sells = db.relationship('Bond', secondary=sells, lazy='dynamic', backref=db.backref('sellers', lazy=True))
    receives = db.relationship('Receives', lazy='dynamic', backref='receiver')
    sends = db.relationship('Sends', lazy='dynamic', backref='sender')

    
    def __repr__(self):
        return f"User('{self.username}', '{self.cash}')"



class Receives(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    note = db.Column(db.String(30), nullable=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    t_transaction = db.Column(db.Boolean, default=False, nullable=False)
    b_transaction = db.Column(db.Boolean, default=False, nullable=False)
    sender = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Numeric(20,2), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Sends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    note = db.Column(db.String(30), nullable=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    t_transaction = db.Column(db.Boolean, default=False, nullable=False)
    b_transaction = db.Column(db.Boolean, default=False, nullable=False)
    receiver = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Numeric(20,2), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    



class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    maturity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Numeric(4, 2), nullable=False)
    


class Bond(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    ref_num = db.Column(db.Integer, unique=True, nullable=False)
    maturity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Numeric(4, 2), nullable=False)
    face_value = db.Column(db.Numeric(6, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

