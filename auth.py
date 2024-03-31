from flask import redirect, url_for, flash, request, render_template
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse

from app import app, db, login_manager
from models import User
from oauthlib.oauth2 import WebApplicationClient
import requests
from forms import RegistrationForm, LoginForm

# GitHub OAuth configuration
client = WebApplicationClient(app.config['GITHUB_CLIENT_ID'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login_by_github')
def login_by_github():
    # GitHub OAuth login URL and state
    github_login_url = client.prepare_request_uri('https://github.com/login/oauth/authorize')
    return redirect(github_login_url)

@app.route('/login/callback')
def callback():
    # GitHub OAuth callback handling
    # Get authorization code from response
    code = request.args.get('code')
    # Prepare and send request to get tokens
    token_url, headers, body = client.prepare_token_request(
        'https://github.com/login/oauth/access_token',
        authorization_response=request.url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config['GITHUB_CLIENT_ID'], app.config['GITHUB_CLIENT_SECRET']),
    )
    # Parse the tokens
    client.parse_request_body_response(token_response.text)
    # Get user info from GitHub
    userinfo_endpoint = 'https://api.github.com/user'
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get('login'):
        username = userinfo_response.json()['login']
        # Check if user exists, if not, create new user
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, email=username + "@github.com")
            db.session.add(user)
            db.session.commit()
        # Log in the user
        login_user(user)
        return redirect(url_for('index'))
    else:
        flash('Could not authenticate with GitHub.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
