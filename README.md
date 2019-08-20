### McAfee SIEM Command Line Interface
[![Build Status](https://travis-ci.com/tristanlatr/msiem.svg?branch=master)](https://travis-ci.com/tristanlatr/msiem)

```                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_|
     
 McAfee SIEM Command Line Interface

   ```

Based on the work of [andywalen](https://github.com/andywalden) and the [McFee esm API wrapper](https://github.com/mfesiem/msiempy)

#### Installation
```
pip install msiem
```

#### Command Line Interface Help
##### Config
```bash
$ msiem config --help

 
usage: Use "msiem <command> --help" for more information. config
       [-h] [--print] [--set section]

optional arguments:
  -h, --help     show this help message and exit
  --print        Print configuration fields (default: False)
  --set section  Will inveractively prompt for specified configuration section
                 : esm or general (default: None)

```
##### Alarms
```bash
$ msiem alarms --help
                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_|
     
 McAfee SIEM Command Line Interface

usage: Use "msiem <command> --help" for more information. alarms
       [-h] [--action action] [--force] [--time_range time_range]
       [--start_time time] [--end_time time] [--status status]
       [--filters '<field>=<match>' ['<field>=<match>' ...]]
       [--page_size page_size] [--workers workers] [--max_queries max_queries]
       [--query_delta delta] [--query_slots slots] [--no_events]
       [--query_events]

optional arguments:
  -h, --help            show this help message and exit
  --action action       What to do with the alarms, if not specified will
                        print only (default: None)
  --force               Will not prompt for confirmation to do the specified
                        action (default: False)
  --time_range time_range, -t time_range
                        Timerange, choose from CUSTOM, LAST_MINUTE,
                        LAST_10_MINUTES, LAST_30_MINUTES, LAST_HOUR,
                        CURRENT_DAY, PREVIOUS_DAY, LAST_24_HOURS, LAST_2_DAYS,
                        LAST_3_DAYS, CURRENT_WEEK, PREVIOUS_WEEK,
                        CURRENT_MONTH, PREVIOUS_MONTH, CURRENT_QUARTER,
                        PREVIOUS_QUARTER, CURRENT_YEAR, PREVIOUS_YEAR
                        (default: None)
  --start_time time, --t1 time
                        Start trigger date (default: None)
  --end_time time, --t2 time
                        End trigger date (default: None)
  --status status       Status of the alarm (default: all)
  --filters '<field>=<match>' ['<field>=<match>' ...], -f '<field>=<match>' ['<field>=<match>' ...]
                        List of field/matchvalue filters. Alarm related fields
                        can be : id, summary, assignee, severity,
                        triggeredDate, acknowledgedDate, acknowledgedUsername,
                        alarmName, events. Event related fields can be (if
                        --query_events) : Rule.msg, Alert.SrcPort,
                        Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac,
                        Alert.DstMac, Alert.LastTime, Rule.NormID,
                        Alert.DSIDSigID, Alert.IPSIDAlertID. Or : ruleName,
                        srcIp, destIp, protocol, lastTime, subtype, destPort,
                        destMac, srcMac, srcPort, deviceName, sigId, normId,
                        srcUser, destUser, normMessage, normDesc, host,
                        domain, ipsId. (default: None)
  --page_size page_size, -p page_size
                        Size of requests (default: 50)
  --workers workers     Number of max asynch workers (default: 10)
  --max_queries max_queries
                        Number of times the query can be slipted to get more
                        data (default: 0)
  --query_delta delta   The timedelta of first time slots division (default:
                        12h)
  --query_slots slots   The number of time slots division after the first one
                        (default: 4)
  --no_events           Do not load unecessary event data in order to filter
                        (default: False)
  --query_events        Use the query API query module to retreive events,
                        much more effcient (default: False)
  ```
###### Exemple
```
msiem alarms --ackowledge -t LAST_3_DAYS --status unackowledged --filters ruleName=Wordpress destIp=10.1.155.33
```
##### ESM
  ```bash
$ msiem esm --help 
usage: Use "msiem <command> --help" for more information. esm
       [-h] [--version] [--time] [--disks] [--ram] [--callhome] [--status]
       [--timezones]

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
               rulesAndSoftLastCheck, rulesAndSoftNextCheck (default: False)
  --timezones  Current ESM timezone (default: False)
  ```


