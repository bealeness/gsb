from gsb import db
from flask import Blueprint, render_template, flash, redirect, url_for, abort
from gsb.admin.forms import CreateTermProduct, CreateBond
from gsb.models import Term, Bond
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
    return render_template('admin/adminterm.html', title='AdminTerm', form=form, stock=stock)


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
        flash('Bond created', 'primary')
        return redirect(url_for('admin.admin_bond'))
    stock = Bond.query.order_by(Bond.id).all()
    return render_template('admin/adminbond.html', title='AdminBond', form=form, stock=stock)

