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

    --filter/-f    
                -f event.srcip 10.2.2.2
                -f event.dstip 10.2.2.1
                -f event.msg=http-vulnerability
                -f event.name=Bob le bricoleur'
                #and others under event. #See documentation

                -f summary=<>
                -f severity=90
                -f ackuser=tristan
                -f assignee=tristan
                -f name=Critical
                -f acked=[yes/no/all]

                -f ackdate.begins=2019-03-25
                -f ackdate.ends=2019-03-25
                -f time=2019-03-25T14:00
                -f window=1h
                -f timerange=LAST_24_HOURS
                -f begins=2019-03-25
                vends=2019-03-25

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
try:
    from .config import ESMConfig
except( ModuleNotFoundError, ImportError ):
    from config import ESMConfig

def parseArgs():
    parser = argparse.ArgumentParser(description='McAfee SIEM Command Line Interface and Python API',
                usage='Use "msiem --help" for more information',
                formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--version')
    parser.add_argument('--batch')

    commands = parser.add_subparsers()

    config_command = commands.add_parser('config')
    config_command.set_defaults(func=config)
    config_command.add_argument('--list')
    config_command.add_argument('--set')

    return (parser.parse_args())

def config(args):
    c=ESMConfig()
    if args.set is not None :
        if 'auth' in args.set :
            c.setAuth()
            c.write()

def main():
    args = parseArgs()
    print(lol)
    if args.func :
        args.func(args)

if __name__ == "__main__":
    main()


