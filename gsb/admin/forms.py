from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField
from wtforms.validators import DataRequired





class CreateTermProduct(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    maturity = IntegerField('Maturity:', validators=[DataRequired()])
    rate = DecimalField('Rate:', validators=[DataRequired()], places=2)
    submit = SubmitField('CreateTerm')





class CreateBond(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    ref_num = IntegerField('Ref num:', validators=[DataRequired()])
    maturity = IntegerField('Maturity:', validators=[DataRequired()])
    rate = DecimalField('Rate:', validators=[DataRequired()], places=2)
    face_value = DecimalField('Face:', validators=[DataRequired()], places=2)
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('CreateBond')

