from flask import render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime

from wtforms import FieldList, FormField
from models import VotingSession, Task, Vote
from forms import StartVoteForm, VoteForm, VoteField, OptionVoteField
from utils import generate_qr_code, summarize_votes

@app.route('/')
@login_required
def index():
    # List all voting sessions
    voting_sessions = VotingSession.query.filter_by(
        is_active=True, creator_user_id=current_user.id).all()

    return render_template('index.html', voting_sessions=voting_sessions)


@app.route('/start', methods=['GET', 'POST'])
@login_required
def start_vote():
    form = StartVoteForm()
    if form.validate_on_submit():
        # Create a new voting session
        voting_session = VotingSession(
            title=form.title.data,
            description=form.description.data,
            vote_type=form.vote_type.data,
            creator_user_id=current_user.id
        )
        db.session.add(voting_session)
        db.session.commit()
        # Create tasks for the voting session
        if form.vote_type.data == 'estimation':
            for task_title in form.task_details.data.splitlines():
                task = Task(title=task_title, session_id=voting_session.session_id)
                db.session.add(task)
        elif form.vote_type.data == 'options_voting':
            task = Task(
                title=form.title.data,
                option_list=form.option_list.data,
                session_id=voting_session.session_id
            )
            db.session.add(task)
        elif form.vote_type.data == 'brainstorming':
            task = Task(
                title=form.title.data,
                description=form.description.data,
                session_id=voting_session.session_id
            )
            db.session.add(task)
        db.session.commit()
        return redirect(url_for('vote_details', session_id=voting_session.session_id))
    return render_template('start_vote.html', form=form)

@app.route('/vote/<session_id>', methods=['GET', 'POST'])
@login_required
def vote(session_id):
    voting_session = VotingSession.query.get_or_404(session_id)
    if not voting_session.is_active:
        return redirect(url_for('index'))
    form = VoteForm()
    if request.method == 'POST' and form.validate_on_submit(): 
        error = False
        for vote_form in form.votes:
            # Check if the vote already exists
            existing_vote = Vote.query.filter_by(
                session_id=session_id,
                task_id=vote_form.task_id.data,
                user_id=current_user.id
            ).first()
            if existing_vote:
                # If vote already exists, flash an error message
                flash('You have already voted for this task. You cannot vote twice.', 'error')
                error = True
                break

        if not error and not voting_session.vote_type == 'options_voting':
            # Record user's votes
            print("votes submitted....")
            for vote_form in form.votes:
                vote = Vote(
                    session_id=session_id,
                    task_id=vote_form.task_id.data,
                    vote_value=vote_form.vote_value.data,
                    user_id=current_user.id
                )
                db.session.add(vote)
            db.session.commit()
            return redirect(url_for('vote_details', session_id=session_id))
    elif request.method == 'POST': #and form.validate_on_submit(): 
        app.logger.error('Form failed to validate:')
        app.logger.error(form.errors)

    tasks = Task.query.filter_by(session_id=session_id).all()

    # Initialize form.votes with the number of tasks
    if request.method == 'GET':  # Only populate form.votes on GET request
        while len(form.votes) < len(tasks):
            form.votes.append_entry()

        for i, task in enumerate(tasks):
            form.votes[i].task_id.data = task.task_id
        
    # Handle options voting post request
    #print("vote_type:%s " % (voting_session.vote_type)) 
    if voting_session.vote_type == 'options_voting':
        task = tasks[0]  # There should be only one task for options voting
        options = task.option_list.splitlines()
        form.option_votes = []
        option_form = OptionVoteField()
        option_form.option.choices = [(option, option) for option in options]
        form.option_votes.append(option_form)
        selected_option = request.form.get('option')
        if selected_option and request.method == 'POST':
            vote = Vote(session_id=session_id, task_id=task.task_id, vote_value=selected_option, user_id=current_user.id)
            db.session.add(vote)
            db.session.commit()
            return redirect(url_for('vote_details', session_id=session_id))

    #print("form.votes, len:%d votes:%s" %  (len(form.votes), str(form.votes)) )
    return render_template('vote.html', voting_session=voting_session, tasks=tasks, form=form)

@app.route('/vote/details/<session_id>')
@login_required
def vote_details(session_id):
    voting_session = VotingSession.query.get_or_404(session_id)
    tasks = Task.query.filter_by(session_id=session_id).all()
    votes = Vote.query.filter_by(session_id=session_id).all()

    summary = summarize_votes(votes, voting_session.vote_type)
    qr_code = generate_qr_code(url_for('vote', session_id=session_id, _external=True))
    return render_template('vote_details.html', voting_session=voting_session, tasks=tasks, votes=votes, summary=summary, qr_code=qr_code)

@app.route('/vote/end/<session_id>')
@login_required
def end_vote(session_id):
    voting_session = VotingSession.query.get_or_404(session_id)
    if voting_session.is_active:
        voting_session.is_active = False
        voting_session.finished_at = datetime.utcnow()
        db.session.commit()
    return redirect(url_for('vote_details', session_id=session_id))
