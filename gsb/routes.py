from gsb import app, db, bcrypt
from flask import render_template, flash, redirect, url_for, request
from gsb.forms import (RegistrationForm, LoginForm, PaySomeone, TermProducts, 
                    BuyBond, SellBond, UpdateAccountForm, CreateTermProduct, CreateBond,
                    WithdrawTerm)
from gsb.models import User, Term, Bond, Receives, Sends
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
    receives = Receives.query.filter_by(receiver_id=user, t_transaction=False, b_transaction=False).order_by(Receives.timestamp.desc()).all()
    sends = Sends.query.filter_by(sender_id=user, t_transaction=False, b_transaction=False).order_by(Sends.timestamp.desc()).all()
    if current_user.admin == True:
        receives = Receives.query.order_by(Receives.timestamp.desc()).all()
        sends = Sends.query.order_by(Sends.timestamp.desc()).all()
    return render_template('my_personal.html', title='MyPersonal', personal=personal, user=user, receives=receives, sends=sends)


@app.route('/paysomeone', methods=['GET', 'POST'])
@login_required
def pay_someone():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    form = PaySomeone()
    if form.validate_on_submit():
        receiver = User.query.filter_by(account=form.receiver.data).first()
        if current_user.cash < form.amount.data:
            flash('You do not have enough funds for this payment. Enter another amount.', 'danger')
            return redirect(url_for('pay_someone'))
        current_user.cash=current_user.cash-form.amount.data
        current_user.total=current_user.total-form.amount.data
        receiver.cash=receiver.cash+form.amount.data
        receiver.total=receiver.total+form.amount.data
        receives = Receives(receiver_id=receiver.id, note=form.note.data,
                                    amount=form.amount.data, sender=current_user.account,
                                    balance=receiver.cash)
        sends = Sends(sender_id=user, note=form.note.data,
                                    amount=form.amount.data, receiver=receiver.account,
                                    balance=current_user.cash)
        db.session.add(receives)
        db.session.add(sends)
        db.session.commit()
        flash('Your payment has been sent!', 'primary')
        return redirect(url_for('my_personal'))
    return render_template('pay_someone.html', title='PaySomeone', form=form, user=user, personal=personal)


@app.route('/myterm', methods=['GET', 'POST'])
@login_required
def my_term():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    form = WithdrawTerm()
    if form.validate_on_submit():
        if current_user.term < form.amount.data:
            flash('You do not have that amount in term. Enter another amount.', 'danger')
            return redirect(url_for('term_products'))
        current_user.cash=current_user.cash+form.amount.data
        current_user.term=current_user.term-form.amount.data
        current_user.total=current_user.cash+current_user.term
        #show up in MyTerm
        receives = Receives(amount=form.amount.data, t_transaction=True, receiver_id=current_user.id, 
                        balance=current_user.term, sender=1000010000)
        #show up in MyPersonal
        receive = Receives(amount=form.amount.data, t_transaction=False, receiver_id=current_user.id,
                        balance=current_user.cash, sender=1000010000)
        db.session.add(receives)
        db.session.add(receive)
        db.session.commit()
        flash('Your withdrawal was successful', 'primary')
        return redirect(url_for('my_term'))
    sends = Sends.query.filter_by(sender_id=user, t_transaction=True).order_by(Sends.timestamp.desc()).all()
    receives = Receives.query.filter_by(receiver_id=user, t_transaction=True).order_by(Receives.timestamp.desc()).all()
    return render_template('my_term.html', title='MyTerm', personal=personal, sends=sends, form=form, receives=receives)


@app.route('/adminterm', methods=['GET', 'POST'])
@login_required
def admin_term():
    if current_user.admin != True:
        abort(403)
    form = CreateTermProduct()
    if form.validate_on_submit():
        terms = Term(name=form.name.data, maturity=form.maturity.data, rate=form.rate.data)
        db.session.add(terms)
        db.session.commit()
        flash('Term created', 'primary')
    stock = Term.query.order_by(Term.id).all()
    return render_template('admin/adminterm.html', title='AdminTerm', form=form, stock=stock)


@app.route('/termproducts', methods=['GET', 'POST'])
@login_required
def term_products():
    form = TermProducts()
    if form.validate_on_submit():
        if current_user.cash < form.amount.data:
            flash('You do not have enough funds for this deposit. Enter another amount.', 'danger')
            return redirect(url_for('term_products'))
        current_user.cash=current_user.cash-form.amount.data
        current_user.term=current_user.term+form.amount.data
        current_user.total=current_user.cash+current_user.term
        #show up in MyTerm
        sends = Sends(amount=form.amount.data, t_transaction=True, receiver=1000010000, 
                        balance=current_user.term, sender_id=current_user.id)
        #show up in MyPersonal
        send = Sends(amount=form.amount.data, t_transaction=False, receiver=1000010000,
                        balance=current_user.cash, sender_id=current_user.id)
        db.session.add(sends)
        db.session.add(send)
        db.session.commit()
        flash('Your cash has been deposited', 'primary')
        return redirect(url_for('term_products'))
    stock = Term.query.order_by(Term.id).all()
    return render_template('term_products.html', title='TermProducts', form=form, stock=stock)


@app.route('/mybond', methods=['GET'])
@login_required
def my_bond():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    return render_template('my_bond.html', title='MyBond', personal=personal)


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
    stock = Bond.query.order_by(Bond.id).all()
    return render_template('bond_market.html', title='BondMarket', stock=stock)


@app.route('/adminbond', methods=['GET', 'POST'])
@login_required
def admin_bond():
    if current_user.admin != True:
        abort(403)
    form = CreateBond()
    if form.validate_on_submit():
        bonds = Bond(name=form.name.data, ref_num=form.ref_num.data, maturity=form.maturity.data,
                rate= form.rate.data, face_value=form.face_value.data, quantity=form.quantity.data)
        db.session.add(bonds)
        db.session.commit()
        flash('Bond created', 'primary')
        return redirect(url_for('admin_bond'))
    stock = Bond.query.order_by(Bond.id).all()
    return render_template('admin/adminbond.html', title='AdminBond', form=form, stock=stock)

@app.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    users = User.query.filter_by(admin=False).order_by(User.cash.desc()).all()
    return render_template('leaderboard.html', title='Leaderboard', users=users, count=1)


@app.route('/accountsettings', methods=['GET', 'POST'])
@login_required
def account_settings():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.image.data == 'Midway Sunrise':
            current_user.image=1
        elif form.image.data == 'Town':
            current_user.image=2
        elif form.image.data == 'Bomb Bridge':
            current_user.image=3
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'primary')
        return redirect(url_for('account_settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.image.data = current_user.image
    return render_template('account_settings.html', title='AccountSettings', form=form, personal=personal)

