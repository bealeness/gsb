from gsb import db
from flask import Blueprint, render_template, flash, redirect, url_for, abort
from gsb.bond.forms import BuyBond, SellBond, NewBuy, NewSell
from gsb.models import User, Bond, Sells, Sends, Receives, Bonds, Buys
from flask_login import current_user, login_required


bond = Blueprint('bond', __name__)


@bond.route('/mybond', methods=['GET'])
@login_required
def my_bond():
    user = current_user.id
    personal = User.query.filter_by(id=user).first_or_404()
    bonds = Bonds.query.filter_by(user_id=user).all()
    sends = Sends.query.filter_by(sender_id=user, b_transaction=True).order_by(Sends.timestamp.desc()).all()
    receives = Receives.query.filter_by(receiver_id=user, b_transaction=True).order_by(Receives.timestamp.desc()).all()
    buys = Buys.query.filter_by(user_id=user).order_by(Buys.bond_id).all()
    sells = Sells.query.filter_by(user_id=user).order_by(Sells.bond_id).all()
    if current_user.admin == True:
        sends = Sends.query.filter_by(b_transaction=True).order_by(Sends.timestamp.desc()).all()
        receives = Receives.query.filter_by(b_transaction=True).order_by(Receives.timestamp.desc()).all()
    return render_template('bonds/my_bond.html', title='MyBond', personal=personal, sends=sends, receives=receives, bonds=bonds, buys=buys, sells=sells)


@bond.route('/buybond', methods=['GET', 'POST'])
@login_required
def buy_bond():
    form = BuyBond()
    if form.validate_on_submit():
        bond = Sells.query.filter_by(bond_id=form.ref_num.data-100).first()
        seller = User.query.filter_by(id=form.user.data).first()
        if current_user.cash < form.price.data*form.quantity.data:
            flash('You do not have enough cash for this order. Enter different price or quantity amounts.', 'danger')
            return redirect(url_for('bond.buy_bond'))
        elif form.quantity.data > bond.quantity:
            flash('That is a higher quantity than what is available. Enter a lower quantity.', 'danger')
            return redirect(url_for('bond.buy_bond'))
        elif form.price.data < bond.offer:
            bond = Bond.query.filter_by(id=form.ref_num.data-100).first()
            has = Buys.query.filter_by(user_id=current_user.id).filter_by(bond_id=bond.id).first()
            if not has:
                buys = Buys(user_id=current_user.id, bond_id=form.ref_num.data-100, quantity=form.quantity.data, 
                            bid=form.price.data, yd=(bond.rate*1000)/form.price.data)
                db.session.add(buys)
                db.session.commit()
                flash('Your buy order has been placed', 'primary')
                return redirect(url_for('bond.buy_bond'))
            elif has:
                db.session.query(Buys).filter(Buys.user_id == current_user.id).filter(Buys.bond_id == bond.id).\
                    update({"quantity": (Buys.quantity+form.quantity.data)})
                db.session.commit()
                flash('Your buy order has been placed', 'primary')
                return redirect(url_for('bond.buy_bond'))
        elif form.price.data >= bond.offer:
            current_user.cash=current_user.cash-(form.price.data*form.quantity.data)
            current_user.bond=current_user.bond+(form.price.data*form.quantity.data)
            current_user.total=current_user.cash+current_user.bond+current_user.term
            seller.cash=seller.cash+(form.price.data*form.quantity.data)
            seller.bond=seller.bond-(form.price.data*form.quantity.data)
            seller.total=seller.cash+seller.bond+seller.term
            #show up in MyBond
            sends = Sends(amount=form.price.data*form.quantity.data, b_transaction=True, receiver=seller.account, 
                            balance=current_user.bond, sender_id=current_user.id, note='Bond purchase')
            #show up in senders MyBond
            receives = Receives(amount=form.price.data*form.quantity.data, b_transaction=True, sender=current_user.account, 
                            balance=seller.bond, receiver_id=seller.id, note='Bond sale')
            #show up in MyPersonal
            send = Sends(amount=form.price.data*form.quantity.data, b_transaction=False, receiver=seller.account,
                            balance=current_user.cash, sender_id=current_user.id, note='Bond purchase')
            #show up in senders MyPersonal
            receive = Receives(amount=form.price.data*form.quantity.data, b_transaction=False, sender=current_user.account, 
                            balance=seller.cash, receiver_id=seller.id, note='Bond sale')
            #add bond ownership to buyer
            bond = Bond.query.filter_by(id=form.ref_num.data-100).first()
            has = Bonds.query.filter_by(user_id=current_user.id).filter_by(bond_id=bond.id).first()
            if not has:
                bonds = Bonds(user_id=current_user.id, bond_id=bond.id, quantity=form.quantity.data)
                db.session.query(Bonds).filter(Bonds.user_id == seller.id).filter(Bonds.bond_id == bond.id).\
                    update({"quantity": (Bonds.quantity-form.quantity.data)})
                db.session.query(Sells).filter(Sells.user_id == seller.id).filter(Sells.bond_id == bond.id).\
                    update({"quantity": (Sells.quantity-form.quantity.data)})
                Bonds.query.filter_by(quantity=0).delete()
                Sells.query.filter_by(quantity=0).delete()
                db.session.add(sends)
                db.session.add(receives)
                db.session.add(send)
                db.session.add(receive)
                db.session.add(bonds)
                db.session.commit()
                flash('Your buy order has been executed!', 'primary')
                return redirect(url_for('bond.buy_bond'))
            elif has:
                db.session.query(Bonds).filter(Bonds.user_id == current_user.id).filter(Bonds.bond_id == bond.id).\
                    update({"quantity": (Bonds.quantity+form.quantity.data)})
                db.session.query(Bonds).filter(Bonds.user_id == seller.id).filter(Bonds.bond_id == bond.id).\
                    update({"quantity": (Bonds.quantity-form.quantity.data)})
                db.session.query(Sells).filter(Sells.user_id == seller.id).filter(Sells.bond_id == bond.id).\
                    update({"quantity": (Sells.quantity-form.quantity.data)})
                Bonds.query.filter_by(quantity=0).delete()
                Sells.query.filter_by(quantity=0).delete()
                db.session.add(sends)
                db.session.add(receives)
                db.session.add(send)
                db.session.add(receive)
                db.session.commit()
                flash('Your buy order has been executed!', 'primary')
                return redirect(url_for('bond.buy_bond'))
    sells = Sells.query.order_by(Sells.quantity.desc()).all()
    return render_template('bonds/buy_bond.html', title='BuyBond', form=form, sells=sells)


@bond.route('/sellbond', methods=['GET', 'POST'])
@login_required
def sell_bond():
    form = SellBond()
    if form.validate_on_submit():
        bond = Buys.query.filter_by(bond_id=form.ref_num.data-100).first()
        buyer = User.query.filter_by(id=form.user.data).first()
        if form.quantity.data > bond.quantity:
            flash('You are trying to sell too great a quantity. Enter a lower quantity.', 'danger')
            return redirect(url_for('bond.sell_bond'))
        elif form.price.data > bond.bid:
            bond = Bond.query.filter_by(id=form.ref_num.data-100).first()
            has = Sells.query.filter_by(user_id=current_user.id).filter_by(bond_id=bond.id).first()
            if not has:
                sells = Sells(user_id=current_user.id, bond_id=form.ref_num.data-100, quantity=form.quantity.data, 
                                offer=form.price.data, yd=(bond.rate*1000)/form.price.data)
                db.session.add(sells)
                db.session.commit()
                flash('Your sell order has been placed', 'primary')
                return redirect(url_for('bond.sell_bond'))
            elif has:
                db.session.query(Sells).filter(Sells.user_id == current_user.id).filter(Sells.bond_id == bond.id).\
                    update({"quantity": (Sells.quantity+form.quantity.data)})
                db.session.commit()
                flash('Your sell order has been placed', 'primary')
                return redirect(url_for('bond.sell_bond'))
        elif form.price.data <= bond.bid:
            current_user.cash=current_user.cash+(form.price.data*form.quantity.data)
            current_user.bond=current_user.bond-(form.price.data*form.quantity.data)
            current_user.total=current_user.cash+current_user.bond+current_user.term
            buyer.cash=buyer.cash-(form.price.data*form.quantity.data)
            buyer.bond=buyer.bond+(form.price.data*form.quantity.data)
            buyer.total=buyer.cash+buyer.bond+buyer.term
            #show up in MyBond
            receives = Receives(amount=form.price.data*form.quantity.data, b_transaction=True, receiver_id=current_user.id, 
                            balance=current_user.bond, sender=buyer.account, note='Bond sale')
            #show up in receivers MyBond
            sends = Sends(amount=form.price.data*form.quantity.data, b_transaction=True, sender_id=buyer.id, 
                            balance=buyer.bond, receiver=current_user.account, note='Bond purchase')
            #show up in MyPersonal
            receive = Receives(amount=form.price.data*form.quantity.data, b_transaction=False, receiver_id=current_user.id,
                            balance=current_user.cash, sender=buyer.account, note='Bond sale')
            #show up in receivers MyPersonal
            send = Sends(amount=form.price.data*form.quantity.data, b_transaction=False, sender_id=buyer.id, 
                            balance=buyer.cash, receiver=current_user.account, note='Bond purchase')
            #add bond ownership to buyer
            bond = Bond.query.filter_by(id=form.ref_num.data-100).first()
            has = Bonds.query.filter_by(user_id=buyer.id).filter_by(bond_id=bond.id).first()
            if not has:
                bonds = Bonds(user_id=buyer.id, bond_id=bond.id, quantity=form.quantity.data)
                db.session.query(Bonds).filter(Bonds.user_id == current_user.id).filter(Bonds.bond_id == bond.id).\
                    update({"quantity": (Bonds.quantity-form.quantity.data)})
                db.session.query(Buys).filter(Buys.user_id == buyer.id).filter(Buys.bond_id == bond.id).\
                    update({"quantity": (Buys.quantity-form.quantity.data)})
                Bonds.query.filter_by(quantity=0).delete()
                Buys.query.filter_by(quantity=0).delete()
                db.session.add(sends)
                db.session.add(receives)
                db.session.add(send)
                db.session.add(receive)
                db.session.add(bonds)
                db.session.commit()
                flash('Your sell order has been executed!', 'primary')
                return redirect(url_for('bond.sell_bond'))
            elif has:
                db.session.query(Bonds).filter(Bonds.user_id == buyer.id).filter(Bonds.bond_id == bond.id).\
                    update({"quantity": (Bonds.quantity+form.quantity.data)})
                db.session.query(Bonds).filter(Bonds.user_id == current_user.id).filter(Bonds.bond_id == bond.id).\
                    update({"quantity": (Bonds.quantity-form.quantity.data)})
                db.session.query(Buys).filter(Buys.user_id == buyer.id).filter(Buys.bond_id == bond.id).\
                    update({"quantity": (Buys.quantity-form.quantity.data)})
                Bonds.query.filter_by(quantity=0).delete()
                Buys.query.filter_by(quantity=0).delete()
                db.session.add(sends)
                db.session.add(receives)
                db.session.add(send)
                db.session.add(receive)
                db.session.commit()
                flash('Your sell order has been executed!', 'primary')
                return redirect(url_for('bond.sell_bond'))
    buys = Buys.query.order_by(Buys.quantity.desc()).all()
    return render_template('bonds/sell_bond.html', title='SellBond', form=form, buys=buys)


@bond.route('/bondmarket', methods=['GET'])
@login_required
def bond_market():
    stock = Bond.query.order_by(Bond.id).all()
    return render_template('bonds/bond_market.html', title='BondMarket', stock=stock)


@bond.route('/purchase/<int:send_id>')
@login_required
def purchase(send_id):
    purchase = Sends.query.get_or_404(send_id)
    if current_user.admin != True:
        if purchase.sender != current_user:
            abort(403)
    return render_template('bonds/purchase.html', title=purchase.id, purchase=purchase)


@bond.route('/sale/<int:receive_id>')
@login_required
def sale(receive_id):
    sale = Receives.query.get_or_404(receive_id)
    if current_user.admin != True:
        if sale.receiver != current_user:
            abort(403)
    return render_template('bonds/sale.html', title=sale.id, sale=sale)


@bond.route('/newbuy', methods=['GET', 'POST'])
@login_required
def new_buy():
    form = NewBuy()
    if form.validate_on_submit():
        bond = Bond.query.filter_by(id=form.ref_num.data-100).first()
        has = Buys.query.filter_by(user_id=current_user.id).filter_by(bond_id=bond.id).first()
        if not has:
            buys = Buys(user_id=current_user.id, bond_id=form.ref_num.data-100, 
                        quantity=form.quantity.data, bid=form.price.data, yd=(bond.rate*1000)/form.price.data)
            db.session.add(buys)
            db.session.commit()
            flash('Your buy order has been placed', 'primary')
            return redirect(url_for('bond.buy_bond'))
        elif has:
            db.session.query(Buys).filter(Buys.user_id == current_user.id).filter(Buys.bond_id == bond.id).\
                update({"quantity": (Buys.quantity+form.quantity.data)})
            db.session.commit()
            flash('Your buy order has been placed', 'primary')
            return redirect(url_for('bond.buy_bond'))
    sells = Sells.query.order_by(Sells.quantity.desc()).all()
    return render_template('bonds/new_buy.html', title=NewBuy, sells=sells, form=form)


@bond.route('/newsell', methods=['GET', 'POST'])
@login_required
def new_sell():
    form = NewSell()
    if form.validate_on_submit():
        bond = Bond.query.filter_by(id=form.ref_num.data-100).first()
        has = Sells.query.filter_by(user_id=current_user.id).filter_by(bond_id=bond.id).first()
        if not has:
            sells = Sells(user_id=current_user.id, bond_id=form.ref_num.data-100, 
                            quantity=form.quantity.data, offer=form.price.data, yd=(bond.rate*1000)/form.price.data)
            db.session.add(sells)
            db.session.commit()
            flash('Your sell order has been placed', 'primary')
            return redirect(url_for('bond.sell_bond'))
        elif has:
            db.session.query(Sells).filter(Sells.user_id == current_user.id).filter(Sells.bond_id == bond.id).\
                update({"quantity": (Sells.quantity+form.quantity.data)})
            db.session.commit()
            flash('Your sell order has been placed', 'primary')
            return redirect(url_for('bond.sell_bond'))
    buys = Buys.query.order_by(Buys.quantity.desc()).all()
    return render_template('bonds/new_sell.html', title=NewSell, buys=buys, form=form)


@bond.route('/bondproduct/<int:bond_id>')
@login_required
def bond_product(bond_id):
    bond = Bond.query.get_or_404(bond_id)
    return render_template('bonds/bond.html', title=bond_id, bond=bond)
