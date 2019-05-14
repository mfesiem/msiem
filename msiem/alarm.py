"""
    msiem alarms
"""
from .session import ESMObject, ESMSession
from .exceptions import ESMException
from .constants import ALARM_FILTER_FIELDS, ALARM_EVENT_FILTER_FIELDS, ALARM_DEFAULT_FIELDS
from prettytable import PrettyTable


class Alarm(ESMObject):
    """
    Alarm object.
    Gives possibility to access alarm fields and related events.
    Delete, Ack, or Unack alarm.
    """

    def __init__(self, **args):
        """
        Have to be instanciated with all the infos in parameters.
        Nothing is retreived from the ESM at the time of instanciation.
        Alarm.detailed property will return the fetched alarm infos if
        you passed a valid id.
        We can instanciate Alarm object with any data we want at this time.
        #TODO be able to pass only the id not a dict(value=id)
        """
        
        self.id = {"value" : 0}
        self.summary = ''
        self.assignee = ''
        self.severity = 0
        self.triggeredDate = ''
        self.acknowledgedDate = ''
        self.acknowledgedUsername = ''
        self.alarmName = ''
        self.conditionType = 0

        self.__dict__.update(args)

        self._detailed = None

        super().__init__()

    def _hasID(self):
        """
        We can instanciate Alarm object with any data we want at this time.
        So this method checks if the ID has been initiated
        """
        try :
            if self.id['value'] == 0 :
                return False
            else :
                return True
        except KeyError :
            return False


    @property
    def detailed(self):
        """
        Fetch the completed detais of the Alarm from the ESM 
        and returns a DetailedAlarm object
        """
        if self._hasID() :
            if self._detailed is None :
                self._detailed = DetailedAlarm(self)
            return self._detailed
        else :
            raise ESMException("Looks like this alarm doesn't have a valid ID. Cannot get the details.")

    @property
    def events(self):
        return self.detailed.events

    @property
    def status(self):
        """
        #TODO use a boolean maybe with is_acknowledged() ?
        """
        return('acknowledged' if (
            len(self.acknowledgedDate)>0
            and 
            len(self.acknowledgedUsername)>0)
            else 'unacknowledged')

    def delele(self):
        """
        Deletes the alarm. Be careful.
        """
        if self._hasID() :
            self.esmRequest('delete_alarms', ids=[self.id['value']])
        else :
            raise ESMException("Looks like this alarm doesn't have a valid ID. Cannot delete.")
        return
    
    def acknowledge(self):
        """
        Acknowledge the alarm.
        """
        if self._hasID() :
            self.esmRequest('ack_alarms', ids=[self.id['value']])
        else :
            raise ESMException("Looks like this alarm doesn't have a valid ID. Cannot acknowledge.")
        return

    def unacknowledge(self):
        """
        Unacknowledge the alarm.
        """
        if self._hasID() :
            self.esmRequest('unack_alarms', ids=[self.id['value']])
        else :
            raise ESMException("Looks like this alarm doesn't have a valid ID. Cannot unacknowledge.")
        return  

class DetailedAlarm(Alarm):
    """
    Alarm details object. Based on EsmTriggeredAlarmDetail
    """
    def __init__(self, alarm):

        if not alarm._hasID() :
            raise ESMException("Looks like this alarm doesn't have a valid ID. Cannot init DetailledAlarm.")
        
        super().__init__(id=alarm.id)

        #Listing all attributes an alarm object have
        self.id = {"value" : 0}     
        self.summary = ''           
        self.assignee = ''          
        self.severity = 0 
        self.triggeredDate  = '' 
        self.acknowledgedDate  = ''
        self.acknowledgedUsername  = ''
        self.alarmName  = ''
        self.conditionType  = 0 
        self.filters  = ''
        self.queryId = 0
        self.alretRateMin = 0
        self.alertRateCount = 0
        self.percentAbove = 0
        self.percentBelow = 0
        self.offsetMinutes = 0
        self.timeFilter  = ''
        self.maximumConditionTriggerFrequency = 0
        self.useWatchlist = ''
        self.matchField = ''
        self.matchValue = ''
        self.healthMonStatus = ''
        self.assigneeId = 0
        self.escalatedDate = ''
        self.caseId = 0
        self.caseName = ''
        self.iocName = 0
        self.iocId = 0
        self.description = ''
        self.actions = ''
        
        #Actually getting the properties information by calling the ESM
        #This opération takes time
        self._events=list()
        resp = self.esmRequest('get_alarm_details', id=alarm.id)
        self.__dict__.update(resp)
        self.id = alarm.id
        self._events = resp['events']

    @property
    def detailed(self):
        return self

    @property
    def events(self):
        return self._events

class AlarmCollection(list):
    """
        Makes easy to manage and print a list of alarms by providing a 
        subclass of list having acknowledge, unacknowledge and delete methods
    """
    def __init__(self, alarms):
        super().__init__()
        self+=alarms

    def _ack(self, alarm):
        return alarm.acknowledge()

    def _unack(self, alarm):
        return alarm.unacknowledge()

    def _delete(self, alarm):
        return alarm.delete()

    def ack(self):
        self.acknowledge()

    def unack(self):
        self.unacknowledge()

    def acknowledge(self):
        ESMSession()._logger.info("Ackowledging alarms...")
        ESMSession()._executor.map(self._ack, self)

    def unacknowledge(self):
        ESMSession()._logger.info("Unackowledging alarms...")
        ESMSession()._executor.map(self._unack, self)

    def delete(self):
        raise ESMException("Not implemented for security reasons.")
        """
        ESMSession()._logger.info("Unackowledging alarms...")
        ESMSession()._executor.map(self._delete, self)
        """

    def show(self, add_columns=[], sortBy=None):
        table = PrettyTable()
        table.field_names=[f[0] for f in ALARM_FILTER_FIELDS]+['status']+[f[0] for f in ALARM_EVENT_FILTER_FIELDS]
        for a in self :
            table.add_row(
                [a.__dict__[f[0]] for f in ALARM_FILTER_FIELDS]+[a.status]+
                [ (a.events[0][f[0]] if len(a.events)>0 else 'No event') for f in ALARM_EVENT_FILTER_FIELDS])

        print(table.get_string(fields=ALARM_DEFAULT_FIELDS+add_columns, sortby=sortBy))

    def json(self):
        return None
