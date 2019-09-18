# -*- coding: utf-8 -*-
"""
msiem cli
"""

import argparse
import msiempy
import msiempy.event
import msiempy.alarm
import msiempy.device

class Formatter( argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass

def parse_args():
    parser = argparse.ArgumentParser(description="""
                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_|
     
 McAfee SIEM Command Line Interface

    """, usage='Run "msiem <command> --help" for more information about a sub-command.', formatter_class=Formatter,)

    #parser.add_argument('--version', help="Show version",action="store_true")
    #parser.add_argument('-v', '--verbose', help="Increase output verbosity",action="store_true")

    commands = parser.add_subparsers(dest='command')

    config = commands.add_parser('config', formatter_class=Formatter, epilog=config_cmd.__doc__)
    config.set_defaults(func=config_cmd)
    config.add_argument('--print', help="Print configuration fields", action="store_true")
    config.add_argument('--set', metavar='section', help="Will inveractively prompt for specified configuration section : esm or general")

    alarm = commands.add_parser('alarms', formatter_class=Formatter, epilog=alarms_cmd.__doc__)
    alarm.set_defaults(func=alarms_cmd)

    alarm.add_argument('--action', metavar="action", help="What to do with the alarms, if not specified will print only", 
        choices=['acknowledge','unacknowledge','delete'])

    alarm.add_argument('--force', help="Will not prompt for confirmation to do the specified action", action="store_true")

    alarm.add_argument('--time_range','-t', metavar='time_range', help='Timerange, choose from '+', '.join(msiempy.FilteredQueryList.POSSIBLE_TIME_RANGE),  
        choices=msiempy.FilteredQueryList.POSSIBLE_TIME_RANGE, default='CURRENT_DAY')
    alarm.add_argument('--start_time','--t1', metavar='time', help='Start trigger date')
    alarm.add_argument('--end_time','--t2', metavar='time', help='End trigger date')
    alarm.add_argument('--status', metavar='status', help='Status of the alarm',choices=['acknowledged','unacknowledged','all'], default='all')

    alarm.add_argument('--filters', '-f', metavar="'<field>=<match>'", action='append', nargs='+', help="""List of field/matchvalue filters. 
    Alarm related fields can be : id, summary, assignee, severity, triggeredDate, acknowledgedDate, acknowledgedUsername, alarmName, events.  
    Event related fields can be (if --query_events) : Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID.  
    Or : ruleName, srcIp, destIp, protocol, lastTime, subtype, destPort, destMac, srcMac, srcPort, deviceName, sigId, normId, srcUser, destUser, normMessage, normDesc, host, domain, ipsId.""", default=[[]])
    
    alarm.add_argument('--alarms_fields', metavar="list of fields", nargs='+', help="List of fields you want to appear in the alarm table. Overwritten by --json", default=[])
    alarm.add_argument('--events_fields', metavar="list of fields", nargs='+', help="List of fields you want to appear in the events sub tables. Overwritten by --json", default=[])
    alarm.add_argument('--json', action='store_true', help="Prints the raw json object with all loaded fields")

    alarm.add_argument('--page_size', '-p', metavar='page_size', help='Size of requests', default=100, type=int)

    alarm.add_argument('--workers', metavar="workers", help='Number of max asynch workers', default=10, type=int)
    #alarm.add_argument('--max_queries', metavar="max_queries", help='Number of times the query can be slipted to get more data', default=0, type=int)
    #alarm.add_argument('--query_delta', metavar='delta', help='The timedelta of first time slots division', default=None)
    #alarm.add_argument('--query_slots', metavar='slots', help='The number of time slots division after the first one', default=10, type=int)

    alarm.add_argument('--no_events', help='Do not load unecessary event data in order to filter', action="store_true")
    alarm.add_argument('--query_events', help='Use the query API query module to retreive events, much more effcient', action="store_true")

    esm_parser = commands.add_parser('esm', formatter_class=Formatter, epilog=esm_cmd.__doc__)
    esm_parser.set_defaults(func=esm_cmd)
    esm_parser.add_argument('--version', help='Show ESM version', action="store_true")
    esm_parser.add_argument('--time', help='time (GMT)', action="store_true")
    esm_parser.add_argument('--disks', help='disk status', action="store_true")
    esm_parser.add_argument('--ram', help='ram status', action="store_true")
    esm_parser.add_argument('--callhome', help='True/False if callhome is active/not active', action="store_true")
    esm_parser.add_argument('--status', help='Statuses and a few other less interesting details : autoBackupEnabled, autoBackupDay, backupLastTime, backupNextTime, rulesAndSoftwareCheckEnabled, rulesAndSoftLastCheck, rulesAndSoftNextCheck', action="store_true")
    esm_parser.add_argument('--timezones', help='Current ESM timezone', action="store_true")


    return (parser.parse_args())

def config_cmd(args):

    conf=msiempy.NitroConfig()

    if args.set is not None :
        conf.iset(args.set)
        conf.write()

    if args.print :
        print(conf)

def alarms_cmd(args):

    filters = [item for sublist in args.filters for item in sublist]

    alarms=msiempy.alarm.AlarmManager(
        time_range=args.time_range,
        start_time=args.start_time,
        end_time=args.end_time,
        status_filter=args.status,
        filters=[((item.split('=')[0],item.split('=')[1])) for item in filters],
        page_size=args.page_size,
        #max_query_depth = 1,
    )
    alarms.load_data(
        workers=args.workers,
        # slots=10,
        # delta=args.query_delta,
        no_detailed_filter = args.no_events,
        use_query = args.query_events,
        extra_fields=args.events_fields
    )
    if args.json:
        text = alarms.json
    else:
        if args.no_events :
            text = alarms.get_text() if len(args.alarms_fields)==0 else alarms.get_text(fields=args.alarms_fields)
        else:
            try :
                text=alarms.get_text(fields=['alarmName','triggeredDate', 'acknowledgedDate', 'events'] if len(args.alarms_fields)==0 else args.alarms_fields,
                    get_text_nest_attr=dict(fields=(['ruleName','srcIp','destIp', 'srcUser', 'host', 'sigId'] if not args.query_events 
                        else ['Rule.msg','Alert.SrcIP','Alert.DstIP','Alert.DSIDSigID']) if len(args.events_fields)==0 else args.events_fields)
                    )
            except KeyError:
                text=alarms.json + "\n\n" + alarms.text + "\n\nWARNING : Sorry the table you requested coulnd't be generated. \nHere is printed a global table and upper the json content. \nThe SIEM query respond with very inconsistent data and returned fields don't necessary match requested ones..."

    print(text)
        
    if args.action is not None :
        if args.force or ('y' in input('Are you sure you want to '+str(args.action)+' those alarms ? [y/n]')):
            alarms.perform(getattr(msiempy.alarm.Alarm, args.action), progress=True)

def esm_cmd(args):
    esm = msiempy.device.ESM()
    vargs=vars(args)
    for arg in vargs :
        if vargs[arg] == True and hasattr(esm, vargs[arg]):
            print(getattr(esm, arg)())

def main():
    
    print()

    args = parse_args()

    if args.command == 'config' :
        config_cmd(args)
    elif args.command == 'alarms' :
        alarms_cmd(args)
    elif args.command == 'esm':
        esm_cmd(args)
    else :
        pass


        """
        #Needs to ignore exception when we call 'msiem command' with no other attributes
        try :
            args.func(args)
        except TypeError as err :
            if "'ArgumentParser' object is not callable" in str(err):
                print("Please refer to documentation.")
            else:
                raise"""

if __name__ == "__main__":
    main()


