from gsb import db
from flask import Blueprint, render_template, flash, redirect, url_for, abort
from gsb.admin.forms import CreateTermProduct, CreateBond, CashOut, TermCashOut, MarketForm
from gsb.models import Term, Bond, User, Bonds, Sells, Terms, Buys, Sends, Receives
from flask_login import current_user, login_required


admin = Blueprint('admin', __name__)


@admin.route('/adminterm', methods=['GET', 'POST'])
@login_required
def admin_term():
    if current_user.admin != True:
        abort(403)
    form = CreateTermProduct()
    if form.validate_on_submit():
        terms = Term(name=form.name.data, maturity=form.maturity.data, rate=form.rate.data, info=form.info.data)
        db.session.add(terms)
        db.session.commit()
        flash('Term created', 'primary')
        return redirect(url_for('admin.admin_term'))
    stock = Term.query.order_by(Term.id).all()
    owners = Terms.query.order_by(Terms.user_id).all()
    return render_template('admin/adminterm.html', title='AdminTerm', form=form, stock=stock, owners=owners)


@admin.route('/adminbond', methods=['GET', 'POST'])
@login_required
def admin_bond():
    if current_user.admin != True:
        abort(403)
    form = CreateBond()
    if form.validate_on_submit():
        bonds = Bond(name=form.name.data, ref_num=form.ref_num.data, maturity=form.maturity.data,
                rate= form.rate.data, face_value=form.face_value.data, quantity=form.quantity.data,
                info=form.info.data)
        db.session.add(bonds)
        db.session.commit()
        bond = Bond.query.filter_by(name=form.name.data).first()
        owns = Bonds(user_id=current_user.id, bond_id=bond.id, quantity=form.quantity.data)
        db.session.add(owns)
        db.session.commit()
        sells = Sells(user_id=current_user.id, bond_id=bond.id, quantity=form.quantity.data, offer=form.face_value.data,
                        rate=bond.rate, yd=bond.rate)
        db.session.add(sells)
        db.session.commit()
        flash('Bond created', 'primary')
        return redirect(url_for('admin.admin_bond'))
    stock = Bond.query.order_by(Bond.id).all()
    owners = Bonds.query.order_by(Bonds.user_id).all()
    buys = Buys.query.order_by(Buys.user_id).all()
    sells = Sells.query.order_by(Sells.user_id).all()
    return render_template('admin/adminbond.html', title='AdminBond', form=form, stock=stock, owners=owners, buys=buys, sells=sells)


@admin.route('/adminusers', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.admin != True:
        abort(403)
    users = User.query.order_by(User.id).all()
    return render_template('admin/adminusers.html', title='AdminUsers', users=users)


@admin.route('/user/<int:user_id>')
def user(user_id):
    if current_user.admin != True:
        abort(403)
    user = User.query.get_or_404(user_id)
    return render_template('admin/user.html', title=user.id, user=user)


@admin.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.admin != True:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('The user has been deleted.', 'primary')
    return redirect(url_for('admin.admin_users'))


@admin.route('/adminbond/delete_buys', methods=['POST'])
@login_required
def delete_buys():
    if current_user.admin != True:
        abort(403)
    db.session.query(Buys).delete()
    db.session.commit()
    flash('All buy orders have been deleted.', 'primary')
    return redirect(url_for('admin.admin_bond'))


@admin.route('/adminbond/delete_sells', methods=['POST'])
@login_required
def delete_sells():
    if current_user.admin != True:
        abort(403)
    db.session.query(Sells).delete()
    db.session.commit()
    flash('All sell orders have been deleted.', 'primary')
    return redirect(url_for('admin.admin_bond'))


@admin.route('/admintransactions', methods=['GET'])
@login_required
def user_transactions():
    if current_user.admin != True:
        abort(403)
    receives = Receives.query.filter_by(t_transaction=False, b_transaction=False).order_by(Receives.timestamp.desc()).all()
    sends = Sends.query.filter_by(t_transaction=False, b_transaction=False).order_by(Sends.timestamp.desc()).all()
    return render_template('admin/user_transactions.html', title='AdminTransactions', receives=receives, sends=sends)



@admin.route('/bondowner', methods=['GET', 'POST'])
def bond_owner():
    if current_user.admin != True:
        abort(403)
    form = CashOut()
    if form.validate_on_submit():
        if form.validate_on_submit():
            user = User.query.filter_by(id=form.user.data).first()
            user.bond=user.bond-form.quantity.data*1000
            user.total=user.cash+user.bond+user.term
            db.session.query(Bonds).filter(Bonds.user_id == form.user.data).filter(Bonds.bond_id == form.ref_num.data-100).\
                        update({"quantity": (Bonds.quantity-form.quantity.data)})
            Bonds.query.filter_by(quantity=0).delete()
            db.session.commit()
            flash('The user has been cashed out', 'primary')
            return redirect(url_for('admin.bond_owner'))
    owners = Bonds.query.order_by(Bonds.user_id).all()
    return render_template('admin/bondowner.html', title='BondOwners', owners=owners, form=form)


@admin.route('/adminproduct/<int:bond_id>')
@login_required
def admin_product(bond_id):
    bond = Bond.query.get_or_404(bond_id)
    return render_template('admin/adminproduct.html', title=bond_id, bond=bond)


@admin.route('/adminproduct/<int:bond_id>/delete', methods=['POST'])
@login_required
def delete_bond(bond_id):
    if current_user.admin != True:
        abort(403)
    bond = Bond.query.get_or_404(bond_id)
    db.session.delete(bond)
    db.session.commit()
    flash('The bond has been deleted.', 'primary')
    return redirect(url_for('admin.admin_bond'))


@admin.route('/termowner', methods=['GET', 'POST'])
def term_owner():
    if current_user.admin != True:
        abort(403)
    form = TermCashOut()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.user.data).first()
        user.term=user.term-form.balance.data
        user.total=user.cash+user.bond+user.term
        db.session.query(Terms).filter(Terms.user_id == form.user.data).filter(Terms.term_id == form.term_id.data).\
                    update({"balance": (Terms.balance-form.balance.data)})
        Terms.query.filter_by(balance=0.00).delete()
        db.session.commit()
        flash('The user has been cashed out', 'primary')
        return redirect(url_for('admin.term_owner'))
    owners = Terms.query.order_by(Terms.user_id).all()
    return render_template('admin/termowner.html', title='TermOwners', owners=owners, form=form)


@admin.route('/adminmarket', methods=['GET', 'POST'])
@login_required
def market():
    form = MarketForm()
    if form.validate_on_submit():
        user = User.query.all()
        if form.status.data == 'Open':
            db.session.query(User).update({ User.market: True})
            db.session.commit()
            flash('Market status has been changed', 'primary')
            return redirect(url_for('admin.market'))
        elif form.status.data == 'Close':
            db.session.query(User).update({ User.market: False})
            db.session.commit()
            flash('Market status has been changed', 'primary')
            return redirect(url_for('admin.market'))
    return render_template('admin/market.html', title='AdminMarket', form=form)
