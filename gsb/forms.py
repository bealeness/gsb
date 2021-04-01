from flask_wtf import FlaskForm
from gsb.models import User
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, 
                        IntegerField, DecimalField, RadioField, SelectField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), 
                                        Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                        validators=[DataRequired(), EqualTo('password')])
    accept_tos = BooleanField('I accept the Terms of Service', validators=[DataRequired()])           
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken.  Please choose a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken.  Please choose a different email.')




class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')



class PaySomeone(FlaskForm):
    receiver = IntegerField('Enter the receivers account number:', validators=[DataRequired()])
    amount = DecimalField('Enter the amount:', validators=[DataRequired()], places=2)
    note = StringField('Write a short note (optional):', validators=[Optional(), Length(min=1, max=30)])
    submit = SubmitField('Send')



class TermProducts(FlaskForm):
    amount = DecimalField('Enter the amount you wish to deposit:', validators=[DataRequired()], places=2)
    submit = SubmitField('Deposit')

class CreateTermProduct(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    maturity = IntegerField('Maturity', validators=[DataRequired()])
    rate = DecimalField('Rate', validators=[DataRequired()], places=2)
    submit = SubmitField('Create')


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
