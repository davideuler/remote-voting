from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

from flask_wtf.csrf import CSRFProtect 
csrf = CSRFProtect() 

import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = Config.SECRET_KEY
csrf.init_app(app)

db = SQLAlchemy(app)
db.init_app(app)

def create_db():
    with app.app_context():
        db.create_all()

create_db()
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from views import *
from auth import *
from models import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8899, debug=True)
