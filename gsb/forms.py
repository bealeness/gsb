from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DecimalField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), 
                                        Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                        validators=[DataRequired(), EqualTo('password')])
    accept_tos = BooleanField('I accept the Terms of Service', validators=[DataRequired()])           
    submit = SubmitField('Sign Up')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')



class PaySomeone(FlaskForm):
    receiver = IntegerField('Enter the receivers account number:', validators=[DataRequired()])
    amount = DecimalField('Enter the amount:', validators=[DataRequired()], places=2)
    note = StringField('Write a short note (optional):', validators=[Length(min=2, max=30)])
    submit = SubmitField('Send')



class TermProducts(FlaskForm):
    product = RadioField('Choose a Term Product', choices=[('value1', 'The GSB Daily'), ('value2', 'The GSB Double Daily')], validators=[DataRequired()])
    amount = DecimalField('Enter the amount you want in this term:', validators=[DataRequired()], places=2)
    submit = SubmitField('Deposit')


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


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), 
                                        Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')