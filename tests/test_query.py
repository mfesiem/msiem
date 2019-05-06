# -*- coding: utf-8 -*-=
"""
    test_query
"""

import unittest
import msiem
import msiem.query
from msiem.session import ESMSession
from msiem.utils import log, getTimes
import os

class Tests(unittest.TestCase):

    def test_QueryBase(self):
        #1
        query = msiem.query.TestingQuery(time_range='LAST_MINUTE')
        self.assertEqual('LAST_MINUTE', query.time_range, 'time range is not set uppon init')

        #2
        query = msiem.query.TestingQuery(time_range='CURRENT_YEAR')
        self.assertEqual('CURRENT_YEAR', query.time_range, 'time range is not set uppon setter call')

        #3
        query = msiem.query.TestingQuery(time_range='CUSTOM',
            start_time='2019-01-01T12:00',
            end_time='2019-01-15T12:00')

        self.assertEqual('CUSTOM', query.time_range, 'custom time range is not set uppon setter call')
        self.assertEqual('2019-01-01T12:00', query.start_time, 'start time is not set uppon setter call')
        self.assertEqual('2019-01-15T12:00', query.end_time, 'end time is not set uppon setter call')

        #4
        query = msiem.query.TestingQuery(time_range='LAST_MINUTE')
        with self.assertRaisesRegex(msiem.exceptions.ESMException,"The time range must be in"):
            query.time_range='impossible time range'
        
        #5
        query = msiem.query.TestingQuery(time_range='LAST_MINUTE')
        with self.assertRaisesRegex(msiem.exceptions.ESMException,"The time range must be 'CUSTOM' if you want to specify a custom start time"):
            query.start_time='1999-01-01'

        #6
        query = msiem.query.TestingQuery(time_range='LAST_MINUTE')
        with self.assertRaisesRegex(msiem.exceptions.ESMException,"The time range must be 'CUSTOM' if you want to specify a custom end time"):
            query.end_time='1999-01-01'

        #7
        with self.assertRaisesRegex(msiem.exceptions.ESMException,"Not implemented"):
            msiem.query.TestingQuery(
                time_range='CUSTOM',
                start_time='2019-01-01T14:32',
                end_time='2019-02-01T12:00'
            ).execute()

    def test_AlarmQuery(self):

        #1
        query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS')
        query.status='acknowledged'
        self.assertEqual('acknowledged', query.status, 'query status is not set uppont setter call')

        #2
        query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS')
        query.page_size=100
        self.assertEqual(100, query.page_size, 'query page size is not set uppont setter call')

        #3
        query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS')
        query.page_number=55
        self.assertEqual(55, query.page_number, 'query page number is not set uppont setter call')

        #4
        query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS')
        with self.assertRaisesRegex(msiem.exceptions.ESMException, "Illegal value of status filter."):
            query.status='impossible status filter'

        #5
        query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS')
        with self.assertRaisesRegex(msiem.exceptions.ESMException, "The page size must be in 0-5000"):
            query.page_size=5005

        #6 This test will fail if you don't have new alarms in the siem for 30 minutes
        alarms=msiem.query.AlarmQuery(time_range='LAST_3_DAYS').execute()
        self.assertGreater(len(alarms),0)
        
    def test_Alarm(self):
        
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

    def test_Filter(self):
        f = msiem.query.FieldFilter(
            name="SrcIP", 
            operator='IN',
            values=[
                {'type':'EsmBasicValue', 'value':'10.1.1.1'},
                {'type':'EsmVariableValue', 'variable':5}
            ])

        self.assertEqual(f.configDict(), {
            "type": "EsmFieldFilter",
            "field": {"name": "SrcIP"},
            "operator": "IN",
            "values": [{
                "type": "EsmBasicValue",
                "value": "10.1.1.1"
                },{
                "type": "EsmVariableValue",
                "variable": 5
                }]
            }
        )

        f = msiem.query.GroupFilter(
                msiem.query.FieldFilter(
                    name="SrcIP", 
                    operator='IN',
                    values=[
                        {'type':'EsmBasicValue', 'value':'10.1.1.1'},
                    ]),
                msiem.query.FieldFilter(
                    name="DstIP", 
                    operator='IN',
                    values=[
                        {'type':'EsmBasicValue', 'value':'222.0.25.1'},
                    ]),
                msiem.query.GroupFilter(
                    msiem.query.FieldFilter(
                        name="SigID", 
                        operator='CONTAINS',
                        values=[
                            {'type':'EsmBasicValue', 'value':'123'},
                    ]),
                    msiem.query.FieldFilter(
                        name="Description", 
                        operator='CONTAINS',
                        values=[
                            {'type':'EsmBasicValue', 'value':'Critical'},
                    ]),
                    logic='AND',
                ),
                logic='OR'
            )

        self.assertEqual(f.configDict(), {
            "type": "EsmFilterGroup",
            "logic":"OR",
            "filters":[
                {
                    "type":"EsmFieldFilter",
                    "field": {"name": "SrcIP"},
                    "operator": "IN",
                    "values": [{
                        "type": "EsmBasicValue",
                        "value": "10.1.1.1"
                        }]
                },
                {
                    "type":"EsmFieldFilter",
                    "field": {"name": "DstIP"},
                    "operator": "IN",
                    "values": [{
                        "type": "EsmBasicValue",
                        "value": "222.0.25.1"
                        }]
                },
                {
                    "type": "EsmFilterGroup",
                    "logic":"AND",
                    "filters":[
                        {
                            "type":"EsmFieldFilter",
                            "field": {"name": "SigID"},
                            "operator": "CONTAINS",
                            "values": [{
                                "type": "EsmBasicValue",
                                "value": "123"
                                }]
                        },
                        {
                            "type":"EsmFieldFilter",
                            "field": {"name": "Description"},
                            "operator": "CONTAINS",
                            "values": [{
                                "type": "EsmBasicValue",
                                "value": "Critical"
                            }]
                        },
                        
                    ]
                }
            ]
            
            }
        )

        f = msiem.query.FieldFilter('SrcIP', ['10.1.1.0', '10.1.1.3'])

        self.assertEqual(f.configDict(), {
            "type": "EsmFieldFilter",
            "field": {"name": "SrcIP"},
            "operator": "IN",
            "values": [{
                "type": "EsmBasicValue",
                "value": "10.1.1.0"
                },{
                "type": "EsmBasicValue",
                "value": "10.1.1.3"
                }]
            }
        )

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


if __name__ == '__main__':
    unittest.main()
