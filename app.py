import os
import logging
from datetime import datetime

from flask import Flask, session
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import routes after app is created to avoid circular imports
from routes import *
from models import User, users_db

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(int(user_id))

# Add template filter for formatting dates
@app.template_filter('formatdatetime')
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return value
    return value.strftime(format)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
