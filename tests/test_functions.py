# -*- coding: utf-8 -*-
import unittest
import requests
from lxml import etree
from io import BytesIO
import tempfile
import os

from msiempy import FieldFilter, GroupFilter, NitroSession

from msiem.cli import (
    alarms_cmd_parse_filters, 
    events_cmd_parse_filters, 
    api_cmd_get_api_docs,
    api_cmd_parse_interpolated_args,
    api_cmd_get_data
)

class T(unittest.TestCase):

    def test_alarms_cmd_parse_filters(self):
        args = [    ["destIp=10.55.16.99", "srcIp=10.55.16.25"],
                    ["ruleName=HTTP: SQL Injection Attempt Detected",],
                    ["HostID=hello=@1234.com",],]

        excepted = [
            ("destIp", "10.55.16.99"),
            ("srcIp", "10.55.16.25"),
            ("ruleName", "HTTP: SQL Injection Attempt Detected"),
            ("HostID", "hello=@1234.com"),
        ]

        self.assertEqual(alarms_cmd_parse_filters(args), excepted, msg="Alarms --filters parsing is broken")
    
        with self.assertRaises(ValueError, msg="Alarms --filters parsing do not raise execption when passing invalid filter"):
            alarms_cmd_parse_filters([["invalid:my val"]])

    
    def test_events_cmd_parse_filters(self):
        args = [    [   "DstIP=10.55.16.99", 
                        "SrcIP=10.0.0.0/8", 
                        "Rule.msg=HTTP: SQL Injection Attempt Detected", 
                        "severity=90"],
                    ["HostID=hello=@1234.com",],
                    ["HostID", "REGEX", ".*"],
                    ["DstIP", "NOT_IN", "22.0.0.0/8", "55.0.0.0/8"]
                ]
        excepted = [
            ("DstIP", "10.55.16.99"),
            ("SrcIP", "10.0.0.0/8"),
            ("Rule.msg", "HTTP: SQL Injection Attempt Detected"),
            ("severity", "90"),
            ("HostID", "hello=@1234.com"),
            GroupFilter([
                FieldFilter(name="HostID", values=[".*"], operator='REGEX'),
                FieldFilter(name="DstIP", values=["22.0.0.0/8", "55.0.0.0/8"], operator='NOT_IN'),
                ], logic='AND')
        ]
        print(events_cmd_parse_filters(args))
        self.assertEqual(events_cmd_parse_filters(args), excepted, msg="Events --filters parsing is broken")

        with self.assertRaises(ValueError, msg="Events --filters parsing do not raise execption when passing invalid filter"):
            events_cmd_parse_filters([["invalid:my val"]])


    def test_api_cmd_get_api_docs(self):
        s=NitroSession()
        help_page = etree.parse(BytesIO(requests.get('https://{esm_url}/rs/esm/v2/help'.format(esm_url=s.config.host), verify=s.config.ssl_verify).text.encode()))
        endpoints = [e.get('name') for e in help_page.iter() if 'esmCommand' in e.tag and e.get('name')]

        for index, line in enumerate(api_cmd_get_api_docs().splitlines()):
            self.assertIn(endpoints[index], line, "API ---list option broken")


    def test_api_cmd_parse_interpolated_args(self):
        args = [    ["destIp=10.55.16.99", "srcIp=10.55.16.25"],
                    ["ruleName=HTTP: SQL Injection Attempt Detected",],
                    ["HostID=hello=@1234.com",],]

        excepted = {
            "destIp": "10.55.16.99",
            "srcIp": "10.55.16.25",
            "ruleName": "HTTP: SQL Injection Attempt Detected",
            "HostID": "hello=@1234.com"
        }
        

        self.assertEqual(api_cmd_parse_interpolated_args(args), excepted, msg="API --args parsing is broken")

        with self.assertRaises(ValueError, msg="API --args parsing do not raise execption when passing invalid value"):
            api_cmd_parse_interpolated_args([["invalid:my val"]])


    def test_api_cmd_get_data(self):
        data = '["1","2","3"]'
        self.assertEqual(api_cmd_get_data(data), ["1","2","3"])
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            f.write('["1","2","3"]')
            fname = f.name
        self.assertEqual(api_cmd_get_data(fname), ["1","2","3"])
        os.remove(fname)