from gsb import db
from flask import Blueprint, render_template, flash, redirect, url_for, abort
from gsb.term.forms import TermProducts
from gsb.models import User, Term, Receives, Sends, Terms
from flask_login import current_user, login_required

term = Blueprint('term', __name__)

@term.route('/myterm', methods=['GET', 'POST'])
@login_required
def my_term():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    sends = Sends.query.filter_by(sender_id=user, t_transaction=True).order_by(Sends.timestamp.desc()).all()
    receives = Receives.query.filter_by(receiver_id=user, t_transaction=True).order_by(Receives.timestamp.desc()).all()
    terms = Terms.query.filter_by(user_id=user).all()
    if current_user.admin == True:
        sends = Sends.query.filter_by(t_transaction=True).order_by(Sends.timestamp.desc()).all()
        receives = Receives.query.filter_by(t_transaction=True).order_by(Receives.timestamp.desc()).all()
    return render_template('terms/my_term.html', title='MyTerm', personal=personal, sends=sends, receives=receives, terms=terms)


@term.route('/termproducts', methods=['GET', 'POST'])
@login_required
def term_products():
    form = TermProducts()
    bank = User.query.filter_by(admin=True).first()
    if form.validate_on_submit():
        if current_user.cash < form.amount.data:
            flash('You do not have enough funds for this deposit. Enter another amount.', 'danger')
            return redirect(url_for('term.term_products'))
        elif form.product.data == 'The GSB 10':
            if form.amount.data < 10000.00:
                flash('The minimum deposit for The GSB 10 is $10,000. Enter a higher amount.', 'danger')
                return redirect(url_for('term.term_products'))
        elif form.product.data == 'The GSB 20':
            if form.amount.data < 20000.00:
                flash('The minimum deposit for The GSB 20 is $20,000. Enter a higher amount.', 'danger')
                return redirect(url_for('term.term_products'))
        elif form.product.data == 'The GSB 50':
            if form.amount.data < 50000.00:
                flash('The minimum deposit for The GSB 50 is $50,000. Enter a higher amount.', 'danger')
                return redirect(url_for('term.term_products'))
        current_user.cash=current_user.cash-form.amount.data
        current_user.term=current_user.term+form.amount.data
        current_user.total=current_user.cash+current_user.term+current_user.bond
        bank.cash=bank.cash+form.amount.data
        #show up in MyTerm
        sends = Sends(amount=form.amount.data, t_transaction=True, receiver=bank.account, 
                        balance=current_user.term, sender_id=current_user.id, note='Term deposit')
        #show up in MyPersonal
        send = Sends(amount=form.amount.data, t_transaction=False, receiver=bank.account,
                        balance=current_user.cash, sender_id=current_user.id, note='Term deposit')
        #show up in banks MyTerm
        receives = Receives(amount=form.amount.data, t_transaction=True, receiver_id=bank.id, 
                        balance=current_user.term, sender=current_user.account, note='Term deposit')
        #show up in banks MyPersonal
        receive = Receives(amount=form.amount.data, t_transaction=False, receiver_id=bank.id,
                        balance=current_user.cash, sender=current_user.account, note='Term deposit')
        #add term ownership
        term = Term.query.filter_by(name=form.product.data).first()
        has = Terms.query.filter_by(user_id=current_user.id).filter_by(term_id=term.id).first()
        if not has:
            terms = Terms(user_id=current_user.id, term_id=term.id, balance=form.amount.data)
            db.session.add(sends)
            db.session.add(send)
            db.session.add(receive)
            db.session.add(receives)
            db.session.add(terms)
            db.session.commit()
            flash('Your cash has been deposited', 'primary')
            return redirect(url_for('term.term_products'))
        elif has:
            db.session.query(Terms).filter(Terms.user_id == current_user.id).filter(Terms.term_id == term.id).\
                    update({"balance": (Terms.balance+form.amount.data)})
            db.session.add(sends)
            db.session.add(send)
            db.session.add(receives)
            db.session.add(receive)
            db.session.commit()
            flash('Your term balance has been updated', 'primary')
            return redirect(url_for('term.term_products'))
    stock = Term.query.order_by(Term.id).all()
    return render_template('terms/term_products.html', title='TermProducts', form=form, stock=stock)


@term.route('/deposit/<int:send_id>')
@login_required
def deposit(send_id):
    deposit = Sends.query.get_or_404(send_id)
    if current_user.admin != True:
        if deposit.sender != current_user:
            abort(403)
    return render_template('terms/deposit.html', title=deposit.id, deposit=deposit)


@term.route('/withdraw/<int:receive_id>')
@login_required
def withdraw(receive_id):
    withdraw = Receives.query.get_or_404(receive_id)
    if current_user.admin != True:
        if withdraw.receiver != current_user:
            abort(403)
    return render_template('terms/withdraw.html', title=withdraw.id, withdraw=withdraw)


@term.route('/product/<int:term_id>')
@login_required
def product(term_id):
    product = Term.query.get_or_404(term_id)
    return render_template('terms/product.html', title=product.id, product=product)