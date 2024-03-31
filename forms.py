from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FieldList, FormField , RadioField
from wtforms import PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

class StartVoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    vote_type = SelectField('Vote Type', choices=[('brainstorming', 'Brainstorming'), ('estimation', 'Estimation') ,('options_voting', 'Options Voting')], validators=[DataRequired()])
    task_details = TextAreaField('Task Details')
    option_list = TextAreaField('Option List')

class OptionVoteField(FlaskForm):
    option = RadioField('Options', coerce=str)


class VoteField(FlaskForm):
    task_id = StringField('Task ID')
    vote_value = StringField('Vote Value')


class VoteForm(FlaskForm):
    votes = FieldList(FormField(VoteField), min_entries=1)
    option_votes = FieldList(FormField(OptionVoteField), min_entries=0)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired() ])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


