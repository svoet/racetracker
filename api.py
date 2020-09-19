#from heat import HeatAPIHandler
#from race import RaceAPIHandler
#from mark import MarkAPIHandler
#from participant import ParticipantAPIHandler
#from person import PersonAPIHandler
#from racinggroup import RacingGroupAPIHandler
#from rounding import RoundingAPIHandler
#from yachtclass import YachtClassAPIHandler
#from yacht import YachtAPIHandler
import models

heats = models.HeatAPIHandler()
races = models.RaceAPIHandler()
marks = models.MarkAPIHandler()
participants = models.ParticipantAPIHandler()
persons = models.PersonAPIHandler()
racinggroups = models.RacingGroupAPIHandler()
roundings = models.RoundingAPIHandler()
yachtclasses = models.YachtClassAPIHandler()
yachts = models.YachtAPIHandler()
