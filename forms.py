from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ResourceForm(FlaskForm):
    resource_type = SelectField('Resource Type', choices=[
        ('cpu', 'CPU Cores'),
        ('memory', 'Memory (GB)'),
        ('storage', 'Storage (GB)')
    ], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.1)])
    availability = BooleanField('Available for Sharing', default=True)
    submit = SubmitField('Add Resource')

class ResourceRequestForm(FlaskForm):
    resource_type = SelectField('Resource Type', choices=[
        ('cpu', 'CPU Cores'),
        ('memory', 'Memory (GB)'),
        ('storage', 'Storage (GB)')
    ], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.1)])
    duration = IntegerField('Duration (hours, leave empty for indefinite)', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Request Resource')
