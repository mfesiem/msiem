"""
    msiem event
"""

from.session import ESMObject
from .constants import ALARM_EVENT_FILTER_FIELDS
from prettytable import PrettyTable

class Event(ESMObject):
    """ Based on EsmTriggeredAlarmEvent """
    def __init__(self, **args):
        self.__dict__.update(**args)

    def addNote(self, string):
        pass

class EventCollection(list):
    def __init__(self, events):
        super().__init__()
        self+=events

    def show(self, add_columns=[], sortBy=None):
        table = PrettyTable()
        table.field_names=[f[0] for f in ALARM_EVENT_FILTER_FIELDS]
        for a in self :
            pass #TODO

        #print(table.get_string(fields=ALARM_DEFAULT_FIELDS+add_columns, sortby=sortBy))
