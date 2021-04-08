from flask_wtf import FlaskForm
from gsb.models import User
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, 
                        IntegerField, DecimalField, RadioField, TextAreaField)
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
    note = StringField('Write a short note (optional-maximum 30 characters):', validators=[Optional(), Length(min=1, max=30)])
    submit = SubmitField('Send')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), 
                                        Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    image = RadioField('Background Image', choices=['Midway Sunrise', 'Town', 'Bomb Bridge'])
    submit = SubmitField('Update')


class StatusForm(FlaskForm):
    status = StringField('', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Share')


class MessageForm(FlaskForm):
    message = TextAreaField('Write your message here', validators=[DataRequired(),
                                        Length(min=1, max=300)])
    submit = SubmitField('Send')                              