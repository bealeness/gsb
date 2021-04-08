from gsb import db
from flask import Blueprint, render_template, flash, redirect, url_for, abort
from gsb.admin.forms import CreateTermProduct, CreateBond
from gsb.models import Term, Bond, User, Bonds, Sells, Terms, Buys
from flask_login import current_user, login_required


admin = Blueprint('admin', __name__)


@admin.route('/adminterm', methods=['GET', 'POST'])
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
                rate= form.rate.data, face_value=form.face_value.data, quantity=form.quantity.data)
        db.session.add(bonds)
        db.session.commit()
        bond = Bond.query.filter_by(name=form.name.data).first()
        owns = Bonds(user_id=current_user.id, bond_id=bond.id, quantity=form.quantity.data)
        db.session.add(owns)
        db.session.commit()
        sells = Sells(user_id=current_user.id, bond_id=bond.id, quantity=form.quantity.data, offer=form.face_value.data)
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
    return redirect(url_for('admin.admin_user'))


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