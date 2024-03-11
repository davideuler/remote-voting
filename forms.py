from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FieldList, FormField 
from wtforms.validators import DataRequired

class StartVoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    vote_type = SelectField('Vote Type', choices=[('estimation', 'Estimation'), ('brainstorming', 'Brainstorming'), ('options_voting', 'Options Voting')], validators=[DataRequired()])
    task_details = TextAreaField('Task Details')
    option_list = TextAreaField('Option List')


class VoteField(FlaskForm):
    task_id = StringField('Task ID')
    vote_value = StringField('Vote Value')


class VoteForm(FlaskForm):
    votes = FieldList(FormField(VoteField), min_entries=1)


