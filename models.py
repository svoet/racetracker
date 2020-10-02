from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from marshmallow import ValidationError
from apihandler import GenericAPIHandler
import datetime
import pdb
import config
from enum import Enum



class Heat(config.db.Model):
    class HeatStatus():
        NOT_STARTED = 0
        STARTED = 1
        ENDED = 2
        CANCELLED = 3

    def defaultName(context):
        existing_heats=Heat.query\
                .filter( Heat.racinggroup_id == context.get_current_parameters()['racinggroup_id'])\
                .filter( Heat.status != Heat.HeatStatus.CANCELLED).count()
        return "H{}".format(existing_heats + 1)

    __tablename__ = 'heat'
    id = Column(Integer, primary_key=True)
    racinggroup_id = Column(Integer, ForeignKey('racinggroup.id'))
    roundings = relationship( 'Rounding',backref="heat")
    starttime = Column(DateTime)
    endtime = Column(DateTime)
    name = Column(String,default=defaultName)
    status = Column(Integer,default=HeatStatus.NOT_STARTED)


class Mark(config.db.Model):
    __tablename__ = 'mark'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    order = Column(Integer)
    racinggroup_id = Column(Integer, ForeignKey('racinggroup.id'))
    roundings = relationship('Rounding',backref='mark')

class Participant(config.db.Model):
    __tablename__ = 'participant'
    id = Column(Integer, primary_key=True)
    racinggroup_id = Column(Integer, ForeignKey('racinggroup.id'))
    yacht_id = Column(Integer, ForeignKey('yacht.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    roundings = relationship( 'Rounding',backref="participant")

class Person(config.db.Model):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)
    countrycode = Column(String)
    fislyid = Column(String)
    email = Column(String)
    participants = relationship( 'Participant',backref="person")
    yachts = relationship('Yacht', secondary = 'person_yacht_link')

class PersonYachtLink(config.db.Model):
    __tablename__ = 'person_yacht_link'
    person_id = Column(Integer, ForeignKey('person.id'),primary_key=True)
    yacht_id = Column(Integer, ForeignKey('yacht.id'),primary_key=True)

class Race(config.db.Model):
    __tablename__ = 'race'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    starttime = Column(DateTime)
    racinggroups = relationship('RacingGroup',backref='race',lazy='select')

class RacingGroup(config.db.Model):
    __tablename__ = 'racinggroup'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    race_id = Column(Integer, ForeignKey('race.id'))
    participants = relationship( 'Participant',backref="racinggroup")
    heats = relationship('Heat',backref="racinggroup")
    yachtclasses = relationship('YachtClass',secondary="racinggroup_yachtclass_link")

class Rounding(config.db.Model):
    __tablename__ = 'rounding'
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('participant.id'))
    mark_id = Column(Integer, ForeignKey('mark.id'))
    heat_id = Column(Integer, ForeignKey('heat.id'))
    registeredtime = Column(DateTime)
    overriddentime = Column(DateTime)

    @property
    def time(self):
        if self.overriddentime:
            return overriddentime
        else:
            return registeredtime

class YachtClass(config.db.Model):
    __tablename__ = 'yachtclass'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)
    yachts = relationship('Yacht',backref="yachtclass")

class Yacht(config.db.Model):
    __tablename__ = 'yacht'
    id = Column(Integer, primary_key=True)
    sailnumber = Column(String)
    yachtclass_id = Column(Integer, ForeignKey('yachtclass.id'))
    participants = relationship( 'Participant',backref="yacht")

class RacingGroupYachtClassLink(config.db.Model):
    __tablename__ = 'racinggroup_yachtclass_link'
    racinggroup_id = Column(Integer, ForeignKey('racinggroup.id'),primary_key=True)
    yachtclass_id = Column(Integer, ForeignKey('yachtclass.id'),primary_key=True)

#SCHEMAS and APIHandlers from here
class HeatSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Heat
        sqla_session=config.db.session
        load_instance = True
        include_fk = True

class HeatAPIHandler(GenericAPIHandler):
    object_class = Heat
    schema_class = HeatSchema

    def getParticipants(self,heat_id):
        ret=[]
        try:
            participants=racinggroup=Heat.query.filter(Heat.id == heat_id).one_or_none().racinggroup.participants
            roundings = Rounding.query.filter(Rounding.heat_id == heat_id).order_by(Rounding.overriddentime.desc()).all()
            #Group all roundings per participant
            #[ { participant: { ... }, position : 3, passing_order : 3, roundings: []}]
            for participant in participants:
                ret.append({
                    "participant": ParticipantSchema().dump(participant),
                    "last_rounding_time":0,
                    "roundings":[]}),

            for rounding in roundings:
                found=False
                found_position=0
                for i in range(0,len(ret)):
                    if ret[i]['participant']['id'] == rounding.participant_id:
                        found=True
                        found_position=i
                        break
                #pconfig.db.set_trace()
                #If the participant is not in the ret list yet, add it
                if not found:
                    #this should actually never occur, since all participants should be already listed
                    ret.append({
                        "participant": ParticipantSchema().dump(Participant.query.filter(Participant.id == rounding.participant_id).one_or_none()),
                        "last_rounding_time" : rounding.overriddentime.timestamp(),
                        "roundings" : [ RoundingSchema().dump(rounding) ]})
                else:
                    if ret[i]['last_rounding_time'] == 0:
                        ret[i]['last_rounding_time'] = rounding.overriddentime.timestamp()

                    ret[i]['roundings'].append(RoundingSchema().dump(rounding))

            #First, order all roundings from old to new, regardless of laps. That's the "passing order"
            #TODO: this only works for scoring on a single mark. for multiple marks ,we need to:
            #   -do passing order on the mark where the first pilot has last passed
            #   -then do passing order on the previous mark (Mark-1, not len(roundings))
            #   -continue until all marks have been processed
            passing_order=1
            ret.sort(key=lambda x:x['last_rounding_time'],reverse=False)
            for i in range(0,len(ret)):
                ret[i]['passing_order']=passing_order
                passing_order=passing_order+1

            position=1
            ret.sort(key=lambda x:len(x['roundings']),reverse=True)
            for i in range(0,len(ret)):
                if len(ret[i]['roundings']) > 0:
                    ret[i]['position']=position
                    position=position+1
                else:
                    ret[i]['position']=len(ret)
        except Exception as e:
            config.app.logger.error(e)
            pass
            #TODO log the error

        # Serialize the data for the response
        #schema = self.schema_class(many=True)
        #data = scheconfig.ma.dump(objects)
        return ret

    def getRoundings(self,heat_id):
        roundings = Rounding.query.filter(Rounding.heat_id == heat_id).order_by(Rounding.overriddentime).all()
        return RoundingWithParticipantSchema(many=True).dump(roundings)


    def addRounding(self,heat_id,object):
        #object['registeredtime']=datetime.datetime.now().strptime('%Y-%m-%d %H:%M:%S %Z')
        object['registeredtime']=datetime.datetime.now().isoformat()
        object['overriddentime']=object['registeredtime']
        object['heat_id']=heat_id
        if Participant.query.filter(Participant.id == object['participant_id']).one_or_none() == None:
            raise ValidationError("Participant with id '{}' not found.".format(object['participant_id']))
        api=RoundingAPIHandler()
        api.post(object)

class MarkSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mark
        sqla_session=config.db.session
        load_instance=True
        include_fk = True

class MarkAPIHandler(GenericAPIHandler):
    object_class = Mark
    schema_class = MarkSchema

class ParticipantSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Participant
        sqla_session=config.db.session
        load_instance = True
        include_fk = True

    person = config.ma.Nested('PersonSchema',only=('firstname','lastname','countrycode'))
    yacht = config.ma.Nested('YachtSchema',only=('sailnumber','yachtclass'))

class ParticipantAPIHandler(GenericAPIHandler):
    object_class = Participant
    schema_class = ParticipantSchema


class PersonSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        sqla_session=config.db.session
        load_instance = True

class PersonAPIHandler(GenericAPIHandler):
    object_class = Person
    schema_class = PersonSchema

#from marshmallow_sqlalchemy.fields import Nested


class RaceSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Race
        sqla_session=config.db.session
        load_instance=True
        include_fk = True
        include_relationships=True

    racinggroups = config.ma.Nested('RacingGroupSchema',many=True,only=('id','name','heats','yachtclasses','participants'))

class RaceAPIHandler(GenericAPIHandler):
    object_class = Race
    schema_class = RaceSchema


class RacingGroupSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RacingGroup
        sqla_session=config.db.session
        include_fk = True
        include_relationships=True
        load_instance = True

    heats = config.ma.Nested('HeatSchema',many=True,only=('id','starttime','endtime','status','name'))
    participants = config.ma.Nested('ParticipantSchema',many=True,only=('id','yacht','person'))
    yachtclasses = config.ma.Nested('YachtClassSchema',many=True,only=('id','code','description'))

class RacingGroupAPIHandler(GenericAPIHandler):
    object_class = RacingGroup
    schema_class = RacingGroupSchema

    def addParticipant(self,racinggroup_id,object):
        person_id=None
        yacht_id=None
        if ("person_id" in object.keys()):
            person_id=object['person_id']
        if ("yacht_id" in object.keys()):
            yacht_id=object['yacht_id']
        if person_id == None or Person.query.filter(Person.id == person_id).one_or_none() == None:
            new_person={ 'firstname': object['firstname'],\
                    'lastname':object['lastname'],\
                     }
            for key in ['email','fislyid','countrycode']:
                if key in object.keys():
                     new_person[key]=object[key]
            ret=PersonAPIHandler().post(new_person)
            person_id=ret[0]['id']
        if yacht_id == None or Yacht.query.filter(Yacht.id == yacht_id).one_or_none() == None:
            new_yacht={ 'sailnumber': object['sailnumber'],\
                    'yachtclass_id':object['yachtclass_id']\
                    }
            ret=YachtAPIHandler().post(new_yacht)
            yacht_id=ret[0]['id']

        if Participant.query.filter(Participant.racinggroup_id == racinggroup_id).filter(Participant.person_id == person_id).one_or_none():
            raise ValidationError("This person ({}) is already registered in this racinggroup ({})".format(person_id,racinggroup_id))
        if Participant.query.filter(Participant.racinggroup_id == racinggroup_id).filter(Participant.yacht_id == yacht_id).one_or_none():
            raise ValidationError("This yacht ({}) is already registered in this racinggroup ({})".format(yacht_id,racinggroup_id))
        return ParticipantAPIHandler().post({'racinggroup_id':racinggroup_id,'person_id':person_id,'yacht_id':yacht_id})

    def addYachtClass(self,racinggroup_id,yachtclass_id):
        yachtclass=YachtClass.query.filter(YachtClass.id == yachtclass_id).one_or_none()
        racinggroup=RacingGroup.query.filter(RacingGroup.id == racinggroup_id).one_or_none()

        if yachtclass and racinggroup:
            racinggroup.yachtclasses.append(yachtclass)
            config.db.session.add(yachtclass)
            config.db.session.commit()

    def removeYachtClass(self,racinggroup_id,yachtclass_id):
        yachtclass=YachtClass.query.filter(YachtClass.id == yachtclass_id).one_or_none()
        racinggroup=RacingGroup.query.filter(RacingGroup.id == racinggroup_id).one_or_none()

        if yachtclass and racinggroup:
            racinggroup.yachtclasses.remove(yachtclass)
            config.db.session.add(yachtclass)
            config.db.session.commit()

    def addHeat(self,racinggroup_id,heat={}):
        racinggroup=RacingGroup.query.filter(RacingGroup.id == racinggroup_id).one_or_none()

        if not racinggroup:
            raise ValidationError("Racinggroup ({}) not found".format(racinggroup_id))

        heat['racinggroup_id'] = racinggroup_id
        return HeatAPIHandler().post(heat)

class RoundingSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rounding
        sqla_session=config.db.session
        load_instance=True
        include_fk=True

class RoundingWithParticipantSchema(RoundingSchema):
    participant = config.ma.Nested('ParticipantSchema',only=('yacht','person'))

class RoundingAPIHandler(GenericAPIHandler):
    object_class = Rounding
    schema_class = RoundingSchema


class YachtClassSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = YachtClass
        sqla_session=config.db.session
        load_instance = True

class YachtClassAPIHandler(GenericAPIHandler):
    object_class = YachtClass
    schema_class = YachtClassSchema



class YachtSchema(config.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Yacht
        sqla_session=config.db.session
        load_instance = True
        include_fk = True
    yachtclass = config.ma.Nested('YachtClassSchema',only=('code','description'))

class YachtAPIHandler(GenericAPIHandler):
    object_class = Yacht
    schema_class = YachtSchema
