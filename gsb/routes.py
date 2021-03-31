from gsb import app, db, bcrypt
from flask import render_template, flash, redirect, url_for
from gsb.forms import (RegistrationForm, LoginForm, PaySomeone, TermProducts, 
                    BuyBond, SellBond, UpdateAccountForm)
from gsb.models import User, Transactions, Term, Bond
from random import randint


@app.route('/', methods=['GET', 'POST'])
def home():
    form = LoginForm()
    return render_template("logged_out/gsb.html", title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        random = randint(1000000000, 9999999999)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                    account=random, cash='100000.00', term='0.00', bond='0.00', total='100000.00')
        if user.username == "GSB Bank":
            user.admin = True
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for { form.username.data }! You are now able to login.', 'success')
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

