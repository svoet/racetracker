#!/usr/bin/python3
import os
import sys
from config import db,basedir
from datetime import datetime
import api


# Data to initialize database with
RACES = [
        {'name': 'Potjesregatta', 'starttime': '2020-09-21 08:00'},
        {'name': '5 Hours De Panne for Standart','starttime':  '2020-10-10 08:00'}
]
PERSONS = [
          {
                  "countrycode": "BE", "firstname": "Symen", "fislyid": "001", "id": 1, "lastname": "Voet"
                                    },
            {
                    "countrycode": "BE", "firstname": "Egon", "fislyid": "002", "id": 2, "lastname": "Plovier"
                                      },
              {
                      "countrycode": "BE", "firstname": "Jan", "fislyid": "003", "id": 3, "lastname": "Leye"
                                        },
                {
                        "countrycode": "BE", "firstname": "Ronny", "fislyid": "003", "id": 4, "lastname": "Nollet"
                                          }
                ]

YACHTCLASSES = [
          {
                  "code": "3", "description": "Class 3", "id": 1 },
            {
                    "code": "2", "description": "Class 2", "id": 2 },
              {
                      "code": "5", "description": "Class 5", "id": 3 },
                {
                        "code": "S", "description": "Class Standart", "id": 4 },
                  {
                          "code": "P", "description": "Class Promo", "id": 5 },
                    {
                            "code": "MY", "description": "Mini Yacht", "id": 6 }
                    ]

RACINGGROUPS = [
          {
                  "id": 1, "name": "class 2 and 3", "race_id": 1 },
            {
                    "id": 2, "name": "Promo, 5 and Standart", "race_id": 1 }
            ]

YACHTS = [
          {
                  "id": 1, "sailnumber": "B69", "yachtclass_id": 1 },
            {
                    "id": 2, "sailnumber": "B99", "yachtclass_id": 1 },
              {
                      "id": 3, "sailnumber": "B50", "yachtclass_id": 1 },
                {
                        "id": 4, "sailnumber": "B101", "yachtclass_id": 1 }
                ]

MARKS = [
          { "id": 1, "name": "Paal Frankrijk", "order": 1, "racinggroup_id": 1 },
            { "id": 2, "name": "Paal De Panne", "order": 2, "racinggroup_id": 1 }
            ]

HEATS = [
          { "endtime": "2020-09-20T08:30:00", "id": 1, "racinggroup_id": 1, "starttime": "2020-09-20T08:00:00" },
            { "endtime": "2020-09-20T09:30:00", "id": 2, "racinggroup_id": 1, "starttime": "2020-09-20T09:00:00" }
            ]

PARTICIPANTS = [
          { "id": 1, "person_id": 1, "racinggroup_id": 1, "yacht_id": 1 },
            { "id": 2, "person_id": 2, "racinggroup_id": 1, "yacht_id": 2 },
              { "id": 3, "person_id": 3, "racinggroup_id": 1, "yacht_id": 3 },
                { "id": 4, "person_id": 4, "racinggroup_id": 1, "yacht_id": 4 }
                ]

# Delete database file if it exists currently
dbfile=os.path.join(basedir,'data', 'racetracker.db')
if os.path.exists(dbfile):
    os.remove(dbfile)

# Create the database
db.create_all()

for obj in RACES:
    api.races.post(obj)
for obj in PERSONS:
    api.persons.post(obj)
for obj in YACHTCLASSES:
    api.yachtclasses.post(obj)
for obj in YACHTS:
    api.yachts.post(obj)
for obj in RACINGGROUPS:
    api.racinggroups.post(obj)
for obj in MARKS:
    api.marks.post(obj)
for obj in HEATS:
    api.heats.post(obj)
for obj in PARTICIPANTS:
    api.participants.post(obj)

db.session.commit()
