from gsb import db, bcrypt
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from gsb.main.forms import RegistrationForm, LoginForm, PaySomeone, UpdateAccountForm
from gsb.models import User, Receives, Sends
from random import randint
from flask_login import login_user, current_user, logout_user, login_required


main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.my_personal'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.my_personal'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template("logged_out/gsb.html", title='Sign In', form=form)


@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'primary')
    return redirect(url_for('main.home'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.my_personal'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        random = randint(1000000000, 9999999999)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                    account=random, cash='100000.00', term='0.00', bond='0.00', total='100000.00')
        if user.username == "GSB Bank":
            user.admin = True
        if user.username == "GSB Bank":
            user.cash = '1000000.00'
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for { form.username.data }! You are now able to login.', 'success')
        return redirect(url_for('main.home'))
    return render_template("logged_out/register.html", title='Register', form=form)


@main.route('/mypersonal', methods=['GET'])
@login_required
def my_personal():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    receives = Receives.query.filter_by(receiver_id=user, t_transaction=False, b_transaction=False).order_by(Receives.timestamp.desc()).all()
    sends = Sends.query.filter_by(sender_id=user, t_transaction=False, b_transaction=False).order_by(Sends.timestamp.desc()).all()
    if current_user.admin == True:
        receives = Receives.query.filter_by(t_transaction=False).order_by(Receives.timestamp.desc()).all()
        sends = Sends.query.filter_by(t_transaction=False).order_by(Sends.timestamp.desc()).all()
    return render_template('my_personal.html', title='MyPersonal', personal=personal, user=user, receives=receives, sends=sends)


@main.route('/paysomeone', methods=['GET', 'POST'])
@login_required
def pay_someone():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    form = PaySomeone()
    if form.validate_on_submit():
        receiver = User.query.filter_by(account=form.receiver.data).first()
        if receiver is None:
            flash('That account does not exist. Enter another account.', 'danger')
            return redirect(url_for('main.pay_someone'))
        if current_user.cash < form.amount.data:
            flash('You do not have enough funds for this payment. Enter another amount.', 'danger')
            return redirect(url_for('main.pay_someone'))
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
        return redirect(url_for('main.my_personal'))
    return render_template('pay_someone.html', title='PaySomeone', form=form, user=user, personal=personal)


@main.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    users = User.query.filter_by(admin=False).order_by(User.cash.desc()).all()
    return render_template('leaderboard.html', title='Leaderboard', users=users)


@main.route('/accountsettings', methods=['GET', 'POST'])
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
        return redirect(url_for('main.account_settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.image.data = current_user.image
    return render_template('account_settings.html', title='AccountSettings', form=form, personal=personal)


@main.route('/send/<int:send_id>')
@login_required
def send(send_id):
    send = Sends.query.get_or_404(send_id)
    if current_user.admin != True:
        if send.sender != current_user:
            abort(403)
    return render_template('send.html', title=send.id, send=send)


@main.route('/receive/<int:receive_id>')
@login_required
def receive(receive_id):
    receive = Receives.query.get_or_404(receive_id)
    if current_user.admin != True:
        if receive.receiver != current_user:
            abort(403)
    return render_template('receive.html', title=receive.id, receive=receive)