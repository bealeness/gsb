from flask import Flask, render_template, flash, redirect, url_for
from forms import (RegistrationForm, LoginForm, PaySomeone, TermProducts, 
                    BuyBond, SellBond, UpdateAccountForm)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    form = LoginForm()
    return render_template("logged_out/gsb.html", title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for { form.username.data }!', 'success')
        return redirect(url_for('home'))
    return render_template("logged_out/register.html", title='Register', form=form)


@app.route('/mypersonal', methods=['GET', 'POST'])
def my_personal():
    return render_template('my_personal.html', title='MyPersonal')


@app.route('/paysomeone', methods=['GET', 'POST'])
def pay_someone():
    form = PaySomeone()
    return render_template('pay_someone.html', title='PaySomeone', form=form)


@app.route('/myterm', methods=['GET'])
def my_term():
    return render_template('my_term.html', title='MyTerm')


@app.route('/termproducts', methods=['GET', 'POST'])
def term_products():
    form = TermProducts()
    return render_template('term_products.html', title='TermProducts', form=form)


@app.route('/mybond', methods=['GET'])
def my_bond():
    return render_template('my_bond.html', title='MyBond')


@app.route('/buybond', methods=['GET'])
def buy_bond():
    form = BuyBond()
    return render_template('buy_bond.html', title='BuyBond', form=form)


@app.route('/sellbond', methods=['GET'])
def sell_bond():
    form = SellBond()
    return render_template('sell_bond.html', title='SellBond', form=form)


@app.route('/bondmarket', methods=['GET'])
def bond_market():
    return render_template('bond_market.html', title='BondMarket')


@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    return render_template('leaderboard.html', title='Leaderboard')


@app.route('/accountsettings', methods=['GET'])
def account_settings():
    form = UpdateAccountForm()
    return render_template('account_settings.html', title='AccountSettings', form=form)



#MODELS

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



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    account = db.Column(db.BigInteger, unique=True, nullable=False)
    cash = db.Column(db.Numeric(20, 2), nullable=False)
    admin =  db.Column(db.Boolean, default=False, nullable=False)
    term = db.Column(db.Numeric(20, 2), nullable=False)
    bond = db.Column(db.Numeric(20, 2), nullable=False)
    total = db.Column(db.Numeric(20, 2), nullable=False)
    send_tr = db.relationship('Transactions', backref='sender', lazy=True)
    receive_tr = db.relationship('Transactions', backref='receiver', lazy=True)
    terms = db.relationship('Term', secondary=terms, lazy='dynamic', backref=db.backref('owners', lazy=True))
    bonds = db.relationship('Bond', secondary=bonds, lazy='dynamic', backref=db.backref('owners', lazy=True))
    buys = db.relationship('Bond', secondary=buys, lazy='dynamic', backref=db.backref('buyers', lazy=True))
    sells = db.relationship('Bond', secondary=sells, lazy='dynamic', backref=db.backref('sellers', lazy=True))

    def __repr__(self):
        return f"User('{self.username}', '{self.total}')"

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    note = db.Column(db.String(30), nullable=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    t_trasaction = db.Column(db.Boolean, default=False, nullable=False)
    b_transaction = db.Column(db.Boolean, default=False, nullable=False)  


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




if __name__ == '__main__':
    app.run(debug=True)