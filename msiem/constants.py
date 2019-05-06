# -*- coding: utf-8 -*-
""" 
    msiem constants
"""
BASE_URL = 'https://{}/rs/esm/'
BASE_URL_PRIV = 'https://{}/ess'

ASYNC_MAX_WORKERS=10
GENERAL_POST_TIMEOUT=30

CONFIG_FILE_NAME='.msiem/conf.ini'

DEFAULT_CONFIG_FILE='''
    ; This file should be located in your securely in your path since it 
    ; has credentials.
    ; 
    ; For Windows:  %APPDATA%\\\\'''+CONFIG_FILE_NAME+'''
    ; For Mac :     $HOME/'''+CONFIG_FILE_NAME+'''
    ; For Linux :   $XDG_CONFIG_HOME/'''+CONFIG_FILE_NAME+'''
    ;        or :   $HOME/'''+CONFIG_FILE_NAME+'''

    [general]
    output=text
    verbose=yes
    ssl_verify=no
    log_file=

    ; Use command line to setup authentication
    
    [esm]
    host=
    user=
    passwd=
    '''

POSSIBLE_FIELD_TYPES = [ 'BOOLEAN',
        'STRING',
        'CUSTOM',
        'INT2',
        'INT4',
        'INT8',
        'INT32',
        'INT64',
        'UINT8',
        'UINT16',
        'UINT32',
        'UINT64',
        'IPV4',
        'FLOAT',
        'SIGID',
        'SSTRING',
        'IPTYPE',
        'IP',
        'GUID',
        'MAC_ADDRESS',
        'LONG_CUSTOM',
        'HSTRING',
        'STRLIT',
        'AGG',
        'TIME4',
        'TIME8']

POSSIBLE_OPERATORS=['IN',
        'NOT_IN',
        'GREATER_THAN',
        'LESS_THAN',
        'GREATER_OR_EQUALS_THAN',
        'LESS_OR_EQUALS_THAN',
        'NUMERIC_EQUALS',
        'NUMERIC_NOT_EQUALS',
        'DOES_NOT_EQUAL',
        'EQUALS',
        'CONTAINS',
        'DOES_NOT_CONTAIN',
        'REGEX']

POSSIBLE_VALUE_TYPES=[
        {'type':'EsmWatchlistValue',    'key':'watchlist'},
        {'type':'EsmVariableValue',     'key':'variable'},
        {'type':'EsmBasicValue',        'key':'value'},
        {'type':'EsmCompoundValue',     'key':'values'}]

DEFAULT_TIME_RANGE="LAST_30_MINUTES"
POSSIBLE_TIME_RANGE=[
            "CUSTOM",
            "LAST_MINUTE",
            "LAST_10_MINUTES",
            "LAST_30_MINUTES",
            "LAST_HOUR",
            "CURRENT_DAY",
            "PREVIOUS_DAY",
            "LAST_24_HOURS",
            "LAST_2_DAYS",
            "LAST_3_DAYS",
            "CURRENT_WEEK",
            "PREVIOUS_WEEK",
            "CURRENT_MONTH",
            "PREVIOUS_MONTH",
            "CURRENT_QUARTER",
            "PREVIOUS_QUARTER",
            "CURRENT_YEAR",
            "PREVIOUS_YEAR"
        ]

POSSIBLE_ALARM_STATUS=[
        'acknowledged',
        'unacknowledged',
        '',
        None
    ]
POSSBILE_ROW_ORDER=[
        'ASCENDING',
        'DESCENDING'
]

DEFAULTS_EVENT_FIELDS=[
 "DSIDSigID",
 "SrcPort", 
 "AvgSeverity", 
 "DstPort", 
 "SrcIP", 
 "DstIP", 
 "SrcMac",
 "DstMac", 
 "LastTime"
]

ALARM_FILTER_FIELDS = ['id',
'summary',
'assignee',
'severity',
'triggeredDate',
'acknowledgedDate',
'acknowledgedUsername',
'alarmName']


ALARM_EVENT_FILTER_FIELDS=["eventId",
#"severity", ignored cause duplicated in ALARM_FILTER_FIELD
"ruleMessage",
"eventCount",
"sourceIp",
"destIp",
"protocol",
"lastTime",
"eventSubType"]

