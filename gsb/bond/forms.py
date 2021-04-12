from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, DecimalField
from wtforms.validators import DataRequired



class BuyBond(FlaskForm):
    user = IntegerField('Enter the seller ID:', validators=[DataRequired()])
    ref_num = IntegerField('Enter the bond ID:', validators=[DataRequired()])
    price = DecimalField('Enter your bid price:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('Buy')

class NewBuy(FlaskForm):
    ref_num = IntegerField('Enter the bond ID:', validators=[DataRequired()])
    price = DecimalField('Enter your bid price:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('Bid')


class SellBond(FlaskForm):
    user = IntegerField('Enter the buyer ID:', validators=[DataRequired()])
    ref_num = IntegerField('Enter the bond ID:', validators=[DataRequired()])
    price = DecimalField('Enter your offer price:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('Sell')

class NewSell(FlaskForm):
    ref_num = IntegerField('Enter the bond ID:', validators=[DataRequired()])
    price = DecimalField('Enter your offer price:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('Offer')



