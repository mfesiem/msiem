# McAfee SIEM Command Line Interface

```
                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_|
     
 McAfee SIEM Command Line Interface
 ```

Based on the work of [andywalen](https://github.com/andywalden) and the [McAfee SIEM API Python wrapper](https://github.com/mfesiem/msiempy)

## Installation
```bash
$ pip install msiem --upgrade
```

## Command Line Interface overview
### Config
```bash
$ msiem config --help
```
#### Exemples
Set the ESM configuration (`host/user/password`) :  
```bash
$ msiem config --set esm
```
Set the general configuration (`verbose/quiet/logfile/timeout/ssl_verify`) :  
```bash
$ msiem config --set general
```
Print the configuration fields :  
```bash
$ msiem config --print
```
### Alarms
```bash
$ msiem alarms --help
  ```
#### Exemples
Acknowledges the (unacknowledged) alarms triggered in the last 3 days that mention "`HTTP: SQL Injection Attempt Detected`" in the triggered event name and destinated to `10.55.16.99` :  
```bash
$ msiem alarms --action acknowledge \
  -t LAST_24_HOURS \
  --status unacknowledged \
  --filters "ruleName=HTTP: SQL Injection Attempt Detected" "destIp=10.55.16.99"
```
<details><summary>See output</summary>
<p>

```
    
INFO - New NitroSession instance
INFO - Getting alarms infos...
INFO - Getting events infos...
INFO - 2 alarms matching your filter(s)
WARNING - The query is not complete... Try to divide in more slots or increase the requests_size, page_size or limit
|         alarmName         |    triggeredDate    | acknowledgedDate |                                                    events                                                    |
| IPS - High Severity Event | 09/18/2019 07:50:14 |                  | |               ruleName               |      srcIp      |     destIp    | srcUser |   host  |    sigId    | |
|                           |                     |                  | | HTTP: SQL Injection Attempt Detected | 103.127.206.228 | 10.55.16.99 |         | MTL-IPS | 305-4531511 | |
| IPS - High Severity Event | 09/18/2019 07:50:14 |                  | |               ruleName               |      srcIp      |     destIp    | srcUser |   host  |    sigId    | |
|                           |                     |                  | | HTTP: SQL Injection Attempt Detected | 103.127.206.228 | 10.55.16.99 |         | MTL-IPS | 305-4531511 | |
Are you sure you want to acknowledge those alarms ? [y/n]y
```
</p>
</details>

Prints the specified fields of alarms triggered in the specified time range that match "`IPS`" in the alarm name with the minimum amount of information possible (events informations aren't retreived) : 
```bash
$ msiem alarms --t1 2019-09-01T00:00:00 \
  --t2 2019-09-04T23:59:59 \
  --no_events \
  --filter alarmName=IPS \
  --alarms_fields triggeredDate acknowledgedDate acknowledgedUsername alarmName
```
Let's note the WARNING here, the query counldn't complete because the `--page_size` argument is defaulted to 100. Increase this value to retreive more alarms at a time.
<details><summary>See output</summary>
<p>

```
INFO - New NitroSession instance
INFO - 30 alarms matching your filter(s)
WARNING - The query is not complete... Try to divide in more slots or increase the requests_size, page_size or limit
|    triggeredDate    |   acknowledgedDate  | acknowledgedUsername |          alarmName           |
| 09/04/2019 23:58:23 | 09/05/2019 09:02:06 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 23:33:23 | 09/05/2019 09:05:54 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 21:38:13 | 09/05/2019 09:03:19 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 20:13:13 | 09/05/2019 09:02:32 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 19:53:13 | 09/05/2019 09:02:47 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 19:53:13 | 09/05/2019 09:03:01 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 19:53:13 | 09/05/2019 09:03:51 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 18:53:13 | 09/05/2019 09:04:53 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 17:53:13 | 09/05/2019 09:05:12 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 17:48:13 | 09/05/2019 09:04:30 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 16:23:03 | 09/05/2019 09:04:46 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 14:38:03 | 09/04/2019 15:08:19 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 14:38:03 | 09/04/2019 15:08:23 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 14:38:03 | 09/04/2019 15:08:33 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 14:38:03 | 09/04/2019 15:08:41 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 12:47:53 | 09/04/2019 15:14:25 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 12:47:53 | 09/04/2019 15:14:26 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 10:32:20 | 09/05/2019 09:37:22 |   username@domain   | FORTI - IPS - Critical Event |
| 09/04/2019 09:57:43 | 09/04/2019 15:24:33 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 09:57:43 | 09/04/2019 15:24:38 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 09:57:43 | 09/04/2019 15:41:05 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 08:47:43 | 09/04/2019 15:42:18 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 08:47:43 | 09/04/2019 15:42:22 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 07:22:43 | 09/04/2019 08:23:52 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 06:42:43 | 09/04/2019 08:24:17 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 06:42:43 | 09/04/2019 08:24:38 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 06:17:43 | 09/04/2019 15:42:59 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 06:17:43 | 09/04/2019 15:43:03 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 06:12:43 | 09/04/2019 08:25:28 |   username@domain   |  IPS - High Severity Event   |
| 09/04/2019 06:12:43 | 09/04/2019 08:26:28 |   username@domain   |  IPS - High Severity Event   |
```
</p>
</details>

Prints the alarms triggered in the last hour using the query module to retreive events informations and request for specific fields : 
```bash
$ msiem alarms -t LAST_HOUR \
  --query_events \
  --alarms_fields acknowledgedDate alarmName events
  --events_fields Alert.LastTime Rule.msg Alert.DstIP
```
<details><summary>See output</summary>
<p>

```

INFO - New NitroSession instance
INFO - Getting alarms infos...
INFO - Getting events infos...
INFO - 8 alarms matching your filter(s)
|   acknowledgedDate  |             alarmName              |                                                          events                                                         |
|                     |     IPS - High Severity Event      | |    Alert.LastTime   |                                    Rule.msg                                    | Alert.DstIP  | |
|                     |                                    | | 09/18/2019 14:33:17 | HTTP: WordPress portable phpmyadmin plugin authentication bypass vulnerability | 159.33.18.10 | |
|                     |     IPS - High Severity Event      |                      |    Alert.LastTime   |               Rule.msg               | Alert.DstIP  |                      |
|                     |                                    |                      | 09/18/2019 14:31:47 | HTTP: SQL Injection Attempt Detected | 155.32.18.10 |                      |
| 09/18/2019 14:33:40 | FORTI - DNS Access to Botnet C & C |                             |    Alert.LastTime   |         Rule.msg        | Alert.DstIP  |                            |
|                     |                                    |                             | 09/18/2019 14:32:35 | FortiGate_UTM DNS Event | 164.24.65.42 |                            |
|                     |     IPS - High Severity Event      |     |    Alert.LastTime   |                                Rule.msg                               |  Alert.DstIP   |    |
|                     |                                    |     | 09/18/2019 14:21:07 | NETBIOS-SS: Samba Remote Code Execution Vulnerability (CVE-2017-7494) | 10.165.199.111 |    |
|                     |     IPS - High Severity Event      |     |    Alert.LastTime   |                                Rule.msg                               |  Alert.DstIP   |    |
|                     |                                    |     | 09/18/2019 14:21:07 | NETBIOS-SS: Samba Remote Code Execution Vulnerability (CVE-2017-7494) | 10.164.55.151  |    |
|                     |    SSH Login failed on Juniper     |                                |    Alert.LastTime   |      Rule.msg     | Alert.DstIP |                                |
|                     |                                    |                                | 09/18/2019 14:24:24 | SSHD_LOGIN_FAILED |      ::     |                                |
| 09/18/2019 14:03:00 | FORTI - DNS Access to Botnet C & C |                             |    Alert.LastTime   |         Rule.msg        | Alert.DstIP |                             |
|                     |                                    |                             | 09/18/2019 14:02:06 | FortiGate_UTM DNS Event |   8.8.8.8   |                             |
|                     |        DDI - Critical Event        |                        |    Alert.LastTime   |             Rule.msg            |  Alert.DstIP  |                        |
|                     |                                    |                        | 09/18/2019 13:58:08 | File in Suspicious Objects list | 10.123.11.163 |                        |
```
</p>
</details>

Prints the alarms triggered in the the last 30 minutes as JSON structure with the maximum amount of information possible : 
```bash
$ msiem alarms -t LAST_30_MINUTES --json
```
<details><summary>See output</summary>
<p>

```
INFO - New NitroSession instance
INFO - Getting alarms infos...
INFO - Getting events infos...
INFO - 3 alarms matching your filter(s)
[
    {
        "conditionType": 49,
        "summary": "Field match alarm triggered on TOR-DDI",
        "assignee": "NGCP",
        "severity": 80,
        "id": {
            "value": 725489
        },
        "triggeredDate": "09/18/2019 14:00:44",
        "acknowledgedDate": "",
        "acknowledgedUsername": "",
        "alarmName": "DDI - Critical Event",
        "filters": null,
        "queryId": "0",
        "alretRateMin": "0",
        "alertRateCount": "0",
        "percentAbove": "0",
        "percentBelow": "0",
        "offsetMinutes": "0",
        "maximumConditionTriggerFrequency": null,
        "useWatchlist": null,
        "matchField": null,
        "matchValue": null,
        "assigneeId": "1",
        "escalatedDate": null,
        "caseId": "0",
        "caseName": null,
        "iocName": null,
        "iocId": "0",
        "description": null,
        "actions": "1|| ",
        "events": [
            {
                "severity": 80,
                "eventCount": 1,
                "command": "",
                "subtype": "pass",
                "cases": [],
                "ipsId": {
                    "id": 144128388406182400
                },
                "ruleName": "File in Suspicious Objects list",
                "alertId": 801428400,
                "destIp": "10.155.16.1",
                "lastTime": "09/18/2019 13:58:08",
                "flowId": 0,
                "destPort": "60160",
                "destMac": "00:00:0C:07:AC:01",
                "firstTime": "09/18/2019 13:58:08",
                "flowSessionId": 0,
                "reviewed": "F",
                "srcIp": "23.64.57.23",
                "srcMac": "00:09:0F:09:03:0C",
                "srcPort": "http",
                "vlan": 0,
                "sigId": "473-708",
                "sigDesc": "",
                "sigText": "",
                "duration": "00:00:00.000",
                "deviceName": "MTL-ERC-2650 - Deep Discovery - MTL-DDI - TOR-DDI",
                "normId": 1343225856,
                "app": "HTTP-",
                "srcUser": "",
                "destUser": "",
                "remedyCaseId": 0,
                "remedyTicketTime": null,
                "deviceTime": "09/18/2019 14:00:44",
                "remedyAnalyst": "",
                "sequence": 0,
                "trusted": 2,
                "sessionId": 0,
                "asnGeoSrcId": "1423146286932115461",
                "srcAsnGeo": "Cambridge, Massachusetts, United States, 02142",
                "asnGeoDestId": "0",
                "destAsnGeo": "",
                "normMessage": "Misc Application Event",
                "normDesc": "Indicates a miscellaneous application event.  Belongs to Application: The Application category indicates various application activities.",
                "archiveId": "6338207",
                "srcZone": "",
                "destZone": "",
                "srcGuid": "",
                "destGuid": "",
                "agg1Name": "",
                "agg1Value": "0.00000000000000E+000",
                "agg2Name": "",
                "agg2Value": "0.00000000000000E+000",
                "agg3Name": "",
                "agg3Value": "0.00000000000000E+000",
                "iocName": "",
                "iocId": 0,
                "customTypes": [
                    {
                        "fieldId": 1,
                        "fieldName": "AppID",
                        "definedFieldNumber": 1,
                        "unformattedValue": "5138163395327189285",
                        "formatedValue": "HTTP-"
                    },
                    {
                        "fieldId": 4259843,
                        "fieldName": "Filename",
                        "definedFieldNumber": 3,
                        "unformattedValue": "2148728525277381385",
                        "formatedValue": "AGC_6_3_0_73_osx10.zip"
                    },
                    {
                        "fieldId": 4,
                        "fieldName": "HostID",
                        "definedFieldNumber": 4,
                        "unformattedValue": "11008634256373089658",
                        "formatedValue": "a23-64-57-23.deploy.static.akamaitechnologies.com"
                    },
                    {
                        "fieldId": 4259841,
                        "fieldName": "URL",
                        "definedFieldNumber": 8,
                        "unformattedValue": "1365490746265658267",
                        "formatedValue": "http://agsupdate.adobe.com/osx/AGC_6_3_0_73_osx10.zip"
                    },
                    {
                        "fieldId": 65539,
                        "fieldName": "Destination_Hostname",
                        "definedFieldNumber": 21,
                        "unformattedValue": "8F8DBCE018CE44FB5CFD84E179C835A6",
                        "formatedValue": "10.147.16.156"
                    },
                    {
                        "fieldId": 65575,
                        "fieldName": "External_Hostname",
                        "definedFieldNumber": 22,
                        "unformattedValue": "6209F566FA0147769F1E67484E96167E",
                        "formatedValue": "agsupdate.adobe.com"
                    }
                ],
                "host": "a23-64-57-23.deploy.static.akamaitechnologies.com",
                "object": "",
                "domain": "",
                "protocol": "n/a",
                "note": ""
            }
        ]
    },
    {
        "conditionType": 48,
        "summary": "Field match alarm triggered on TOR-IPS G2/1-G2/2",
        "assignee": "NGCP",
        "severity": 80,
        "id": {
            "value": 725488
        },
        "triggeredDate": "09/18/2019 13:45:44",
        "acknowledgedDate": "",
        "acknowledgedUsername": "",
        "alarmName": "IPS - High Severity Event",
        "filters": null,
        "queryId": "0",
        "alretRateMin": "0",
        "alertRateCount": "0",
        "percentAbove": "0",
        "percentBelow": "0",
        "offsetMinutes": "0",
        "maximumConditionTriggerFrequency": null,
        "useWatchlist": null,
        "matchField": null,
        "matchValue": null,
        "assigneeId": "1",
        "escalatedDate": null,
        "caseId": "0",
        "caseName": null,
        "iocName": null,
        "iocId": "0",
        "description": null,
        "actions": "1|| ",
        "events": [
            {
                "severity": 70,
                "eventCount": 1,
                "command": "",
                "subtype": "alert",
                "cases": [],
                "ipsId": {
                    "id": 144126183208912640
                },
                "ruleName": "HTTP: SQL Injection Attempt Detected",
                "alertId": 801404801,
                "destIp": "155.32.35.12",
                "lastTime": "09/18/2019 13:41:09",
                "flowId": 0,
                "destPort": "n/a",
                "destMac": "00:00:00:00:00:00",
                "firstTime": "09/18/2019 13:41:09",
                "flowSessionId": 0,
                "reviewed": "F",
                "srcIp": "23.216.10.28",
                "srcMac": "00:00:00:00:00:00",
                "srcPort": "n/a",
                "vlan": 0,
                "sigId": "305-4531511",
                "sigDesc": "",
                "sigText": "",
                "duration": "00:00:00.000",
                "deviceName": "NSM - TOR-IPS - TOR-IPS G2/1-G2/2",
                "normId": 1343225856,
                "app": "HTTP",
                "srcUser": "",
                "destUser": "",
                "remedyCaseId": 0,
                "remedyTicketTime": null,
                "deviceTime": "09/18/2019 13:45:44",
                "remedyAnalyst": "",
                "sequence": 0,
                "trusted": 2,
                "sessionId": 0,
                "asnGeoSrcId": "1423146283710808064",
                "srcAsnGeo": "California, United States",
                "asnGeoDestId": "1351084288405161540",
                "destAsnGeo": "Ottawa, Ontario, Canada, K1Y",
                "normMessage": "Misc Application Event",
                "normDesc": "Indicates a miscellaneous application event.  Belongs to Application: The Application category indicates various application activities.",
                "archiveId": "0",
                "srcZone": "",
                "destZone": "",
                "srcGuid": "",
                "destGuid": "",
                "agg1Name": "",
                "agg1Value": "0.00000000000000E+000",
                "agg2Name": "",
                "agg2Value": "0.00000000000000E+000",
                "agg3Name": "",
                "agg3Value": "0.00000000000000E+000",
                "iocName": "",
                "iocId": 0,
                "customTypes": [
                    {
                        "fieldId": 1,
                        "fieldName": "AppID",
                        "definedFieldNumber": 1,
                        "unformattedValue": "20325061917139208",
                        "formatedValue": "HTTP"
                    },
                    {
                        "fieldId": 10,
                        "fieldName": "Object_Type",
                        "definedFieldNumber": 2,
                        "unformattedValue": "4857833489265330424",
                        "formatedValue": "Signature"
                    },
                    {
                        "fieldId": 3,
                        "fieldName": "DomainID",
                        "definedFieldNumber": 3,
                        "unformattedValue": "15619313100548066249",
                        "formatedValue": "My Company"
                    },
                    {
                        "fieldId": 4,
                        "fieldName": "HostID",
                        "definedFieldNumber": 4,
                        "unformattedValue": "13391635955911484534",
                        "formatedValue": "TOR-IPS"
                    },
                    {
                        "fieldId": 11,
                        "fieldName": "Method",
                        "definedFieldNumber": 5,
                        "unformattedValue": "4857833489265330424",
                        "formatedValue": "Signature"
                    },
                    {
                        "fieldId": 29,
                        "fieldName": "Interface",
                        "definedFieldNumber": 8,
                        "unformattedValue": "8950269003246828398",
                        "formatedValue": "G2/1-G2/2"
                    },
                    {
                        "fieldId": 30,
                        "fieldName": "Direction",
                        "definedFieldNumber": 10,
                        "unformattedValue": "10778667140275494521",
                        "formatedValue": "Inbound"
                    },
                    {
                        "fieldId": 65545,
                        "fieldName": "Event_Class",
                        "definedFieldNumber": 21,
                        "unformattedValue": "787A1A2D48ED1D51FB23BFAAAE977517",
                        "formatedValue": "Emergency Sigset Rules"
                    },
                    {
                        "fieldId": 65547,
                        "fieldName": "Message_ID",
                        "definedFieldNumber": 22,
                        "unformattedValue": "23AE849092BF224ECE33DA1B712C6CFF",
                        "formatedValue": "0x45253700"
                    },
                    {
                        "fieldId": 65540,
                        "fieldName": "Category",
                        "definedFieldNumber": 25,
                        "unformattedValue": "CCCCCBB3ED1AC4D7597E0B6827C9B318",
                        "formatedValue": "Exploit:Code/Script Execution"
                    }
                ],
                "host": "TOR-IPS",
                "object": "",
                "domain": "My Company",
                "protocol": "n/a",
                "note": ""
            }
        ]
    },
    {
        "conditionType": 48,
        "summary": "Field match alarm triggered on TOR-IPS G2/1-G2/2",
        "assignee": "NGCP",
        "severity": 80,
        "id": {
            "value": 725487
        },
        "triggeredDate": "09/18/2019 13:40:44",
        "acknowledgedDate": "",
        "acknowledgedUsername": "",
        "alarmName": "IPS - High Severity Event",
        "filters": null,
        "queryId": "0",
        "alretRateMin": "0",
        "alertRateCount": "0",
        "percentAbove": "0",
        "percentBelow": "0",
        "offsetMinutes": "0",
        "maximumConditionTriggerFrequency": null,
        "useWatchlist": null,
        "matchField": null,
        "matchValue": null,
        "assigneeId": "1",
        "escalatedDate": null,
        "caseId": "0",
        "caseName": null,
        "iocName": null,
        "iocId": "0",
        "description": null,
        "actions": "1|| ",
        "events": [
            {
                "severity": 70,
                "eventCount": 1,
                "command": "",
                "subtype": "alert",
                "cases": [],
                "ipsId": {
                    "id": 144126183208912640
                },
                "ruleName": "HTTP: SQL Injection Attempt Detected",
                "alertId": 801395683,
                "destIp": "155.32.35.12",
                "lastTime": "09/18/2019 13:39:08",
                "flowId": 0,
                "destPort": "http:80",
                "destMac": "00:00:00:00:00:00",
                "firstTime": "09/18/2019 13:39:08",
                "flowSessionId": 0,
                "reviewed": "F",
                "srcIp": "23.216.10.28",
                "srcMac": "00:00:00:00:00:00",
                "srcPort": "37780",
                "vlan": 0,
                "sigId": "305-4531511",
                "sigDesc": "",
                "sigText": "",
                "duration": "00:00:00.000",
                "deviceName": "NSM - TOR-IPS - TOR-IPS G2/1-G2/2",
                "normId": 1343225856,
                "app": "HTTP",
                "srcUser": "",
                "destUser": "",
                "remedyCaseId": 0,
                "remedyTicketTime": null,
                "deviceTime": "09/18/2019 13:40:44",
                "remedyAnalyst": "",
                "sequence": 0,
                "trusted": 2,
                "sessionId": 0,
                "asnGeoSrcId": "1423146283710808064",
                "srcAsnGeo": "California, United States",
                "asnGeoDestId": "1351084288405161540",
                "destAsnGeo": "Ottawa, Ontario, Canada, K1Y",
                "normMessage": "Misc Application Event",
                "normDesc": "Indicates a miscellaneous application event.  Belongs to Application: The Application category indicates various application activities.",
                "archiveId": "0",
                "srcZone": "",
                "destZone": "",
                "srcGuid": "",
                "destGuid": "",
                "agg1Name": "",
                "agg1Value": "0.00000000000000E+000",
                "agg2Name": "",
                "agg2Value": "0.00000000000000E+000",
                "agg3Name": "",
                "agg3Value": "0.00000000000000E+000",
                "iocName": "",
                "iocId": 0,
                "customTypes": [
                    {
                        "fieldId": 1,
                        "fieldName": "AppID",
                        "definedFieldNumber": 1,
                        "unformattedValue": "20325061917139208",
                        "formatedValue": "HTTP"
                    },
                    {
                        "fieldId": 10,
                        "fieldName": "Object_Type",
                        "definedFieldNumber": 2,
                        "unformattedValue": "4857833489265330424",
                        "formatedValue": "Signature"
                    },
                    {
                        "fieldId": 3,
                        "fieldName": "DomainID",
                        "definedFieldNumber": 3,
                        "unformattedValue": "15619313100548066249",
                        "formatedValue": "My Company"
                    },
                    {
                        "fieldId": 4,
                        "fieldName": "HostID",
                        "definedFieldNumber": 4,
                        "unformattedValue": "13391635955911484534",
                        "formatedValue": "TOR-IPS"
                    },
                    {
                        "fieldId": 11,
                        "fieldName": "Method",
                        "definedFieldNumber": 5,
                        "unformattedValue": "4857833489265330424",
                        "formatedValue": "Signature"
                    },
                    {
                        "fieldId": 29,
                        "fieldName": "Interface",
                        "definedFieldNumber": 8,
                        "unformattedValue": "8950269003246828398",
                        "formatedValue": "G2/1-G2/2"
                    },
                    {
                        "fieldId": 4259886,
                        "fieldName": "Device_URL",
                        "definedFieldNumber": 9,
                        "unformattedValue": "1066699811985063715",
                        "formatedValue": "/user.php?act=login"
                    },
                    {
                        "fieldId": 30,
                        "fieldName": "Direction",
                        "definedFieldNumber": 10,
                        "unformattedValue": "10778667140275494521",
                        "formatedValue": "Inbound"
                    },
                    {
                        "fieldId": 65545,
                        "fieldName": "Event_Class",
                        "definedFieldNumber": 21,
                        "unformattedValue": "787A1A2D48ED1D51FB23BFAAAE977517",
                        "formatedValue": "Emergency Sigset Rules"
                    },
                    {
                        "fieldId": 65547,
                        "fieldName": "Message_ID",
                        "definedFieldNumber": 22,
                        "unformattedValue": "23AE849092BF224ECE33DA1B712C6CFF",
                        "formatedValue": "0x45253700"
                    },
                    {
                        "fieldId": 65546,
                        "fieldName": "Request_Type",
                        "definedFieldNumber": 24,
                        "unformattedValue": "E67072FD01A29DC00095379A46F1D315",
                        "formatedValue": "GET"
                    },
                    {
                        "fieldId": 65540,
                        "fieldName": "Category",
                        "definedFieldNumber": 25,
                        "unformattedValue": "CCCCCBB3ED1AC4D7597E0B6827C9B318",
                        "formatedValue": "Exploit:Code/Script Execution"
                    },
                    {
                        "fieldId": 4259873,
                        "fieldName": "Description",
                        "definedFieldNumber": 27,
                        "unformattedValue": "599919BE03A42FD9FCD6414277B0E5FA",
                        "formatedValue": "HTTP Request Method == GET ;;; HTTP URI == /user.php?act=login;;; HTTP User-Agent ==  Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2);;; HTTP Host ==  www.cbcsports.ca;;;"
                    }
                ],
                "host": "TOR-IPS",
                "object": "",
                "domain": "My Company",
                "protocol": "n/a",
                "note": ""
            }
        ]
    }
]
```
</p>
</details>


### ESM
  ```bash
$ msiem esm --help
  ```


