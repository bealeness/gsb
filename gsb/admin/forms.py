from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, RadioField, TextAreaField
from wtforms.validators import DataRequired

class CreateTermProduct(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    maturity = IntegerField('Maturity:', validators=[DataRequired()])
    rate = DecimalField('Rate:', validators=[DataRequired()], places=2)
    info = TextAreaField('Info:', validators=[DataRequired()])
    submit = SubmitField('CreateTerm')


class CreateBond(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    ref_num = IntegerField('Ref num:', validators=[DataRequired()])
    maturity = IntegerField('Maturity:', validators=[DataRequired()])
    rate = DecimalField('Rate:', validators=[DataRequired()], places=2)
    face_value = DecimalField('Face:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    info = TextAreaField('Info:', validators=[DataRequired()])
    submit = SubmitField('CreateBond')



class CashOut(FlaskForm):
    user = IntegerField('Enter the owner ID:', validators=[DataRequired()])
    ref_num = IntegerField('Enter the ref num:', validators=[DataRequired()])
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('CashOut')


class TermCashOut(FlaskForm):
    user = IntegerField('Enter the owner ID:', validators=[DataRequired()])
    term_id = IntegerField('Enter the term ID:', validators=[DataRequired()])
    balance = IntegerField('Balance:', validators=[DataRequired()])
    submit = SubmitField('CashOut')


class MarketForm(FlaskForm):
    status = RadioField('Market status:', choices=['Open', 'Close'], validators=[DataRequired()]) 
    submit = SubmitField('Change')