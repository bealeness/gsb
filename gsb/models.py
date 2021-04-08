from gsb import db, login_manager
from datetime import datetime
from flask_login import UserMixin
import pytz

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Terms(db.Model):
    __tablename__ = 'terms'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), primary_key=True)
    balance = db.Column(db.Numeric(20, 2), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Pacific/Auckland")))

    owner = db.relationship("User", backref="term_owner")
    term = db.relationship("Term", backref="term")
    


class Bonds(db.Model):
    __tablename__ = 'bonds'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    bond_id = db.Column(db.Integer, db.ForeignKey('bond.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Pacific/Auckland")))
    
    owner = db.relationship("User", backref="bond_owner")
    bond = db.relationship("Bond", backref="bond")


class Buys(db.Model):
    __tablename__ = 'buys'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    bond_id = db.Column(db.Integer, db.ForeignKey('bond.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    bid = db.Column(db.Numeric(6, 2), nullable=False)
    rate = db.Column(db.Numeric(4, 2), nullable=False)
    yd = db.Column(db.Numeric(4, 2), nullable=False)
    
    buyer = db.relationship("User", backref="buyer")
    bond = db.relationship("Bond", backref="bond_buy")
    


class Sells(db.Model):
    __tablename__ = 'sells'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    bond_id = db.Column(db.Integer, db.ForeignKey('bond.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    offer = db.Column(db.Numeric(6, 2), nullable=False)
    rate = db.Column(db.Numeric(4, 2), nullable=False)
    yd = db.Column(db.Numeric(4, 2), nullable=False)
    

    seller = db.relationship("User", backref="seller")
    bond = db.relationship("Bond", backref="bond_sell")
    



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
    terms = db.relationship('Term', secondary="terms")
    bonds = db.relationship('Bond', secondary="bonds")
    buys = db.relationship('Bond', secondary="buys")
    sells = db.relationship('Bond', secondary="sells")
    receives = db.relationship('Receives', lazy='dynamic', backref='receiver')
    sends = db.relationship('Sends', lazy='dynamic', backref='sender')
    posts = db.relationship('Statuses', lazy='dynamic', backref='poster')
    messages = db.relationship('Messages', lazy='dynamic', backref='messager')

    
    def __repr__(self):
        return f"User('{self.username}', '{self.cash}')"



class Receives(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Pacific/Auckland")))
    note = db.Column(db.String(300), nullable=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    t_transaction = db.Column(db.Boolean, default=False, nullable=False)
    b_transaction = db.Column(db.Boolean, default=False, nullable=False)
    sender = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Numeric(20,2), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Sends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Pacific/Auckland")))
    note = db.Column(db.String(30), nullable=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    t_transaction = db.Column(db.Boolean, default=False, nullable=False)
    b_transaction = db.Column(db.Boolean, default=False, nullable=False)
    receiver = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Numeric(20,2), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Statuses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Pacific/Auckland")))
    status = db.Column(db.String(100), nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Pacific/Auckland")))
    receiver = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(300), nullable=False)
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



