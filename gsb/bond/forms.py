from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, DecimalField
from wtforms.validators import DataRequired



class BuyBond(FlaskForm):
    ref_num = IntegerField('Enter the bond refernece number:', validators=[DataRequired()])
    price = DecimalField('Enter your bid price:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('Bid')


class SellBond(FlaskForm):
    ref_num = IntegerField('Enter the bond refernece number:', validators=[DataRequired()])
    price = DecimalField('Enter your offer price:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('Offer')