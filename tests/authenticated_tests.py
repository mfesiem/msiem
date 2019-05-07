# -*- coding: utf-8 -*-=

import unittest
import msiem
import msiem.query
from msiem.session import ESMSession
from msiem.utils import log, getTimes

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

        alarms=msiem.query.AlarmQuery(time_range='LAST_3_DAYS').execute()
        self.assertGreater(len(alarms),0, "It looks like no alarms were trigered for the last 3 days.")
        
        #1 checks if fields are filled
        for alarm in msiem.query.AlarmQuery(time_range='LAST_3_DAYS').execute() :
            self.assertGreater(alarm.id['value'], 0)
            self.assertGreater(len(alarm.triggeredDate), 0)
            self.assertGreater(len(alarm.alarmName), 0)

        #2 will fails if the last alarm doesn't have event(s) associated
        alarms = msiem.query.AlarmQuery(time_range='LAST_3_DAYS').execute()
        alarm = alarms.pop().detailed
        self.assertGreater(len(alarm.events), 0, "will fails if the last alarm doesn't have event(s) associated")

        # create a alarm with a fake id and try to get the details
        with self.assertRaises(Exception):
            msiem.query.Alarm(id={'value':-1}).detailed

        for alarm in msiem.query.AlarmQuery(time_range='LAST_3_DAYS', status='unacknowledged').execute():
            self.assertEqual(alarm.acknowledgedDate,  '')
            self.assertEqual(alarm.acknowledgedUsername, '')
        
        for alarm in msiem.query.AlarmQuery(time_range='PREVIOUS_WEEK', page_size=2, status='acknowledged').execute():
            alarm.unacknowledge()
            time.sleep(20)
            alarm=msiem.query.DetailedAlarm(alarm)
            self.assertEqual(alarm.status, 'unacknowledged')
            alarm.acknowledge()
            time.sleep(20)
            alarm=msiem.query.DetailedAlarm(alarm)
            self.assertEqual(alarm.status, 'acknowledged')

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
            filters=[('DstIP', ['10.0.0.0/8'])],
            limit=1,
            offset=0,
            time_range='LAST_30_MINUTES',
            compute_time_range=False
        )

        events = query.execute()
        log.debug("Got "+str(len(events))+" events !")

        query = msiem.query.EventQuery(
            filters=[('DstIP', ['10.0.0.0/8'])],
            limit=1,
            offset=100,
            time_range='LAST_30_MINUTES',
            compute_time_range=False
        )

        events2 = query.execute()
        log.debug("Got "+str(len(events2))+" events !")

        log.debug(events[0])
        log.debug(events2[0])

        self.assertEqual(events, events2, 'This test will fail if the offset parameter gets fixed on the SIEM side')

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

        self.assertEqual(events, events2, 'Time computed time range and default time range gave differents results. This test can sometimes fail if new events came up in the meantime')

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

        self.assertEqual(events, events2, 'The computation itself is wrong. This test can sometimes fail if new events came up in the meantime')

        pass

    def test_AlarmFilter(self):
        
        with self.assertRaisesRegex(msiem.exceptions.ESMException, 'Illegal filter'):
            filtered = msiem.query.AlarmQuery(
                time_range='LAST_3_DAYS',
                filters=('whatever', None)
            )

        for alarm in (msiem.query.AlarmQuery(
            time_range='LAST_3_DAYS',
            filters=('alarmName', 'High Severity Event')
            ).execute()) :
            self.assertRegex(alarm.alarmName.lower(), 'High Severity Event'.lower(), 'Filtering alarms is not working')

        for alarm in (msiem.query.AlarmQuery(
            time_range='LAST_3_DAYS',
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