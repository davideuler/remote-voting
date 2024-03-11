from flask import redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import app, db, login_manager
from models import User
from oauthlib.oauth2 import WebApplicationClient
import requests

# GitHub OAuth configuration
client = WebApplicationClient(app.config['GITHUB_CLIENT_ID'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login')
def login():
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
            user = User(username=username)
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
