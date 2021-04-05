from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField, RadioField
from wtforms.validators import DataRequired

#choices need to be added as admin creates terms
class TermProducts(FlaskForm):
    product = RadioField('Term Product', choices=['The GSB Daily'], validators=[DataRequired()])
    amount = DecimalField('Enter the amount you wish to deposit:', validators=[DataRequired()], places=2)
    submit = SubmitField('Deposit')

#choices need to be added as admin creates terms
class WithdrawTerm(FlaskForm):
    product = RadioField('Term Product', choices=['The GSB Daily'], validators=[DataRequired()])
    amount = DecimalField('Enter the amount you wish to withdraw:', validators=[DataRequired()], places=2)
    submit = SubmitField('Withdraw')