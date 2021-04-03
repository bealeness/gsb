from gsb import db
from flask import Blueprint, render_template, flash, redirect, url_for
from gsb.bond.forms import BuyBond, SellBond
from gsb.models import User, Bond
from flask_login import current_user, login_required


bond = Blueprint('bond', __name__)


@bond.route('/mybond', methods=['GET'])
@login_required
def my_bond():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    return render_template('my_bond.html', title='MyBond', personal=personal)


@bond.route('/buybond', methods=['GET'])
@login_required
def buy_bond():
    form = BuyBond()
    return render_template('buy_bond.html', title='BuyBond', form=form)


@bond.route('/sellbond', methods=['GET'])
@login_required
def sell_bond():
    form = SellBond()
    return render_template('sell_bond.html', title='SellBond', form=form)


@bond.route('/bondmarket', methods=['GET'])
@login_required
def bond_market():
    stock = Bond.query.order_by(Bond.id).all()
    return render_template('bond_market.html', title='BondMarket', stock=stock)
