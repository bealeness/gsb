from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField
from wtforms.validators import DataRequired


class TermProducts(FlaskForm):
    amount = DecimalField('Enter the amount you wish to deposit:', validators=[DataRequired()], places=2)
    submit = SubmitField('Deposit')

class WithdrawTerm(FlaskForm):
    amount = DecimalField('Enter the amount you wish to withdraw:', validators=[DataRequired()], places=2)
    submit = SubmitField('Withdraw')