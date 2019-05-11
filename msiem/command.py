# -*- coding: utf-8 -*-
"""
    msiem command
"""

import argparse
from .config import ESMConfig
from .session import ESMSession
from .query import AlarmQuery, Alarm, EventQuery, Event
from .constants import POSSIBLE_TIME_RANGE, ALARM_FILTER_FIELDS, ALARM_EVENT_FILTER_FIELDS

lol="""
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


def parseArgs():
    parser = argparse.ArgumentParser(description='McAfee SIEM Command Line Interface and Python API',
                usage='Use "msiem --help" for more information',
                formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--version', help="Show version",action="store_true")
    parser.add_argument('-v', '--verbose', help="Increase output verbosity",action="store_true")

    commands = parser.add_subparsers()

    config = commands.add_parser('config')
    config.set_defaults(func=config)
    config.add_argument('--list', help="List configuration fields", action="store_true")
    config.add_argument('--set', help="Will inveractively prompt for configuration settings", action="store_true")

    alarm = commands.add_parser('alarms')
    alarm.set_defaults(func=alarms)
    alarm.add_argument('--ack', help="Acknowledge the alarms", action="store_true")
    alarm.add_argument('--unack', help="Unacknowledge the alarms", action="store_true")
    alarm.add_argument('--delete', help="Delete the alarms", action="store_true")
    
    alarm.add_argument('--time_range','-t', metavar='time_range', help='Timerange in'+str(POSSIBLE_TIME_RANGE))
    alarm.add_argument('--start_time','--t1', metavar='time', help='Start trigger date')
    alarm.add_argument('--end_time','--t2', metavar='time', help='End trigger date')

    alarm.add_argument('--status', metavar='status', help='Status of the alarm [ack|unack|all]')

    alarm.add_argument('--filters', '-f', metavar="'<key>=<match>'", nargs='+', type=str, help="List of filters")

    alarm.add_argument('--summary', metavar="sumary", help="Alarm summary filter")
    alarm.add_argument('--assignee', metavar="assignee", help="Alarm assignee filter")
    alarm.add_argument('--severity', metavar="severity", help="Alarm severity filter")
    alarm.add_argument('--trigdate', metavar="trigdate", help="Alarm trigdate filter")
    alarm.add_argument('--ackdate', metavar="ackdate", help="Alarm ackdate filter")
    alarm.add_argument('--ackuser', metavar="ackuser", help="Alarm ackuser filter")
    alarm.add_argument('--name', metavar="name", help="Alarm name filter")

    alarm.add_argument('--msg', metavar="msg", help="Event msg filter")
    alarm.add_argument('--count', metavar="count", help="Event count filter")
    alarm.add_argument('--srcip', metavar="srcip", help="Event srcip filter")
    alarm.add_argument('--dstip', metavar="dstip", help="Event dstip filter")
    alarm.add_argument('--protocol', metavar="protocol", help="Event protocol filter")
    alarm.add_argument('--date', metavar="date", help="Event date filter")
    alarm.add_argument('--subtype', metavar="subtype", help="Event subtype filter")

    return (parser.parse_args())

def config(args):

    if args.set :
        ESMConfig().interactiveSet()

    if args.list :
        ESMConfig().show()

def alarms(args):
    
    vargs=vars(args)

    #Filter out the filters keys from list of parameters based on their names
    filters = list()
    for key in vargs :
        if vargs[key] is not None:
            for synonims in ALARM_FILTER_FIELDS+ALARM_EVENT_FILTER_FIELDS:
                if key in synonims :
                    filters.append((key, vargs[key]))
    
    #Merging values from --filters option
    if args.filters is not None :
        filters+=args.filters

    print(filters)

    alarms=AlarmQuery(
        time_range=args.time_range,
        start_time=args.start_time,
        end_time=args.end_time,
        status=args.status,
        filters=filters
    ).execute()

    if len(alarms) >0:

        alarms.show()

        if args.ack and 'y' in input('Are you sure you want to acknowledge those alarms ? [y/n]'):
            alarms.acknowledge()

        if args.unack and 'y' in input('Are you sure you want to unacknowledge those alarms ? [y/n]'):
            alarms.unacknowledge()

def main():
    args = parseArgs()

    if hasattr(args, 'func') :
        args.func(args)
    

if __name__ == "__main__":
    main()


