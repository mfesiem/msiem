### McAfee SIEM Command Line Interface and Python API
(Dev) [![Build Status](https://travis-ci.com/tristanlatr/msiem.svg?branch=master)](https://travis-ci.com/tristanlatr/msiem)

Based on the work of [andywalen](https://github.com/andywalden) and the [McFee esm API wrapper](https://github.com/mfesiem/msiempy)

#### Installation
```
pip install msiem
```

#### Command Line Interface
```bash
$ msiem alarms --help
usage: Use "msiem <command> --help" for more information. alarms
       [-h] [--action action] [--force] [--time_range time_range]
       [--start_time time] [--end_time time] [--status status]
       [--filters '<key>=<match>' ['<key>=<match>' ...]]
       [--page_size page_size] [--workers workers] [--max_queries max_queries]
       [--query_delta delta] [--query_slots slots] [--no_events]
       [--query_events]

optional arguments:
  -h, --help            show this help message and exit
  --action action       What to do with the alarms:
                        [acknowledge|unacknowledge|delete]
  --force               Will not prompt for confirmation to do the specified
                        action
  --time_range time_range, -t time_range
                        Timerange: ['CUSTOM', 'LAST_MINUTE',
                        'LAST_10_MINUTES', 'LAST_30_MINUTES', 'LAST_HOUR',
                        'CURRENT_DAY', 'PREVIOUS_DAY', 'LAST_24_HOURS',
                        'LAST_2_DAYS', 'LAST_3_DAYS', 'CURRENT_WEEK',
                        'PREVIOUS_WEEK', 'CURRENT_MONTH', 'PREVIOUS_MONTH',
                        'CURRENT_QUARTER', 'PREVIOUS_QUARTER', 'CURRENT_YEAR',
                        'PREVIOUS_YEAR']
  --start_time time, --t1 time
                        Start trigger date
  --end_time time, --t2 time
                        End trigger date
  --status status       Status of the alarm [acknowledged|unacknowledged|all]
  --filters '<key>=<match>' ['<key>=<match>' ...], -f '<key>=<match>' ['<key>=<match>' ...]
                        List of filters. Alarm related keys can be : - id :
                        The ID of the triggered alarm - summary : The summary
                        of the triggered alarm - assignee : The assignee for
                        this triggered alarm - severity : The severity for
                        this triggered alarm - triggeredDate : The date this
                        alarm was triggered - acknowledgedDate : The date this
                        triggered alarm was acknowledged -
                        acknowledgedUsername : The user that acknowledged this
                        triggered alarm - alarmName : The name of the alarm
                        that was triggered - events : A string representation
                        of the triggering events See : https://mfesiem.github.
                        io/docs/msiempy/alarm.html#msiempy.alarm.Alarm Event
                        related keys could be (depending of config) : -
                        Rule.msg - Alert.SrcPort - Alert.DstPort - Alert.SrcIP
                        - Alert.DstIP - Alert.SrcMac - Alert.DstMac -
                        Alert.LastTime - Rule.NormID - Alert.DSIDSigID -
                        Alert.IPSIDAlertID - ruleName - srcIp - destIp -
                        protocol - lastTime - subtype - destPort - destMac -
                        srcMac - srcPort - deviceName - sigId - normId -
                        srcUser - destUser - normMessage - normDesc - host -
                        domain - ipsId
  --page_size page_size, -p page_size
                        Size of requests
  --workers workers     Number of max asynch workers
  --max_queries max_queries
                        Number of times the query can be slipted to get more
                        data
  --query_delta delta   The timedelta of first time slots division
  --query_slots slots   The number of time slots division after the first one
  --no_events           Do not load unecessary event data in order to filter
  --query_events        Use the query API query module to retreive events
  ```

  ```bash
   msiem config --help
  usage: Use "msiem <command> --help" for more information. config
        [-h] [--list] [--set]

  optional arguments:
    -h, --help  show this help message and exit
    --list      List configuration fields
    --set       Will inveractively prompt for configuration settings
  ```

#### Exemple
```
msiem alarms --ackowledge -t LAST_3_DAYS --status ackowledged --filters ruleName=Wordpress srcIp=2.150. destIp=10.1.
```
