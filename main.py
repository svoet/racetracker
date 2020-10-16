#!/usr/bin/python3
import sys
import os
sys.path.append("models")
from flask import (
    Flask,
    render_template,
    request
)
from flask_login import login_required,current_user
import config
import api
import models
import auth
from connexion.resolver import RestyResolver

#import initdb_test
if not os.path.exists(config.dbfile):
    # Create the database
    config.db.create_all()
    config.db.session.commit()

# Create the application instance
app = config.connex_app

# Read the swagger.yml file to configure the endpoints
app.add_api('main.yml',resolver=RestyResolver('api'))

@config.login_manager.user_loader
def load_user(user_id):
    return models.Person.query.filter_by(email=user_id).first()

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return render_template('landing.html',races=api.races.search(),current_user=current_user)

@app.route('/race/<id>')
@login_required
def race(id):
    return render_template('races.html',race=api.races.get(id),all_yachtclasses=api.yachtclasses.search(),all_marks=api.marks.search(),all_persons=api.persons.search(),all_yachts=api.yachts.search(),current_user=current_user)

@app.route('/race/<id>/live')
def live(id):
    return render_template('live.html',race=api.races.get(id),current_user=current_user)

@app.route('/race/<id>/heat/<heat_id>/scoring')
@login_required
def scoring(id,heat_id):
    heat=api.heats.get(heat_id)
    mymark_id=request.cookies.get('mymark-id')
    return render_template('scoring.html',race=api.races.get(id),heat=heat,racinggroup=api.racinggroups.get(heat['racinggroup_id']),current_user=current_user,mymark_id=mymark_id)

@app.route('/classes/')
def classes():
    return render_template('classes.html')
@app.route('/people/')
def people():
    return render_template('people.html')
# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)

