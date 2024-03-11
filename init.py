
# run it 
from app import db, app
from models import *

with app.app_context():
        db.create_all()
