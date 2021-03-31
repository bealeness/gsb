from gsb import app, db, bcrypt
from flask import render_template, flash, redirect, url_for, request
from gsb.forms import (RegistrationForm, LoginForm, PaySomeone, TermProducts, 
                    BuyBond, SellBond, UpdateAccountForm)
from gsb.models import User, Term, Bond, transactions
from random import randint
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('my_personal'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('my_personal'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template("logged_out/gsb.html", title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'primary')
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('my_personal'))
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


@app.route('/mypersonal', methods=['GET'])
@login_required
def my_personal():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    return render_template('my_personal.html', title='MyPersonal', personal=personal, user=user)


@app.route('/paysomeone', methods=['GET', 'POST'])
@login_required
def pay_someone():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    form = PaySomeone()
    if form.validate_on_submit():
        receiver = User.query.filter_by(account=form.receiver.data).first()
        if receiver.cash < form.amount.data:
            flash('You do not have enough funds for this payment. Enter another amount.', 'danger')
            return redirect(url_for('pay_someone'))
        current_user.cash=current_user.cash-form.amount.data
        receiver.cash=receiver.cash+form.amount.data
        #You have to make the transactions work
        db.session.commit()
        flash('Your payment has been sent!', 'primary')
        return redirect(url_for('my_personal'))
    return render_template('pay_someone.html', title='PaySomeone', form=form, user=user, personal=personal)


@app.route('/myterm', methods=['GET'])
@login_required
def my_term():
    return render_template('my_term.html', title='MyTerm')


@app.route('/termproducts', methods=['GET', 'POST'])
@login_required
def term_products():
    form = TermProducts()
    return render_template('term_products.html', title='TermProducts', form=form)


@app.route('/mybond', methods=['GET'])
@login_required
def my_bond():
    return render_template('my_bond.html', title='MyBond')


@app.route('/buybond', methods=['GET'])
@login_required
def buy_bond():
    form = BuyBond()
    return render_template('buy_bond.html', title='BuyBond', form=form)


@app.route('/sellbond', methods=['GET'])
@login_required
def sell_bond():
    form = SellBond()
    return render_template('sell_bond.html', title='SellBond', form=form)


@app.route('/bondmarket', methods=['GET'])
@login_required
def bond_market():
    return render_template('bond_market.html', title='BondMarket')


@app.route('/leaderboard', methods=['GET'])
@login_required
def leaderboard():
    return render_template('leaderboard.html', title='Leaderboard')


@app.route('/accountsettings', methods=['GET'])
@login_required
def account_settings():
    form = UpdateAccountForm()
    return render_template('account_settings.html', title='AccountSettings', form=form)

