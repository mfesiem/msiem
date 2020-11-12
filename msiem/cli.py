# -*- coding: utf-8 -*-
"""
msiem CLI
"""

import argparse
import json
import sys
from urllib.parse import urlparse
from string import Template

import textwrap as _textwrap
import requests
from lxml import etree
from io import BytesIO

from msiempy.core.utils import tob64
from msiempy import ( 
    FilteredQueryList, 
    NitroConfig, 
    AlarmManager, 
    Alarm, 
    EventManager, 
    FieldFilter, 
    GroupFilter, 
    Event, 
    ESM, 
    NitroSession, 
    WatchlistManager, 
    Watchlist 
)

from msiem.__version__ import __version__
from msiem.__pathutils__ import is_path_exists_or_creatable
from msiem.dstools import dstools

class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    def _split_lines(self, text, width):
        text = self._whitespace_matcher.sub(' ', text).strip()
        return _textwrap.wrap(text, 100)

DEFAULT_ALARM_FIELDS=['alarmName','triggeredDate', 'acknowledgedDate', 'events']
DEFAULT_EVENT_FIELDS=['ruleName', 'srcIp', 'destIp' ]
DEFAULT_EVENT_FIELDS_NOTIF_DETAIL=['ruleMessage', 'sourceIp', 'destIp' ]
DEFAULT_EVENT_FIELDS_QUERY=['Rule.msg', 'SrcIP', 'DstIP' ]

def pprint_json(obj):
    print(json.dumps(obj, indent=2))

def get_parser():
    parser = argparse.ArgumentParser(description="""McAfee SIEM Command Line Interface {msiem_version}.
Most of the core msiempy features accessible with CLI.    

License: MIT. 
Credits: Andy Walden, Tristan Landes.

Run `msiem <command> --help` for more information about a sub-command.""".format(
        msiem_version=__version__,),
        prog='msiem',
        formatter_class=Formatter,)

    commands = parser.add_subparsers(dest='command')

    # Global arguments
    parser.add_argument('-V', '--version', help="Show version and exit", action="store_true")   
    
    ### CONFIG ###
    config_parser = commands.add_parser('config', formatter_class=Formatter, help="Set and print your msiempy config.  ", description=config_cmd.__doc__)
    config_parser.add_argument('--print', help="Print configuration fields, password base 64 truncated from the output. ", action="store_true")
    config_parser.add_argument('--set', metavar="'<section>' ['<option>' '<value>']", help="Set the config option to the specified value if passed (can be repeated), OR inveractively prompt for specified configuration section: 'esm' or 'general'.", action='append', nargs='+', default=[])

    ### ALARMS ###
    alarms_parser = commands.add_parser('alarms', formatter_class=Formatter, help="Query alarms with alarms and events based regex filters. Print, acknowledge, unacknowledge and delete alarms.  ", description=alarms_cmd.__doc__)
    alarms_parser.add_argument('--action', metavar="action", help="What to do with the alarms, if not specified will print only. Chose from 'acknowledge','unacknowledge','delete'", 
        choices=['acknowledge','unacknowledge','delete'])
    alarms_parser.add_argument('--force', help="Will not prompt for confirmation to do the specified action", action="store_true")
    alarms_parser.add_argument('--time_range','-t', metavar='time_range', help='Timerange, choose from '+', '.join(FilteredQueryList.POSSIBLE_TIME_RANGE),  
        choices=FilteredQueryList.POSSIBLE_TIME_RANGE, default='CURRENT_DAY')
    alarms_parser.add_argument('--start_time','--t1', metavar='time', help='Start trigger date')
    alarms_parser.add_argument('--end_time','--t2', metavar='time', help='End trigger date')
    alarms_parser.add_argument('--status', metavar='status', help="Status of the alarm. Chose from 'acknowledged','unacknowledged','all'",choices=['acknowledged','unacknowledged','all'], default='all')
    alarms_parser.add_argument('--filters', '-f', metavar="'<field>=<regex>'", action='append', nargs='+', help="""List of alarm related field/matchvalue filters. Repeatable. 
    Alarm related fields can be : id, summary, assignee, severity, triggeredDate, acknowledgedDate, acknowledgedUsername, alarmName, events, and others""", default=[[]])
    alarms_parser.add_argument('--event_filters', '-e', metavar="'<field>=<regex>'", action='append', nargs='+', help="""List of triggering event related field/matchvalue filters. Repeatable.
    Event related fields can be : ruleName, srcIp, destIp, protocol, lastTime, subtype, destPort, destMac, srcMac, srcPort, deviceName, sigId, normId, srcUser, destUser, normMessage, normDesc, host, domain, ipsId, etc...
    Or (if --query_events) : Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID, etc...""", default=[[]])
    alarms_parser.add_argument('--alarms_fields', metavar="list of fields", nargs='+', help="List of fields that appear in the alarm table. Overwritten by --json", default=DEFAULT_ALARM_FIELDS)
    alarms_parser.add_argument('--events_fields', metavar="list of fields", nargs='+', help="List of fields that appear in the events sub tables. Default value: {}. If you use --query_events, this list will be used to query needed values, you must specify all fields you want to filter on with ewvent_filters. Default value if --query_events: {}. Overwritten by --json.".format(DEFAULT_EVENT_FIELDS, DEFAULT_EVENT_FIELDS_QUERY), default=None)
    alarms_parser.add_argument('--json', action='store_true', help="Prints only a JSON object to STDOUT output.  ")
    alarms_parser.add_argument('--page_size', '-p', metavar='page_size', help='Size of requests', default=500, type=int)
    alarms_parser.add_argument('--pages', '-n', metavar='pages', help='Number of alarm pages to load', default=1, type=int)
    alarms_parser.add_argument('--no_events', help='Do not load the complete trigerring events informations. On SIEM v11.x, still load the events infos from notifyGetTriggeredNotification. (Else events field is a string).  ', action="store_true")
    alarms_parser.add_argument('--query_events', help="Use the query module to retreive events, much more effcient. Event keys will be like 'Alert.SrcIP' instead of 'srcIp'", action="store_true")

    ### ESM ###
    esm_parser = commands.add_parser('esm', formatter_class=Formatter, help="Show ESM version and misc informations regarding your ESM.  ", description=esm_cmd.__doc__)
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
                                                                                'Datasources can be defined in CSV or INI format.  ')        
    ds_parser.add_argument( '-s', '--search' ,  nargs='?', default=None, metavar='term',
                             help='Search for datasource name, hostname, or IP.'
                                   'May require quotes around the name if there'
                                   'are spaces.')
    ds_parser.add_argument( '-l', '--list', action="store_true" ,help='Display datasources.')
    ds_parser.add_argument( '--delete', '--remove', metavar='<datasource ID>', help='Deletes the datasource and all the data. Be careful.', nargs='+')
    ds_parser.add_argument( '--deleteclients', metavar='<datasource ID>', help="Deletes the datasource's clients and all the data. Be careful.", nargs='+')
    ds_parser.add_argument( '--force', action='store_true', help="Do not ask the user input before deletion of the datasources / datasources client.")


    ### EVENTS 
    events_parser = commands.add_parser('events', formatter_class=Formatter, help="Query events with any simple filter. Add a note to events.  ", description=events_cmd.__doc__)
    
    events_parser.add_argument('--time_range','-t', metavar='time_range', help='Timerange, choose from '+', '.join(FilteredQueryList.POSSIBLE_TIME_RANGE),  
        choices=FilteredQueryList.POSSIBLE_TIME_RANGE, default='CURRENT_DAY')
    events_parser.add_argument('--start_time','--t1', metavar='<time>', help='Start trigger date')
    events_parser.add_argument('--end_time','--t2', metavar='<time>', help='End trigger date')
    events_parser.add_argument('--filters', '-f', metavar="<filter>", action='append', nargs='+', help="""List of Event field/value filters: '<field>=<value>' or '<field>' '<operator>' '<value1>' '<value2>...'. Repeatable. Will generate only EsmBasicValue filters.   
    Filter fields can be: Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID, etc...""", default=[[]])
    events_parser.add_argument('--fields', metavar="<field>", nargs='+', help="List of fields that appear in the events table. Default value: {}. ".format(DEFAULT_EVENT_FIELDS_QUERY), default=None)
    events_parser.add_argument('--json', action='store_true', help="Prints only a JSON object to STDOUT output.  ")
    events_parser.add_argument('--limit', metavar='<int>', help='Size of requests', default=500, type=int)
    
    events_parser.add_argument('--max', '--max_query_depth', metavar='<int>', help='Maximum number of reccursive time based divisions the loading process can apply to the query in order to load all events', default=0, type=int)
    events_parser.add_argument('--grouped', action='store_true', help='Indicate a grouped events query, a IPSID filter must be provided and only one field value is accepted. ')
    events_parser.add_argument('--add_note', metavar='<file or text>', help="Add a note to the events matching the filters. ")
    events_parser.add_argument('--listfields', action='store_true', help="List all possible fields names")
    events_parser.add_argument('--listfilters', action='store_true', help="List all possible fields names usable in filters")

    ### WATCHLIST ###
    wl_parser = commands.add_parser('wl', formatter_class=Formatter, help="Manage watchlists. Export, import values.  ", description=wl_cmd.__doc__)
    wl_parser.add_argument('-l', '--list', action='store_true', help='List the ESM watchlists and exit. ')
    wl_parser.add_argument('-t', '--types', action='store_true', help='List all possible watchlists types and exit. ')
    wl_parser.add_argument('-e', '--values', metavar='<wl_name>', help='List watchlist values and exit. Redirect STDOUT to file to export data.  ',)
    
    wl_parser.add_argument('--add', metavar='<wl_name> <wl_type>', help='NotImplemented. Create a static watchlist.', nargs=2)
    wl_parser.add_argument('--delete', '--remove', metavar='<wl ID>', help="NotImplemented. Deletes a Watchlist", nargs=1)
    wl_parser.add_argument('-a', '--addvalues', metavar='<wl_name> <file or values>...', help='NotImplemented. Add values to a static watchlist. ', nargs='+')
    wl_parser.add_argument('--rmvalues', metavar='<wl_name> <file or values>...', help='NotImplemented. Remove watchlist values from the watchlist. ', nargs='+')
    
    wl_parser.add_argument('--json', action='store_true', help="NotImplemented. Prints only a JSON object to STDOUT output.  ")

    ### API ###
    api_parser = commands.add_parser('api', formatter_class=Formatter, help="Quickly make API requests to any enpoints with any data.  ", description=api_cmd.__doc__)
    api_parser.add_argument('-m','--method', metavar='<method>', help="SIEM API method name or NitroSession.PARAMS keyword. Exemple: 'v2/qryGetSelectFields' or 'get_possible_fields', see 'msiem api --list' for full details .")
    api_parser.add_argument('-d','--data', metavar='<JSON string or file>', help='POST data, in the case of a API method name call.  See the SIEM API docs for full details.  ', default={})
    api_parser.add_argument('-a', '--args', metavar='<key>=<value>', help="Interpolation parameters, in the case of a NitroSession.PARAMS keyword call.  See 'msiem api --list' for full details.  ", action='append', nargs='+', default=[[]])
    api_parser.add_argument('-l', '--list', action='store_true', help='List all available SIEM API calls as well as all supported calls with keywords and parameter mapping. All upper cases method names signals to use the private API methods. ' )

    return parser

def parse_msiem_cli_args():
    return (get_parser().parse_args())

def config_cmd(args):
    """
Set and print your msiempy config.  

Set your ESM hostname/user/password interactively:

    $ msiem confi --set esm

Set the general config verbose/quiet/logfile/timeout/ssl_verify interactively:

    $ msiem config --set general

Enable quiet mode (no infos or warnings):

    $ msiem config --set general quiet true --set general verbose false
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
        c=dict(conf._sections)
        c['esm'].update({'passwd':'***', })
        pprint_json(c)

def alarms_cmd_parse_filters(filters_args):
    """
    Parse the 'msiem alarms --filters' argument into tuples.  

    Arguments:

    - filters_args: list of list of string like '<field>=<regex>'

    Returns: List of tuples usable in msiempy AlarmManager filters.  
    """
    filters = []
    for item in [item for sublist in filters_args for item in sublist if sublist and item]:
        if len(item.split('=',1))==2:
            filters.append(( item.split('=',1)[0], item.split('=',1)[1] ))
        else:
            raise ValueError("Using 'msiem alarms', filters must be like '<field>=<regex>'.")
    return filters

def alarms_cmd(args):
    """
Query alarms with alarms and events based regex filters.  
Print, acknowledge, unacknowledge and delete alarms.  

Exemples:  

Acknowledges the (unacknowledged) alarms triggered in the last 
3 days that mention "HTTP: SQL Injection Attempt Detected" in 
the triggered event name and destinated to 10.55.16.99 :

    $ msiem alarms --action acknowledge -t LAST_24_HOURS --status unacknowledged --filters "ruleName=HTTP: SQL Injection Attempt Detected" "destIp=10.55.16.99"

Save the current day alarms as JSON:

    $ msiem alarms -t CURRENT_DAY --no_events --json

    """

    alarms=AlarmManager(
        time_range=args.time_range,
        start_time=args.start_time,
        end_time=args.end_time,
        status_filter=args.status,
        filters=alarms_cmd_parse_filters(args.filters),
        event_filters=alarms_cmd_parse_filters(args.event_filters),
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
            alarms.perform(getattr(Alarm, args.action), progress=False)

def esm_cmd(args):
    """
Show ESM version and misc informations regarding your ESM.
    """
    esm = ESM()
    vargs=vars(args)
    for k,v in vargs.items() :
        if v == True and hasattr(esm, k):
            pprint_json(getattr(esm, k)())

def ds_cmd(args):
    """
Add datasources from CSV or INI files, list, search, remove.  

INI format: Single datasource per file.  
            
    [datasource]
    # name of datasource (required)
    name=testing_datasource
    # ip of datasource (ip or hostname required)
    ds_ip=10.10.1.34
    # hostname of te new datasource
    hostname=
    # type of datasource (required)
    type_id=65
    # id of parent device (required)
    parent_id=144116287587483648
    # True value designate a client datasource 
    client=

CSV Format: Multiple datasources per file

    name,ds_ip,hostname,type_id,parent_id,client
    Test_ds_1,10.10.1.41,datasource11.domain.com,65,144116287587483648,
    Test_ds_2,10.10.1.42,datasource12.domain.com,65,144116287587483648,
    Test_ds_3,10.10.1.43,datasource13.domain.com,65,144116287587483648,

Add Datasources with: 

    $ msiem ds --add "File or folder"
    """
    dstools(args)

def events_cmd_parse_filters(filters_args):
    """
    Parse the list of lists fron argument parser --fiters into tuples and/or msiempy.GroupFilter

    Arguments:  

    - filters_args: args.filters. Arguments filters property.  list of lists.  

    Returns: List of filters as msiempy accepts it. i.e. list of tuples and/or GroupFilter or FieldFilter
    """
    filters = []
    
    for item in [ item for sublist in filters_args for item in sublist if len(sublist)<3 or sublist[1] not in FieldFilter.POSSIBLE_OPERATORS ]:
        if len(item.split('=',1))==2:
            filters.append(( item.split('=',1)[0], item.split('=',1)[1] ))
        else:
            raise ValueError("Using 'msiem events', filters must be like '<field>=<value>' or '<field> <operator> <value1> <value2>...'")

    filters.extend([GroupFilter(
        filters=[FieldFilter(name=sublist[0], 
            operator=sublist[1], 
            values=sublist[2:]) for sublist in filters_args 
        if len(sublist)>=3 and sublist[1] in FieldFilter.POSSIBLE_OPERATORS])])
    return filters

def events_cmd(args):
    """
Query events with filters, add note to events.  

With simple filters:

    $ msiem events --filters DstIP=127.0.0.1 SrcIP=22.0.0.0/8 --fields SrcIP DstIP   

Query events with pecific operatior and multiple values filters (filters are ANDed together inside a group filter). 
Print the results as JSON.  

    $ msiem events --filter SrcIP IN 22.0.0.0/8 10.0.0.0/8 --filter DSIDSigID IN 49190-4294967295 --fields SrcIP DstIP Rule.msg DSIDSigID --json
    """

    # Parse the list of lists passed as args
    filters = events_cmd_parse_filters(args.filters)

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
        text = events.get_text(fields=args.fields)
           
    print(text)

def wl_cmd(args):
    """
Watchlist operations. 
    """
    all_watchlists = WatchlistManager()
        
    if args.list:
        if args.json:
            print(all_watchlists.json)
        else: 
            print(all_watchlists.get_text(fields=['name','type','valueCount','active','source','id']))
        exit(0)
    
    if args.types:
        if args.json:
            pprint_json(all_watchlists.get_wl_types())
        else:
            print("All Watchlist types: ")
            print('\n'.join([ t['name'] for t in all_watchlists.get_wl_types() ]) )
        exit(0)

    if args.values:
        my_wl = [ w for w in all_watchlists if w['name'] == args.values]
        if not len(my_wl):
            raise ValueError("Watchlist not found")
        else:
            my_wl=my_wl[0]
        my_wl.load_values()
        if args.json:
            pprint_json(my_wl['values'])
        else:
            print("Watchlist '{}' values: ".format(my_wl['name']))
            print('\n'.join(my_wl['values']))
        exit(0)
    
    if args.addvalues:
        my_wl = [ w for w in all_watchlists if w['name'] == args.addvalues[0]]
        if not len(my_wl):
            raise ValueError("Watchlist not found")
        else:
            my_wl=my_wl[0]
        
        my_wl.add_values()
        raise NotImplementedError()

    if args.add:
        raise NotImplementedError()
    if args.delete:
        raise NotImplementedError()
    if args.rmvalues:
        raise NotImplementedError()
    if args.json:
        raise NotImplementedError()

def api_cmd_get_api_docs():
    """
    Get a list of all possible API calls
    """
    s=NitroSession()
    help_page = etree.parse(BytesIO(requests.get('https://{esm_url}/rs/esm/v2/help'.format(esm_url=s.config.host), verify=s.config.ssl_verify).text.encode()))
    endpoints = [e.get('name') for e in help_page.iter() if 'esmCommand' in e.tag and e.get('name')]

    docs = ""
    for endp in endpoints:
        docs += "msiem api --method v2/{} --data <JSON string or file>\n".format(endp)

    return docs

def api_cmd_get_params_docs():
    """
    Get a list of all possible API calls with paramaters interpolation
    
    TODO: write a test
    """
    s=NitroSession()
    docs = ""
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
        docs += "msiem api --method '{}' {} # Call {}  \n".format(
            name, '--args '+params if params else params, endpoint
        )
    return docs

def api_cmd_parse_interpolated_args(args_args):
    """
    Parse the API call arguments.  
    """
    request_args = {}
    for item in [item for sublist in args_args for item in sublist]:
        if len(item.split('=',1))==2:
            request_args.update({item.split('=',1)[0]: item.split('=',1)[1]})
        else:
            raise ValueError("Using 'msiem api --args', arguments must be like '<key>=<value>'.")
    return request_args

def api_cmd_get_data(args_data):
    """
    Get the passed data from JSON string or read the file.  
    """
    data=None
            
    if args_data:
        try:
            data = json.loads(args_data)
        except ValueError:
            if is_path_exists_or_creatable(args_data):
                with open(args_data, 'r') as d:
                    data = json.load(d)
            else:
                raise
    else:
        data={}
    return data

def api_cmd(args):
    """
Quickly make API requests to any enpoints with any data. Print resposne to sdtout as JSON.   

Request v2/alarmGetTriggeredAlarms:  

    $ msiem api --method "v2/alarmGetTriggeredAlarms?triggeredTimeRange=LAST_24_HOURS&status=&pageSize=500&pageNumber=1"

    """
    
    s=NitroSession()
    s.login()

    if args.list:

        print("All possible SIEM requests: ")
        print(api_cmd_get_api_docs())

        print("Requests with API parameters interpolation")
        print(api_cmd_get_params_docs())

        exit(0)

    if args.method:
        if args.method in s.PARAMS.keys():

            res = s.request(args.method, **api_cmd_parse_interpolated_args(args.args))
        else:

            res = s.api_request(args.method, api_cmd_get_data(args.data))

        pprint_json(res)

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


