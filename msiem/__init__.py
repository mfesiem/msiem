"""
Welcome to the **msiem** CLI documentation.  
***
Links : [GitHub](https://github.com/mfesiem/msiem), [PyPI](https://pypi.org/project/msiem/), [msiempy documentation](https://mfesiem.github.io/docs/msiempy/index.html), [SIEM API references Home](https://mfesiem.github.io) (generated PDFs and other links)
***
## CLI overview
```
usage: msiem [-h] [-V] {config,alarms,esm,ds,events,api} ...

                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_| CLI
     
McAfee SIEM Command Line Interface 0.3.0.dev1
License: MIT
Credits: Andy Walden, Tristan Landes

Run 'msiem <command> --help' for more information about a sub-command.

positional arguments:
  {config,alarms,esm,ds,events,api}
    config              Set and print your msiempy config.
    alarms              Query alarms with alarms and events based regex filters.
                        Print, acknowledge, unacknowledge and delete alarms.
    esm                 Show ESM version and misc informations regarding your ESM.
    ds                  Add datasources from CSV or INI files, list, search, remove.
    events              Query events with any simple filter. Add a note to events.
    api                 Quickly make API requests to any enpoints with any data.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         Show version and exit (default: False)
```
## Config
```
usage: msiem config [-h] [--print] [--set '<section>' ['<option>' '<value>']
                    ['<section>' ['<option>' '<value>'] ...]]

Set and print your msiempy config.  

optional arguments:
  -h, --help            show this help message and exit
  --print               Print configuration fields, password base 64 included.
                        (default: False)
  --set '<section>' ['<option>' '<value>'] ['<section>' ['<option>' '<value>'] ...]
                        Set the config option to the specified value if passed (can
                        be repeated), OR inveractively prompt for specified
                        configuration section: 'esm' or 'general'. (default: [])
```
## Alarms
```
usage: msiem alarms [-h] [--action action] [--force] [--time_range time_range]
                    [--start_time time] [--end_time time] [--status status]
                    [--filters '<field>=<match>' ['<field>=<match>' ...]]
                    [--event_filters '<field>=<match>' ['<field>=<match>' ...]]
                    [--alarms_fields list of fields [list of fields ...]]
                    [--events_fields list of fields [list of fields ...]]
                    [--json] [--page_size page_size] [--pages pages]
                    [--workers workers] [--no_events] [--query_events]

Query alarms with alarms and events based regex filters.  
Print, acknowledge, unacknowledge and delete alarms.  

Exemples:  

Acknowledges the (unacknowledged) alarms triggered in the last 
3 days that mention "HTTP: SQL Injection Attempt Detected" in 
the triggered event name and destinated to 10.55.16.99 :

$ msiem alarms --action acknowledge \
-t LAST_24_HOURS \
--status unacknowledged \
--filters \
    "ruleName=HTTP: SQL Injection Attempt Detected" \
    "destIp=10.55.16.99"

Prints the alarms triggered in the last hour using the query 
module to retreive events informations and request for 
specific fields :

$ msiem alarms -t LAST_HOUR \
--query_events \
--alarms_fields acknowledgedDate alarmName events \
--events_fields Alert.LastTime Rule.msg Alert.DstIP

optional arguments:
  -h, --help            show this help message and exit
  --action action       What to do with the alarms, if not specified will print
                        only. Chose from 'acknowledge','unacknowledge','delete'
                        (default: None)
  --force               Will not prompt for confirmation to do the specified action
                        (default: False)
  --time_range time_range, -t time_range
                        Timerange, choose from CUSTOM, LAST_MINUTE, LAST_10_MINUTES,
                        LAST_30_MINUTES, LAST_HOUR, CURRENT_DAY, PREVIOUS_DAY,
                        LAST_24_HOURS, LAST_2_DAYS, LAST_3_DAYS, CURRENT_WEEK,
                        PREVIOUS_WEEK, CURRENT_MONTH, PREVIOUS_MONTH,
                        CURRENT_QUARTER, PREVIOUS_QUARTER, CURRENT_YEAR,
                        PREVIOUS_YEAR (default: CURRENT_DAY)
  --start_time time, --t1 time
                        Start trigger date (default: None)
  --end_time time, --t2 time
                        End trigger date (default: None)
  --status status       Status of the alarm. Chose from
                        'acknowledged','unacknowledged','all' (default: all)
  --filters '<field>=<match>' ['<field>=<match>' ...], -f '<field>=<match>' ['<field>=<match>' ...]
                        List of alarm related field/matchvalue filters. Repeatable.
                        Alarm related fields can be : id, summary, assignee,
                        severity, triggeredDate, acknowledgedDate,
                        acknowledgedUsername, alarmName, events, and others
                        (default: [[]])
  --event_filters '<field>=<match>' ['<field>=<match>' ...], -e '<field>=<match>' ['<field>=<match>' ...]
                        List of triggering event related field/matchvalue filters.
                        Repeatable. Event related fields can be : ruleName, srcIp,
                        destIp, protocol, lastTime, subtype, destPort, destMac,
                        srcMac, srcPort, deviceName, sigId, normId, srcUser,
                        destUser, normMessage, normDesc, host, domain, ipsId, etc...
                        Or (if --query_events) : Rule.msg, Alert.SrcPort,
                        Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac,
                        Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID,
                        Alert.IPSIDAlertID, etc... (default: [[]])
  --alarms_fields list of fields [list of fields ...]
                        List of fields that appear in the alarm table. Overwritten
                        by --json (default: ['alarmName', 'triggeredDate',
                        'acknowledgedDate', 'events'])
  --events_fields list of fields [list of fields ...]
                        List of fields that appear in the events sub tables. Default
                        value: ['ruleName', 'srcIp', 'destIp']. If you use
                        --query_events, this list will be used to query needed
                        values, you must specify all fields you want to filter on
                        with ewvent_filters. Default value if --query_events:
                        ['Rule.msg', 'Alert.SrcIP', 'Alert.DstIP']. Overwritten by
                        --json. (default: None)
  --json                Prints the raw json object with all loaded fields (default:
                        False)
  --page_size page_size, -p page_size
                        Size of requests (default: 500)
  --pages pages, -n pages
                        Number of alarm pages to load (default: 1)
  --workers workers     Number of max asynch workers (default: 10)
  --no_events           Do not load the complete trigerring events informations.
                        (default: False)
  --query_events        Use the query module to retreive events, much more effcient.
                        Event keys will be like 'Alert.SrcIP' instead of 'srcIp'
                        (default: False)
```
## ESM
```
usage: msiem esm [-h] [--version] [--time] [--disks] [--ram] [--callhome]
                 [--status] [--timezones]

Show ESM version and misc informations regarding your ESM.

optional arguments:
  -h, --help   show this help message and exit
  --version    Show ESM version (default: False)
  --time       time (GMT) (default: False)
  --disks      disk status (default: False)
  --ram        ram status (default: False)
  --callhome   True/False if callhome is active/not active (default: False)
  --status     Statuses and a few other less interesting details :
               autoBackupEnabled, autoBackupDay, backupLastTime,
               backupNextTime, rulesAndSoftwareCheckEnabled,
               rulesAndSoftLastCheck, rulesAndSoftNextCheck (default:
               False)
  --timezones  Current ESM timezone (default: False)
```
## Datasources
```
usage: msiem ds [-h] [-a <file or folder>] [-s [term]] [-l]
                [--delete <datasource ID> [<datasource ID> ...]]
                [--deleteclients <datasource ID> [<datasource ID> ...]]
                [--force]

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
Test DataSource 11,10.10.1.41,datasource11.domain.com,65,144116287587483648,
Test DataSource 12,10.10.1.42,datasource12.domain.com,65,144116287587483648,
Test DataSource 13,10.10.1.43,datasource13.domain.com,65,144116287587483648,

Add Datasources with: 

$ msiem ds --add <file or folder>

optional arguments:
  -h, --help            show this help message and exit
  -a <file or folder>, --add <file or folder>
                        Scan a directory or a file for new Datasource files and add
                        them to the ESM. Datasources can be defined in CSV or INI
                        format (see README.md). (default: None)
  -s [term], --search [term]
                        Search for datasource name, hostname, or IP.May require
                        quotes around the name if thereare spaces. (default: None)
  -l, --list            Display datasources. (default: False)
  --delete <datasource ID> [<datasource ID> ...]
                        Deletes the datasource and all the data. Be careful.
                        (default: None)
  --deleteclients <datasource ID> [<datasource ID> ...]
                        Deletes the datasource's clients and all the data. Be
                        careful. (default: None)
  --force               Do not ask the user input before deletion of the datasources
                        / datasources client. (default: False)
```
## Events
```
usage: msiem events [-h] [--time_range time_range] [--start_time time]
                    [--end_time time] [--filters <filter> [<filter> ...]]
                    [--fields list of fields [list of fields ...]] [--json]
                    [--limit limit]

Query events with filters, add note to events.  

With simpler filter

$ msiem events --filter DstIP=127.0.0.1 --field SrcIP DstIP   

Specific operatior and multiple values filter

$ msiem events --filter \
    SrcIP IN 22.0.0.0/8 10.0.0.0/8 \
    --fields SrcIP DstIP

optional arguments:
  -h, --help            show this help message and exit
  --time_range time_range, -t time_range
                        Timerange, choose from CUSTOM, LAST_MINUTE, LAST_10_MINUTES,
                        LAST_30_MINUTES, LAST_HOUR, CURRENT_DAY, PREVIOUS_DAY,
                        LAST_24_HOURS, LAST_2_DAYS, LAST_3_DAYS, CURRENT_WEEK,
                        PREVIOUS_WEEK, CURRENT_MONTH, PREVIOUS_MONTH,
                        CURRENT_QUARTER, PREVIOUS_QUARTER, CURRENT_YEAR,
                        PREVIOUS_YEAR (default: CURRENT_DAY)
  --start_time time, --t1 time
                        Start trigger date (default: None)
  --end_time time, --t2 time
                        End trigger date (default: None)
  --filters <filter> [<filter> ...], -f <filter> [<filter> ...]
                        List of Event field/value filters: '<field>=<value>' or
                        '<field>' '<operator>' '<value1>' '<value2>...'. Repeatable.
                        Will generate only EsmBasicValue filters. Filter fields can
                        be: Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP,
                        Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime,
                        Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID, etc...
                        (default: [[]])
  --fields list of fields [list of fields ...]
                        List of fields that appear in the events table. Default
                        value: ['Rule.msg', 'Alert.SrcIP', 'Alert.DstIP']. (default:
                        None)
  --json                Prints the raw json object with all loaded fields (default:
                        False)
  --limit limit         Size of requests (default: 500)
```
## API
```
usage: msiem api [-h] [-m <method>] [-d <JSON string or file>]
                 [-a <key>=<value> [<key>=<value> ...]] [-l]

Quickly make API requests to any enpoints with any data.  

Exemple

$ msiem api --method \
    "v2/alarmGetTriggeredAlarms?triggeredTimeRange=LAST_24_HOURS&status=&pageSize=500&pageNumber=1" \
    --data {}

optional arguments:
  -h, --help            show this help message and exit
  -m <method>, --method <method>
                        SIEM API method name or NitroSession.PARAMS keyword.
                        Exemple: 'v2/qryGetSelectFields' or 'get_possible_fields',
                        see https://mfesiem.github.io/docs/msiempy/core/session.html
                        . (default: None)
  -d <JSON string or file>, --data <JSON string or file>
                        POST data, in the case of a API method name call. (default:
                        {})
  -a <key>=<value> [<key>=<value> ...], --args <key>=<value> [<key>=<value> ...]
                        NitroSession.PARAMS interpolation parameters, in the case of
                        a NitroSession.PARAMS keyword call. (default: [[]])
  -l, --list            List all supported SIEM API calls with keywords and
                        parameter mapping. Note that you can still request any
                        endpoint without paramater mapping. (default: False)
```
## Watchlists
```
```
"""
