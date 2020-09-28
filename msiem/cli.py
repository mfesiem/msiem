# -*- coding: utf-8 -*-
"""
CLI
"""

import argparse
import json
import sys
from urllib.parse import urlparse
from string import Template

import textwrap as _textwrap
from pprint import pprint
import requests
from lxml import etree
from io import BytesIO

from msiempy.core.utils import tob64
from msiempy import FilteredQueryList, NitroConfig, AlarmManager, Alarm, EventManager, FieldFilter, Event, ESM, NitroSession

from msiem.__version__ import __version__
from msiem.__pathutils__ import is_path_exists_or_creatable
from msiem.dstools import dstools

class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    def _split_lines(self, text, width):
        text = self._whitespace_matcher.sub(' ', text).strip()
        return _textwrap.wrap(text, 80)

DEFAULT_ALARM_FIELDS=['alarmName','triggeredDate', 'acknowledgedDate', 'events']
DEFAULT_EVENT_FIELDS=['ruleName', 'srcIp', 'destIp' ]
DEFAULT_EVENT_FIELDS_QUERY=['Rule.msg', 'Alert.SrcIP', 'Alert.DstIP' ]

def get_parser():
    parser = argparse.ArgumentParser(description="""McAfee SIEM Command Line Interface {msiem_version}  

    License: MIT  
    Credits: Andy Walden, Tristan Landes  

Run 'msiem <command> --help' for more information about a sub-command.""".format(
        msiem_version=__version__,),
        prog='msiem',
        formatter_class=Formatter,)

    
    # parser.add_argument('-v', '--verbose', help="Increase output verbosity",action="store_true")

    commands = parser.add_subparsers(dest='command')
    parser.add_argument('-V', '--version', help="Show version and exit", action="store_true")

    ### CONFIG ###
    config = commands.add_parser('config', formatter_class=Formatter, help="Set and print your msiempy config.  ", description=config_cmd.__doc__)
    config.set_defaults(func=config_cmd)
    config.add_argument('--print', help="Print configuration fields, password base 64 included. ", action="store_true")
    config.add_argument('--set', metavar="'<section>' ['<option>' '<value>']", help="Set the config option to the specified value if passed (can be repeated), OR inveractively prompt for specified configuration section: 'esm' or 'general'.", action='append', nargs='+', default=[])


    ### ALARMS ###
    alarm = commands.add_parser('alarms', formatter_class=Formatter, help="Query alarms with alarms and events based regex filters. Print, acknowledge, unacknowledge and delete alarms.  ", description=alarms_cmd.__doc__)
    alarm.set_defaults(func=alarms_cmd)
    alarm.add_argument('--action', metavar="action", help="What to do with the alarms, if not specified will print only. Chose from 'acknowledge','unacknowledge','delete'", 
        choices=['acknowledge','unacknowledge','delete'])
    alarm.add_argument('--force', help="Will not prompt for confirmation to do the specified action", action="store_true")
    alarm.add_argument('--time_range','-t', metavar='time_range', help='Timerange, choose from '+', '.join(FilteredQueryList.POSSIBLE_TIME_RANGE),  
        choices=FilteredQueryList.POSSIBLE_TIME_RANGE, default='CURRENT_DAY')
    alarm.add_argument('--start_time','--t1', metavar='time', help='Start trigger date')
    alarm.add_argument('--end_time','--t2', metavar='time', help='End trigger date')
    alarm.add_argument('--status', metavar='status', help="Status of the alarm. Chose from 'acknowledged','unacknowledged','all'",choices=['acknowledged','unacknowledged','all'], default='all')
    alarm.add_argument('--filters', '-f', metavar="'<field>=<match>'", action='append', nargs='+', help="""List of alarm related field/matchvalue filters. Repeatable. 
    Alarm related fields can be : id, summary, assignee, severity, triggeredDate, acknowledgedDate, acknowledgedUsername, alarmName, events, and others""", default=[[]])
    alarm.add_argument('--event_filters', '-e', metavar="'<field>=<match>'", action='append', nargs='+', help="""List of triggering event related field/matchvalue filters. Repeatable.
    Event related fields can be : ruleName, srcIp, destIp, protocol, lastTime, subtype, destPort, destMac, srcMac, srcPort, deviceName, sigId, normId, srcUser, destUser, normMessage, normDesc, host, domain, ipsId, etc...
    Or (if --query_events) : Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID, etc...""", default=[[]])
    alarm.add_argument('--alarms_fields', metavar="list of fields", nargs='+', help="List of fields that appear in the alarm table. Overwritten by --json", default=DEFAULT_ALARM_FIELDS)
    alarm.add_argument('--events_fields', metavar="list of fields", nargs='+', help="List of fields that appear in the events sub tables. Default value: {}. If you use --query_events, this list will be used to query needed values, you must specify all fields you want to filter on with ewvent_filters. Default value if --query_events: {}. Overwritten by --json.".format(DEFAULT_EVENT_FIELDS, DEFAULT_EVENT_FIELDS_QUERY), default=None)
    alarm.add_argument('--json', action='store_true', help="Prints the raw json object with all loaded fields")
    alarm.add_argument('--page_size', '-p', metavar='page_size', help='Size of requests', default=500, type=int)
    alarm.add_argument('--pages', '-n', metavar='pages', help='Number of alarm pages to load', default=1, type=int)
    alarm.add_argument('--workers', metavar="workers", help='Number of max asynch workers', default=10, type=int)
    alarm.add_argument('--no_events', help='Do not load the complete trigerring events informations.', action="store_true")
    alarm.add_argument('--query_events', help="Use the query module to retreive events, much more effcient. Event keys will be like 'Alert.SrcIP' instead of 'srcIp'", action="store_true")

    ### ESM ###
    esm_parser = commands.add_parser('esm', formatter_class=Formatter, help="Show ESM version and misc informations regarding your ESM.  ", description=esm_cmd.__doc__)
    esm_parser.set_defaults(func=esm_cmd)
    esm_parser.add_argument('--version', help='Show ESM version', action="store_true")
    esm_parser.add_argument('--time', help='time (GMT)', action="store_true")
    esm_parser.add_argument('--disks', help='disk status', action="store_true")
    esm_parser.add_argument('--ram', help='ram status', action="store_true")
    esm_parser.add_argument('--callhome', help='True/False if callhome is active/not active', action="store_true")
    esm_parser.add_argument('--status', help='Statuses and a few other less interesting details : autoBackupEnabled, autoBackupDay, backupLastTime, backupNextTime, rulesAndSoftwareCheckEnabled, rulesAndSoftLastCheck, rulesAndSoftNextCheck', action="store_true")
    esm_parser.add_argument('--timezones', help='Current ESM timezone', action="store_true")


    ### DS ###
    ds_parser = commands.add_parser('ds', formatter_class=Formatter, help="Add datasources from CSV or INI files, list, search, remove.  ", description=ds_cmd.__doc__)
    ds_parser.add_argument( '-a', '--add', metavar='<file or folder>', help=   'Scan a directory or a file for new Datasource files and add them to the ESM. '
                                                                                'Datasources can be defined in CSV or INI format (see README.md).  ')        
    ds_parser.add_argument( '-s', '--search' ,  nargs='?', default=None, metavar='term',
                             help='Search for datasource name, hostname, or IP.'
                                   'May require quotes around the name if there'
                                   'are spaces.')
    ds_parser.add_argument( '-l', '--list', action="store_true" ,help='Display datasources.')
    ds_parser.add_argument( '--delete', metavar='<datasource ID>', help='Deletes the datasource and all the data. Be careful.', nargs='+')
    ds_parser.add_argument( '--deleteclients', metavar='<datasource ID>', help="Deletes the datasource's clients and all the data. Be careful.", nargs='+')
    ds_parser.add_argument( '--force', action='store_true', help="Do not ask the user input before deletion of the datasources / datasources client.")


    ### EVENTS 
    ### todo
    events_parser = commands.add_parser('events', formatter_class=Formatter, help="Query events with any simple filter. Add a note to events.  ", description=events_cmd.__doc__)
    events_parser.add_argument('--time_range','-t', metavar='time_range', help='Timerange, choose from '+', '.join(FilteredQueryList.POSSIBLE_TIME_RANGE),  
        choices=FilteredQueryList.POSSIBLE_TIME_RANGE, default='CURRENT_DAY')
    events_parser.add_argument('--start_time','--t1', metavar='time', help='Start trigger date')
    events_parser.add_argument('--end_time','--t2', metavar='time', help='End trigger date')
    events_parser.add_argument('--filters', '-f', metavar="<filter>", action='append', nargs='+', help="""List of Event field/value filters: '<field>=<value>' or '<field>' '<operator>' '<value1>' '<value2>...'. Repeatable. Will generate only EsmBasicValue filters.   
    Filter fields can be: Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID, etc...""", default=[[]])
    events_parser.add_argument('--fields', metavar="<field>", nargs='+', help="List of fields that appear in the events table. Default value: {}. ".format(DEFAULT_EVENT_FIELDS_QUERY), default=None)
    events_parser.add_argument('--json', action='store_true', help="Prints the raw json object with all loaded fields")
    events_parser.add_argument('--limit', metavar='limit', help='Size of requests', default=500, type=int)

    ### API ###
    api_parser = commands.add_parser('api', formatter_class=Formatter, help="Quickly make API requests to any enpoints with any data.  ", description=api_cmd.__doc__)
    api_parser.add_argument('-m','--method', metavar='<method>', help="SIEM API method name or NitroSession.PARAMS keyword. Exemple: 'v2/qryGetSelectFields' or 'get_possible_fields', see 'msiem api --list' for full details .")
    api_parser.add_argument('-d','--data', metavar='<JSON string or file>', help='POST data, in the case of a API method name call.  See the SIEM API docs for full details.  ', default={})
    api_parser.add_argument('-a', '--args', metavar='<key>=<value>', help="Interpolation parameters, in the case of a NitroSession.PARAMS keyword call.  See 'msiem api --list' for full details.  ", action='append', nargs='+', default=[[]])
    api_parser.add_argument('-l', '--list', action='store_true', help='List all available SIEM API calls as well as all supported calls with keywords and parameter mapping. ' )

    return parser

def parse_msiem_cli_args():
    return (get_parser().parse_args())

def config_cmd(args):
    """
Set and print your msiempy config.  
    """

    conf=NitroConfig() # ConfigParser object

    if len(args.set)>0:
        for setting in args.set:
            if len(setting)==1:
                conf.iset(setting[0])
            elif len(setting)==3:
                if setting[1] == 'passwd':
                    setting[2]=tob64(setting[2])
                conf.set(setting[0], setting[1], setting[2])
            else:
                raise ValueError("'--set' argument accept 1 or 3 values: '<section>' or '<section>' '<option>' '<value>'. Not {}".format(setting))

        conf.write()

    if args.print:
        pprint(conf._sections)

def alarms_cmd(args):
    """
Query alarms with alarms and events based regex filters.  
Print, acknowledge, unacknowledge and delete alarms.  

Exemples:  

Acknowledges the (unacknowledged) alarms triggered in the last 
3 days that mention "HTTP: SQL Injection Attempt Detected" in 
the triggered event name and destinated to 10.55.16.99 :

    $ msiem alarms --action acknowledge \\
    -t LAST_24_HOURS \\
    --status unacknowledged \\
    --filters \\
        "ruleName=HTTP: SQL Injection Attempt Detected" \\
        "destIp=10.55.16.99"

Prints the alarms triggered in the last hour using the query 
module to retreive events informations and request for 
specific fields :

    $ msiem alarms -t LAST_HOUR \\
    --query_events \\
    --alarms_fields acknowledgedDate alarmName events \\
    --events_fields Alert.LastTime Rule.msg Alert.DstIP
    """

    filters = [item for sublist in args.filters for item in sublist]
    event_filters = [item for sublist in args.event_filters for item in sublist]

    alarms=AlarmManager(
        time_range=args.time_range,
        start_time=args.start_time,
        end_time=args.end_time,
        status_filter=args.status,
        filters=[((item.split('=',1)[0],item.split('=',1)[1])) for item in filters if len(item.split('=',1)[1])>0],
        event_filters=[((item.split('=',1)[0],item.split('=',1)[1])) for item in event_filters if len(item.split('=',1)[1])>0],
        page_size=args.page_size,
    )

    event_fields=[]
    if args.events_fields == None :
        if args.query_events : 
            event_fields=DEFAULT_EVENT_FIELDS_QUERY
        else : 
            event_fields=DEFAULT_EVENT_FIELDS
    else : 
        event_fields=args.events_fields

    alarms.load_data(
        workers=args.workers,
        events_details = not args.no_events,
        use_query = args.query_events,
        extra_fields=event_fields,
        pages=args.pages
    )
    if args.json:
        text = alarms.json
    else: 
        text=alarms.get_text(fields=args.alarms_fields, 
            get_text_nest_attr=dict(max_column_width=40, fields=event_fields))
           
    print(text)
        
    if args.action is not None :
        if args.force or ('y' in input('Are you sure you want to '+str(args.action)+' those alarms ? [y/n]')):
            alarms.perform(getattr(Alarm, args.action), progress=True)

def esm_cmd(args):
    """
Show ESM version and misc informations regarding your ESM."""
    esm = ESM()
    vargs=vars(args)
    for k,v in vargs.items() :
        if v == True and hasattr(esm, k):
            pprint(getattr(esm, k)())

def ds_cmd(args):
    """
Add datasources from CSV or INI files, list, search, remove.  

INI format: Single datasource per file.  

        
    [datasource]
    # name of datasource (req)
    name=testing_datasource
    # ip of datasource (ip or hostname required)
    ds_ip=10.10.1.34
    # hostname of te new datasource
    hostname=
    # type of datasource (req)
    type_id=65
    # id of parent device (req)
    parent_id=144116287587483648
    # True value designate a client datasource 
    client=


CSV Format: Multiple datasources per file


    name,ds_ip,hostname,type_id,parent_id,client
    Test_ds_1,10.10.1.41,datasource11.domain.com,65,144116287587483648,
    Test_ds_2,10.10.1.42,datasource12.domain.com,65,144116287587483648,
    Test_ds_3,10.10.1.43,datasource13.domain.com,65,144116287587483648,


Add Datasources with: 

        $ msiem ds --add <file or folder>
    """
    dstools(args)

def events_cmd(args):
    """
Query events with filters, add note to events.  

With simpler filter:

    $ msiem events --filter DstIP=127.0.0.1 --field SrcIP DstIP   


Specific operatior and multiple values filter:

    $ msiem events --filter \\
        SrcIP IN 22.0.0.0/8 10.0.0.0/8 \\
        --fields SrcIP DstIP
    """

    filters = [item for sublist in args.filters for item in sublist if len(sublist)!=3]

    filters = [((item.split('=',1)[0],item.split('=',1)[1])) for item in filters if len(item.split('=',1))==2]

    filters.extend([FieldFilter(name=sublist[0], operator=sublist[1], values=sublist[2:]) for sublist in args.filters if len(sublist)>=3 and sublist[1] in FieldFilter.POSSIBLE_OPERATORS])

    events=EventManager(
        time_range=args.time_range,
        start_time=args.start_time,
        end_time=args.end_time,
        filters=filters if filters else None,
        fields=args.fields,
        limit=args.limit,
    )

    events.load_data()
    if args.json:
        text = events.json
    else: 
        text=events.text
           
    print(text)

def wl_cmd(args):
    """
Watchlist operations. Not implemented yet.  
    """
    pass

def api_cmd(args):
    """
Quickly make API requests to any enpoints with any data.  

Exemple:

$ msiem api --method \\
    "v2/alarmGetTriggeredAlarms?triggeredTimeRange=LAST_24_HOURS&status=&pageSize=500&pageNumber=1" \\
    --data {}   
    """
    
    s=NitroSession()
    s.login()
    if args.list:

        help_page = etree.parse(BytesIO(requests.get('https://{esm_url}/rs/esm/v2/help'.format(esm_url=s.config.host), verify=s.config.ssl_verify).text.encode()))
        endpoints = [e.get('name') for e in help_page.iter() if 'esmCommand' in e.tag and e.get('name')]

        API_DOCS = ""
        for endp in endpoints:
            API_DOCS += "msiem api --method v2/{} --data <JSON string or file>\n".format(endp)
        
        print("All possible SIEM requests: ")
        print(API_DOCS)

        PARAMS_DOCS = ""
        for k, v in s.PARAMS.items():
            name = "{}".format(k)
            keywords = []
            params = ""
            endpoint = "{}".format(
                urlparse(v[0] if not isinstance(v[0], Template) else v[0].template).path
            )
            if isinstance(v[0], Template):
                keywords += [
                    s[1] or s[2]
                    for s in Template.pattern.findall(v[0].template)
                    if s[1] or s[2]
                ]
            if isinstance(v[1], Template):
                keywords += [
                    s[1] or s[2]
                    for s in Template.pattern.findall(v[1].template)
                    if s[1] or s[2]
                ]
            params = " ".join(["{}=<value>".format(k) for k in keywords])
            PARAMS_DOCS += "msiem api --method '{}' {} # Call {}  \n".format(
                name, '--args '+params if params else params, endpoint
            )

        print("Requests with API parameters interpolation")
        print(PARAMS_DOCS)

        exit(0)

    if args.method:
        if args.method in s.PARAMS.keys():
            request_args = [item for sublist in args.args for item in sublist]
            request_args = {item.split('=',1)[0]:item.split('=',1)[1] for item in request_args}
            res = s.request(args.method, **request_args)
        else:
            data=None
            
            if args.data:
                try:
                    data = json.loads(args.data)
                except ValueError:
                    if is_path_exists_or_creatable(args.data):
                        with open(args.data, 'r') as d:
                            data = json.load(d)
                    else:
                        raise

            res = s.api_request(args.method, data)

        pprint(res)


def print_version_and_exit():
    print('msiem {}'.format(__version__))
    exit(0)

def main():
    
    try:
        args = parse_msiem_cli_args()

        if args.command == 'config' :
            config_cmd(args)
        elif args.command == 'alarms' :
            alarms_cmd(args)
        elif args.command == 'events' :
            events_cmd(args)
        elif args.command == 'esm':
            esm_cmd(args)
        elif args.command == 'ds':
            ds_cmd(args)
        elif args.command == 'api':
            api_cmd(args)
        elif args.command == 'wl':
            wl_cmd(args)
        else :
            if args.version:
                print_version_and_exit()
                
            print('McAfee SIEM Command Line Interface.\nRun "msiem --help" for more information.')
    
    except KeyboardInterrupt:
        print("Control-C Pressed, stopping...")
        exit(-1)

if __name__ == "__main__":
    main()


