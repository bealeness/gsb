from gsb import db
from flask import Blueprint, render_template, flash, redirect, url_for, abort
from gsb.term.forms import TermProducts, WithdrawTerm
from gsb.models import User, Term, Receives, Sends, Terms
from flask_login import current_user, login_required

term = Blueprint('term', __name__)

@term.route('/myterm', methods=['GET', 'POST'])
@login_required
def my_term():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    form = WithdrawTerm()
    if form.validate_on_submit():
        if current_user.term < form.amount.data:
            flash('You do not have that amount in term. Enter another amount.', 'danger')
            return redirect(url_for('term.term_products'))
        current_user.cash=current_user.cash+form.amount.data
        current_user.term=current_user.term-form.amount.data
        current_user.total=current_user.cash+current_user.term
        #show up in MyTerm
        receives = Receives(amount=form.amount.data, t_transaction=True, receiver_id=current_user.id, 
                        balance=current_user.term, sender=1000010000, note='Term withdrawl')
        #show up in MyPersonal
        receive = Receives(amount=form.amount.data, t_transaction=False, receiver_id=current_user.id,
                        balance=current_user.cash, sender=1000010000, note='Term withdrawl')
        #remove term ownership
        term = Term.query.filter_by(name=form.product.data).first()
        db.session.query(Terms).filter(Terms.user_id == current_user.id).filter(Terms.term_id == term.id).\
                    update({"balance": (Terms.balance-form.amount.data)})
        Terms.query.filter_by(balance=0.00).delete()
        db.session.add(receives)
        db.session.add(receive)
        db.session.commit()
        flash('Your withdrawal was successful', 'primary')
        return redirect(url_for('term.my_term'))
    sends = Sends.query.filter_by(sender_id=user, t_transaction=True).order_by(Sends.timestamp.desc()).all()
    receives = Receives.query.filter_by(receiver_id=user, t_transaction=True).order_by(Receives.timestamp.desc()).all()
    if current_user.admin == True:
        sends = Sends.query.filter_by(t_transaction=True).order_by(Sends.timestamp.desc()).all()
        receives = Receives.query.filter_by(t_transaction=True).order_by(Receives.timestamp.desc()).all()
    return render_template('my_term.html', title='MyTerm', personal=personal, sends=sends, form=form, receives=receives)


@term.route('/termproducts', methods=['GET', 'POST'])
@login_required
def term_products():
    form = TermProducts()
    if form.validate_on_submit():
        if current_user.cash < form.amount.data:
            flash('You do not have enough funds for this deposit. Enter another amount.', 'danger')
            return redirect(url_for('term.term_products'))
        current_user.cash=current_user.cash-form.amount.data
        current_user.term=current_user.term+form.amount.data
        current_user.total=current_user.cash+current_user.term
        #show up in MyTerm
        sends = Sends(amount=form.amount.data, t_transaction=True, receiver=1000010000, 
                        balance=current_user.term, sender_id=current_user.id, note='Term deposit')
        #show up in MyPersonal
        send = Sends(amount=form.amount.data, t_transaction=False, receiver=1000010000,
                        balance=current_user.cash, sender_id=current_user.id, note='Term deposit')
        #add term ownership
        term = Term.query.filter_by(name=form.product.data).first()
        terms = Terms(user_id=current_user.id, term_id=term.id, balance=form.amount.data)
        db.session.add(sends)
        db.session.add(send)
        db.session.add(terms)
        db.session.commit()
        flash('Your cash has been deposited', 'primary')
        return redirect(url_for('term.term_products'))
    stock = Term.query.order_by(Term.id).all()
    return render_template('term_products.html', title='TermProducts', form=form, stock=stock)


@term.route('/deposit/<int:send_id>')
@login_required
def deposit(send_id):
    deposit = Sends.query.get_or_404(send_id)
    if current_user.admin != True:
        if deposit.sender != current_user:
            abort(403)
    return render_template('deposit.html', title=deposit.id, deposit=deposit)


@term.route('/withdraw/<int:receive_id>')
@login_required
def withdraw(receive_id):
    withdraw = Receives.query.get_or_404(receive_id)
    if current_user.admin != True:
        if withdraw.receiver != current_user:
            abort(403)
    return render_template('withdraw.html', title=withdraw.id, withdraw=withdraw)