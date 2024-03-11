from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime
from models import VotingSession, Task, Vote
from forms import StartVoteForm, VoteForm
from utils import generate_qr_code, summarize_votes

@app.route('/')
@login_required
def index():
    # List all voting sessions
    voting_sessions = VotingSession.query.filter_by(is_active=True).all()
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
            vote_type=form.vote_type.data
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
    if form.validate_on_submit():
        # Record user's votes
        for task_id, vote_value in form.votes.data.items():
            vote = Vote(
                session_id=session_id,
                task_id=task_id,
                vote_value=vote_value,
                user_id=current_user.id
            )
            db.session.add(vote)
        db.session.commit()
        return redirect(url_for('vote_details', session_id=session_id))
    tasks = Task.query.filter_by(session_id=session_id).all()
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
