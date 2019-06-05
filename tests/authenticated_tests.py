# -*- coding: utf-8 -*-=

import unittest
import time
import msiem
import msiem.query
from msiem.session import ESMSession
from msiem.utils import getTimes

class SessionTests(unittest.TestCase):
    """
    Uncomment to wirte authentication to file everytime you run tests

    def test_WriteAuth(self):
        s = ESMSession()
        s._config.setAuth()
        s._config.write()

        return
    """

    def test_Login(self):
        s=ESMSession()
        self.assertEqual(s._login(), True)
    
class QueryTests(unittest.TestCase):

    def test_Alarms(self):

        alarms=msiem.query.AlarmQuery(time_range='LAST_HOUR').execute()
        self.assertGreater(len(alarms),0, "It looks like no alarms were trigered for the last 3 days.")
        
        #1 checks if fields are filled
        alarms = msiem.query.AlarmQuery(time_range='LAST_HOUR').execute()
        for alarm in alarms:
            self.assertGreater(alarm.id['value'], 0)
            self.assertGreater(len(alarm.triggeredDate), 0)
            self.assertGreater(len(alarm.alarmName), 0)

        #2 will fails if the last alarm doesn't have event(s) associated
        alarms = msiem.query.AlarmQuery(time_range='LAST_HOUR').execute()
        alarm = alarms.pop().detailed
        self.assertGreater(len(alarm.events), 0, "will fails if the last alarm doesn't have event(s) associated")

        # create a alarm with a fake id and try to get the details
        with self.assertRaises(Exception):
            msiem.query.Alarm(id={'value':-1}).detailed

        for alarm in msiem.query.AlarmQuery(time_range='LAST_HOUR', status='unacknowledged').execute():
            self.assertEqual(alarm.acknowledgedDate,  '')
            self.assertEqual(alarm.acknowledgedUsername, None)

        alarms = msiem.query.AlarmQuery(
            time_range='CUSTOM',
            start_time='2019-05-08',
            end_time='2019-05-09',
            status='acknowledged').execute()
        self.assertGreater(len(alarms), 0, "Can't get alarms with custom time !")

        """
        for alarm in msiem.query.AlarmQuery(time_range='PREVIOUS_WEEK', page_size=1, status='acknowledged').execute():
            alarm.unacknowledge()
            time.sleep(40)
            alarm=msiem.query.DetailedAlarm(alarm)
            self.assertEqual(alarm.status, 'unacknowledged')
            alarm.acknowledge()
            time.sleep(40)
            alarm=msiem.query.DetailedAlarm(alarm)
            self.assertEqual(alarm.status, 'acknowledged')
            """

    def test_EventQuery(self):

        query = msiem.query.EventQuery(
            #time_range='LAST_3_DAYS',
            fields=['SrcIP', 'DstIP', 'SigID'],
            filters=[msiem.query.GroupFilter(
                msiem.query.FieldFilter('DstIP', ['10.0.0.0/8']),
                msiem.query.FieldFilter('SrcIP', ['10.0.0.0/8']),
                logic='OR'
                )],
            time_range='LAST_3_DAYS'
        )

        query = msiem.query.EventQuery(
            fields=['SrcIP', 'DstIP', 'SigID'],
            filters=[msiem.query.GroupFilter(
                msiem.query.FieldFilter('DstIP', ['10.0.0.0/8']),
                msiem.query.FieldFilter('SrcIP', ['10.0.0.0/8']),
                logic='AND'
                )],
            time_range='LAST_10_MINUTES',
            limit=100
        )
        query.execute().show()

        query = msiem.query.EventQuery(
            fields=['SrcIP', 'DstIP', 'SigID', 'LastTime'],
            filters=[msiem.query.GroupFilter(
                msiem.query.FieldFilter('DstIP', ['10.0.0.0/8']),
                msiem.query.FieldFilter('SrcIP', ['10.0.0.0/8']),
                logic='AND'
                )],
            time_range='LAST_10_MINUTES',
            limit=100,
            sub_query=1
        )
        events = query.execute()
        events.show()
        for e in events :
            self.assertRegex(e.SrcIP,'^10.','Auto offset filtering is problematic')

    def test_TimeRange(self):

        timerange = getTimes('LAST_30_MINUTES')
        events=msiem.query.EventQuery(
            filters=[('DstIP', ['10.0.0.0/8'])],
            limit=5,
            offset=0,
            time_range='CUSTOM',
            start_time=timerange[0],
            end_time=timerange[1]
        ).execute()

        events2=msiem.query.EventQuery(
            filters=[('DstIP', ['10.0.0.0/8'])],
            limit=5,
            offset=0,
            time_range='LAST_30_MINUTES',
            compute_time_range=False
        ).execute()

        self.assertEqual(events[0].__dict__, events2[0].__dict__, 'Time computed time range and default time range gave differents results. This test can sometimes fail if new events came up in the meantime')

        timerange = getTimes('LAST_30_MINUTES')
        events=msiem.query.EventQuery(
            filters=[('DstIP', ['10.0.0.0/8'])],
            limit=5,
            offset=0,
            time_range='CUSTOM',
            start_time=timerange[0],
            end_time=timerange[1]
        ).execute()

        events2=msiem.query.EventQuery(
            filters=[('DstIP', ['10.0.0.0/8'])],
            limit=5,
            offset=0,
            time_range='LAST_30_MINUTES'
            #implicit compute_time_range=True
        ).execute()

        self.assertEqual(events[0].__dict__, events2[0].__dict__, 'The computation itself is wrong. This test can sometimes fail if new events came up in the meantime')

        pass

    def test_AlarmFilter(self):
        
        with self.assertRaisesRegex(msiem.exceptions.ESMException, 'Illegal filter'):
            filtered = msiem.query.AlarmQuery(
                time_range='LAST_24_HOURS',
                filters=('whatever', None)
            )

        for alarm in (msiem.query.AlarmQuery(
            time_range='LAST_24_HOURS',
            filters=('alarmName', 'High Severity Event')
            ).execute()) :
            self.assertRegex(alarm.alarmName.lower(), 'High Severity Event'.lower(), 'Filtering alarms is not working')

        for alarm in (msiem.query.AlarmQuery(
            time_range='LAST_24_HOURS',
            filters=[('alarmName', 'High Severity Event'), ('severity', [80,85,90,95,100])]
            ).execute()) :
            self.assertRegex(alarm.alarmName.lower(), 'High Severity Event'.lower(), 'Filtering alarms is not working')
            self.assertRegex(str(alarm.severity), '80|85|90|95|100', 'Filtering alarms is not working')

        for alarm in (msiem.query.AlarmQuery(
            time_range='LAST_24_HOURS',
            filters=[('alarmName', 'High Severity Event'),
                ('severity', [80,85,90,95,100]),
                ('ruleMessage', 'HTTP')]
            ).execute()) :
            self.assertRegex(alarm.alarmName.lower(), 'High Severity Event'.lower(), 'Filtering alarms is not working')
            self.assertRegex(str(alarm.severity), '80|85|90|95|100', 'Filtering alarms is not working')
            self.assertRegex(str(alarm.events[0]), 'HTTP', 'Filtering alarms is not working')
        

        for alarm in (msiem.query.AlarmQuery(
            time_range='LAST_24_HOURS',
            filters=[('alarmName', 'High Severity Event'),
                ('severity', [80,85,90,95,100]),
                ('ruleMessage', 'HTTP'),
                ('destIp', '10.165')]
            ).execute()) :
            self.assertRegex(alarm.alarmName.lower(), 'High Severity Event'.lower(), 'Filtering alarms is not working')
            self.assertRegex(str(alarm.severity), '80|85|90|95|100', 'Filtering alarms is not working')
            self.assertRegex(str(alarm.events[0]), 'HTTP', 'Filtering alarms is not working')
            self.assertRegex(str(alarm.events[0]), '10.165', 'Filtering alarms is not working')

