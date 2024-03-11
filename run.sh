# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the application
FLASK_APP=app.py flask db upgrade &
FLASK_APP=app.py flask run
