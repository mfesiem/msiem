# -*- coding: utf-8 -*-=
"""
    test_query
"""

import unittest
import time
import msiem
import msiem.query
from msiem.utils import log, getTimes

class Tests(unittest.TestCase):

    def test_QueryBase(self):
        

        query = msiem.query.TestingQuery(time_range='CUSTOM',
            start_time='2019-01-01T12:00',
            end_time='2019-01-15T12:00')

        self.assertEqual('CUSTOM', query.time_range, 'custom time range is not set uppon setter call')
        self.assertEqual('2019-01-01T12:00', query.start_time, 'start time is not set uppon setter call')
        self.assertEqual('2019-01-15T12:00', query.end_time, 'end time is not set uppon setter call')
        
        query = msiem.query.TestingQuery(time_range='LAST_MINUTE')
        with self.assertRaisesRegex(msiem.exceptions.ESMException,"The time range must be in"):
            query.time_range='impossible time range'
        
        query = msiem.query.TestingQuery(time_range='LAST_MINUTE')
        with self.assertRaisesRegex(msiem.exceptions.ESMException,"The time range must be 'CUSTOM' if you want to specify a custom start time"):
            query.start_time='1999-01-01'
        
        with self.assertRaisesRegex(msiem.exceptions.ESMException,"Not implemented"):
            msiem.query.TestingQuery(
                time_range='CUSTOM',
                start_time='2019-01-01T14:32',
                end_time='2019-02-01T12:00'
            ).execute()

    def test_AlarmQuery(self):
        
        with self.assertRaisesRegex(msiem.exceptions.ESMException, "Illegal value of status filter."):
            query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS', status='impossible status')
        
        with self.assertRaisesRegex(msiem.exceptions.ESMException, "The page size must be in 0-5000"):
            query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS', page_size=5005)

        with self.assertRaisesRegex(msiem.exceptions.ESMException, "Illegal filter"):
            query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS', filters=('impossible fielsd', 'impossible value'))

        query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS', 
            filters=[
                ('summary', 'important'),
                ('sourceIp', ['10.165', '10.168'])
                ])
        self.assertIn(('summary', ['important']), query._alarm_filters, "Issue when setting alarm filter")
        self.assertIn(('sourceIp', ['10.165', '10.168']), query._event_filters, "Issue when setting event filter")

        query = msiem.query.AlarmQuery(time_range='LAST_3_DAYS', filters=('summary', 'important'))
        a1=msiem.query.Alarm(summary='who cares')
        a2=msiem.query.Alarm(summary='very important')
        a3=msiem.query.Alarm(summary='normal')
        a4=msiem.query.Alarm(summary='a little bit important')
        filtered = query._filter([a1,a2,a3,a4])
        self.assertNotIn(a1, filtered, 'Basic alarm field based filter is not working.')
        self.assertNotIn(a3, filtered, 'Basic alarm field based filter is not working.')
        self.assertIn(a2, filtered, 'Basic alarm field based filter is not working.')
        self.assertIn(a4, filtered, 'Basic alarm field based filter is not working.')

    def test_EventFilter(self):
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
                logic='OR',
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
        
if __name__ == '__main__':
    unittest.main()
