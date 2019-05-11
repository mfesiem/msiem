### McAfee SIEM Command Line Interface and Python API
(Dev) [![Build Status](https://travis-ci.com/tristanlatr/msiem.svg?branch=master)](https://travis-ci.com/tristanlatr/msiem)

Based on the work of andywalen : https://github.com/andywalden

#### Installation
```
pip install msiem
msiem config --set auth
python3 setup.py test
```

#### Command Line Interface Help
```
$ msiem --help
usage: Use "msiem --help" for more information

McAfee SIEM Command Line Interface and Python API

positional arguments:
  {config,alarms}

optional arguments:
  -h, --help       show this help message and exit
  --version        Show version
  -v, --verbose    Increase output verbosity

$ msiem alarms --help

optional arguments:
  -h, --help            show this help message and exit
  --ack                 Acknowledge the alarms
  --unack               Unacknowledge the alarms
  --delete              Delete the alarms
  --time_range time_range, -t time_range
                        Timerange in['CUSTOM', 'LAST_MINUTE',
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
  --status status       Status of the alarm [ack|unack|all]
  --filters '<key>=<match>' ['<key>=<match>' ...], -f '<key>=<match>' ['<key>=<match>' ...]
                        List of filters
  --summary sumary      Alarm summary filter
  --assignee assignee   Alarm assignee filter
  --severity severity   Alarm severity filter
  --trigdate trigdate   Alarm trigdate filter
  --ackdate ackdate     Alarm ackdate filter
  --ackuser ackuser     Alarm ackuser filter
  --name name           Alarm name filter
  --msg msg             Event msg filter
  --count count         Event count filter
  --srcip srcip         Event srcip filter
  --dstip dstip         Event dstip filter
  --protocol protocol   Event protocol filter
  --date date           Event date filter
  --subtype subtype     Event subtype filter

$ msiem config --help
usage: Use "msiem --help" for more information config [-h] [--list] [--set]

optional arguments:
  -h, --help  show this help message and exit
  --list      List configuration fields
  --set       Will inveractively prompt for configuration settings
```

#### CLI exemple
```
msiem alarms --ack -t LAST_3_DAYS --status ackowledged --filters msg=Wordpress srcip=2.150. dstip=10.1.
```

#### Python exemple
```
alarms = msiem.query.AlarmQuery(
    time_range='LAST_24_HOURS',
    filters=[('alarmName', 'High Severity Event'),
        ('severity', [80,85,90,95,100]),
        ('ruleMessage', 'HTTP')]
    ).execute()
alarms.show()
alarms.acknowledge()
```