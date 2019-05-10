# -*- coding: utf-8 -*-
"""
    msiem command
"""

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

import argparse
from .config import ESMConfig
from .session import ESMSession
from .query import AlarmQuery, Alarm, EventQuery, Event
from .utils import log, parseListToDict
from .constants import POSSIBLE_TIME_RANGE

def parseArgs():
    parser = argparse.ArgumentParser(description='McAfee SIEM Command Line Interface and Python API',
                usage='Use "msiem --help" for more information',
                formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--version', help="Show version",action="store_true")
    parser.add_argument('-v' '--verbose', help="Increase output verbosity",action="store_true")

    commands = parser.add_subparsers()

    config_command = commands.add_parser('config')
    config_command.set_defaults(func=config)
    config_command.add_argument('--list', help="List configuration fields", action="store_true")
    config_command.add_argument('--set')

    alarm_command = commands.add_parser('alarms')
    alarm_command.set_defaults(func=alarms)
    alarm_command.add_argument('--ack', help="Acknowledge the alarms", action="store_true")
    alarm_command.add_argument('--unack', help="Unacknowledge the alarms", action="store_true")

    alarm_command.add_argument('--tr','--time_range', help='Timerange in'+str(POSSIBLE_TIME_RANGE), required=True)
    alarm_command.add_argument('--st','--start_time', help='Start acknowledge date')
    alarm_command.add_argument('--et','--end_time', help='Start acknowledge date')
    alarm_command.add_argument('--status', help='Status of the alarm [ack|unack|all]')

    alarm_command.add_argument('--filters', nargs='+', type=str, help="List of filters")

    return (parser.parse_args())

def config(args):
    config=ESMConfig()
    if args.set :
        if 'auth' in args.set :
            config.setAuth()
            config.write()

def alarms(args):
    
    query=AlarmQuery(
        time_range=args.time_range,
        start_time=args.start_time,
        end_time=args.end_time,
        status=args.status,
        filters=args.filters
        )

    log.info(query)

def main():
    args = parseArgs()
    print(lol)
    if args.func :
        args.func(args)

if __name__ == "__main__":
    main()


