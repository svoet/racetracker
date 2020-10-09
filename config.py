import os
import connexion
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


basedir = os.path.abspath(os.path.dirname(__file__))
dbfile=os.path.join(basedir,'data', 'racetracker_schema_20201008.db')

# Create the Connexion application instance
connex_app = connexion.App(__name__, specification_dir=os.path.join(basedir,'swagger'))

# Get the underlying Flask app instance
app = connex_app.app

app.config['SECRET_KEY'] = 'How can this be a secret when its out on github?'
# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + dbfile
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

#Initialize login
login_manager = LoginManager()
login_manager.init_app(app)

#load auth blueprint
# blueprint for auth routes in our app
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

import models
