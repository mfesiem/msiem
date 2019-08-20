# -*- coding: utf-8 -*-
"""
What it could look like :

msiem 
    --help #Exits after
    --version #Exists after
    --batch

msiem config
    --help
    --list/-l
    --set auth
    --set <section.key>=<value>

msiem esm 
    --help/-h
    --time/-t
    --version/-v
    --tz/--timezones
    --disks/-d
    --callhome
    --ram
    --status
    --backup-status
    --buildstamp
    --recs
    --rule

    #Todo
    --nslookup
    --fields -> display list of possible fields with qryGetSelectFields
    --filters -> display list of possible filters with qryGetFilterFields

    #FullBackUp
    --backup esm_full_backup
    https://github.com/andywalden/esm_full_backup/

msiem ds
    --help/-h
    --add/-a interactive si manque arg
        name=DC01_DNS 
        ip=10.10.1.34 
        rec_ip=172.16.15.10
        type=linux
        Will add a new datasource and also call --info
        Ask for confirmation unless --force

    --del/-d <id or name> if resolves to only one device
        Ask for confirmation unless --force

    --search/-s <pattern>
    --searchgroup/-g
    --info/-i <id or name>
    --times/-t
    (--refresh)
    --recs --> ?
    --ipvalid <>
    --addclient <ds> <> ...

    --checkinactive
    Queries a McAfee ESM for inactive data sources. from https://github.com/andywalden/esmcheckds2

msiem alarms

    --search/-s [default]

    --ack/-a
        Ask for confirmation unless --force

    --del/-d
        Ask for confirmation unless --force

    --unack/-u

    
   
    --time_range LAST_24_HOURS
    --start_time 2019-03-25
    --end_time 2019-03-25
    --status [acked/unacked/all]

    --time 2019-03-25T14:00
    --window 1h

    --filter/-f    
                '[event.]srcip 10.2.2.2'
                '[event.]dstip 10.2.2.1'
                '[event.]msg=http-vulnerability'
                '[event.]count=http-vulnerability'
                '[event.]protocol=http-vulnerability'
                'event.time=http-vulnerability'
                '[event.]subtype=http-vulnerability'

                summary=<>
                severity=90
                ackuser=tristan
                assignee=tristan
                name=Critical
                acktime

                

                #No filtering on DetailedAlarm fields value !
                #Only a couple basic event related fields are available for filtering
                #Filters are ANDed together

    --info/-i <id>
        --> show the conditionnal xml tree and alarm meta data

    --force


msiem events
    --search

    --filter
            -f sourceip=10.2.2.2
            -f destinationip=10.2.2.1
            -f message=http-vulnerability
            -f 'name=Bob le bricoleur'

            -f time=2019-03-25T14:00
            -f window=1h
            -f timerange=LAST_24_HOURS
            -f begins=2019-03-25
            -f ends=2019-03-25

            #and others under event. #See documentation
            #Filters are ANDed together

    --fields
        #Fields to add to the defaults settings

    --order <order>

msiem watchlist
    Inteface to whatchlist operations

msiem service
    Opens a service now mcfee ticket.
    Callable by the Execute function of the ESM.
    https://github.com/andywalden/mfe2snow

msiem syslog
    Generate syslog message on the SIEM

msiem case
    --close https://github.com/andywalden/esm_close_cases
    --open <alarm>
    --msg <message>

msiem elm 
    Export ELM files back to original format
    https://github.com/andywalden/elmex/blob/master/elmex.sh

"""

import argparse
import msiempy
import msiempy.event
import msiempy.alarm
import msiempy.device

class Formatter( argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass

def parse_args():
    parser = argparse.ArgumentParser(description='McAfee SIEM Command Line Interface and Python API',
                usage='Use "msiem <command> --help" for more information.', formatter_class=Formatter,)

    #parser.add_argument('--version', help="Show version",action="store_true")
    #parser.add_argument('-v', '--verbose', help="Increase output verbosity",action="store_true")

    commands = parser.add_subparsers(dest='command')

    config = commands.add_parser('config', formatter_class=Formatter)
    config.set_defaults(func=config)
    config.add_argument('--print', help="Print configuration fields", action="store_true")
    config.add_argument('--set', metavar='section', help="Will inveractively prompt for specified configuration section : esm or general")

    alarm = commands.add_parser('alarms', formatter_class=Formatter, epilog=alarms.__doc__)
    alarm.set_defaults(func=alarms)

    alarm.add_argument('--action', metavar="action", help="What to do with the alarms, if not specified will print only", 
        choices=['acknowledge','unacknowledge','delete'])

    alarm.add_argument('--force', help="Will not prompt for confirmation to do the specified action", action="store_true")

    alarm.add_argument('--time_range','-t', metavar='time_range', help='Timerange, choose from '+', '.join(msiempy.FilteredQueryList.POSSIBLE_TIME_RANGE), 
        choices=msiempy.FilteredQueryList.POSSIBLE_TIME_RANGE)
    alarm.add_argument('--start_time','--t1', metavar='time', help='Start trigger date')
    alarm.add_argument('--end_time','--t2', metavar='time', help='End trigger date')
    alarm.add_argument('--status', metavar='status', help='Status of the alarm',choices=['acknowledged','unacknowledged','all'], default='all')

    alarm.add_argument('--filters', '-f', metavar="'<field>=<match>'", nargs='+', type=str, help="""List of field/matchvalue filters. 
    Alarm related fields can be : id, summary, assignee, severity, triggeredDate, acknowledgedDate, acknowledgedUsername, alarmName, events.  
    Event related fields can be (if --query_events) : Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID.  
    Or : ruleName, srcIp, destIp, protocol, lastTime, subtype, destPort, destMac, srcMac, srcPort, deviceName, sigId, normId, srcUser, destUser, normMessage, normDesc, host, domain, ipsId.""")
    
    alarm.add_argument('--page_size', '-p', metavar='page_size', help='Size of requests', default=50, type=int)

    alarm.add_argument('--workers', metavar="workers", help='Number of max asynch workers', default=10, type=int)
    alarm.add_argument('--max_queries', metavar="max_queries", help='Number of times the query can be slipted to get more data', default=0, type=int)
    alarm.add_argument('--query_delta', metavar='delta', help='The timedelta of first time slots division', default='12h')
    alarm.add_argument('--query_slots', metavar='slots', help='The number of time slots division after the first one', default=4)

    alarm.add_argument('--no_events', help='Do not load unecessary event data in order to filter', action="store_true")
    alarm.add_argument('--query_events', help='Use the query API query module to retreive events, much more effcient', action="store_true")

    esm_parser = commands.add_parser('esm', formatter_class=Formatter)
    esm_parser.set_defaults(func=esm)
    esm_parser.add_argument('--version', help='Show ESM version', action="store_true")
    esm_parser.add_argument('--time', help='time (GMT)', action="store_true")
    esm_parser.add_argument('--disks', help='disk status', action="store_true")
    esm_parser.add_argument('--ram', help='ram status', action="store_true")
    esm_parser.add_argument('--callhome', help='True/False if callhome is active/not active', action="store_true")
    esm_parser.add_argument('--status', help='Statuses and a few other less interesting details : autoBackupEnabled, autoBackupDay, backupLastTime, backupNextTime, rulesAndSoftwareCheckEnabled, rulesAndSoftLastCheck, rulesAndSoftNextCheck', action="store_true")
    esm_parser.add_argument('--timezones', help='Current ESM timezone', action="store_true")


    return (parser.parse_args())

def config(args):

    conf=msiempy.NitroConfig()

    if args.set is not None :
        conf.iset(args.set)

    if args.print :
        print(conf)

def alarms(args):

    filters = list()

    #Filers from --filters option
    if args.filters is not None :
        filters+=args.filters

    alarms=msiempy.alarm.AlarmManager(
        time_range=args.time_range,
        start_time=args.start_time,
        end_time=args.end_time,
        status_filter=args.status,
        filters=filters,
        page_size=args.page_size,
        max_query_depth = args.max_queries,
    )
    alarms.load_data(
        workers=args.workers,
        slots=args.query_slots,
        delta=args.query_delta,
        no_detailed_filter = args.no_events,
        use_query = args.query_events
    )
 
    print(alarms.json)
        
    if args.action is not None :
        if args.force or ('y' in input('Are you sure you want to '+str(args.action)+' those alarms ? [y/n]')):
            alarms.perform(getattr(msiempy.alarm.Alarm, args.action), progress=True)
            
            #getattr(alarms, args.action)()

def esm(args):
    esm = msiempy.device.ESM()
    vargs=vars(args)
    for arg in vargs :
        if vargs[arg] == True :
            print(getattr(esm, arg)())

def main():
    
    print("""
                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_|
     
 McAfee SIEM Command Line Interface

    """)

    args = parse_args()

    if args.command == 'config' :
        config(args)
    elif args.command == 'alarms' :
        alarms(args)
    elif args.command == 'esm':
        esm(args)


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


