from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField, RadioField, IntegerField
from wtforms.validators import DataRequired

#choices need to be added as admin creates terms
class TermProducts(FlaskForm):
    product = RadioField('Term Product', choices=['The GSB 10', 'The GSB 20', 'The GSB 50'], validators=[DataRequired()])
    amount = DecimalField('Enter the amount you wish to deposit:', validators=[DataRequired()], places=2)
    submit = SubmitField('Deposit')

