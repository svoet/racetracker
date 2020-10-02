#!/usr/bin/python3
import sys
import os
sys.path.append("models")
from flask import (
    Flask,
    render_template
)
import config
import api
import models
from connexion.resolver import RestyResolver

#import initdb_test
if not os.path.exists(config.dbfile):
    # Create the database
    db.create_all()
    db.session.commit()

# Create the application instance
app = config.connex_app

# Read the swagger.yml file to configure the endpoints
app.add_api('main.yml',resolver=RestyResolver('api'))

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return render_template('landing.html',races=api.races.search())

@app.route('/race/<id>')
def race(id):
    return render_template('races.html',race=api.races.get(id),all_yachtclasses=api.yachtclasses.search(),all_marks=api.marks.search(),all_persons=api.persons.search(),all_yachts=api.yachts.search())

@app.route('/race/<id>/live')
def live(id):
    return render_template('live.html',race=api.races.get(id))

@app.route('/race/<id>/heat/<heat_id>/scoring')
def scoring(id,heat_id):
    return render_template('scoring.html',race=api.races.get(id),heat=api.heats.get(heat_id))

#def racemenu_data(id):
#    return api.races.get(id)
#    race_orm = models.Race.query.filter(models.Race.id == id).one_or_none()
#    race=models.RaceSchema().dump(race_orm)
#    racinggroups=[]
#    for racinggroup_orm in race_orm.racinggroups:
#        racinggroup=models.RacingGroupSchema().dump(racinggroup_orm)
#        heats=[]
#        for heat_orm in racinggroup_orm.heats:
#            heats.append(models.HeatSchema().dump(heat_orm))
#        racinggroup['heats']=heats
#        racinggroups.append(racinggroup)
#    race['racinggroups']=racinggroups
#    return race
@app.route('/classes/')
def classes():
    return render_template('classes.html')
@app.route('/people/')
def people():
    return render_template('people.html')
# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)

