# msiem(1)

Manual

msiem

<a name="synopsis"></a>

# Synopsis

```
msiem [-h] [-V] {config,alarms,esm,ds,events,wl,api} ...
```

<a name="description"></a>

# Description

McAfee SIEM Command Line Interface 0.3.4dev  

License: MIT 
Credits: Andy Walden, Tristan Landes  

Run \`msiem &lt;command&gt; --help\` for more information about a sub-command.

<a name="options"></a>

# Options


**Sub-commands**

* **msiem** _config_  
  Set and print your msiempy config.  
* **msiem** _alarms_  
  Query alarms with alarms and events based regex filters. Print, acknowledge, unacknowledge and delete alarms.  
* **msiem** _esm_  
  Show ESM version and misc informations regarding your ESM.  
* **msiem** _ds_  
  Add datasources from CSV or INI files, list, search, remove.  
* **msiem** _events_  
  Query events with any simple filter. Add a note to events.  
* **msiem** _wl_  
  Manage watchlists. Export, import values.  
* **msiem** _api_  
  Quickly make API requests to any enpoints with any data.  

<a name="options-msiem-config"></a>

# Options 'msiem config'

usage: msiem config [-h] [--print] [--set '&lt;section&gt;' ['&lt;option&gt;' '&lt;value&gt;']
                    ['&lt;section&gt;' ['&lt;option&gt;' '&lt;value&gt;'] ...]]

Set and print your msiempy config.  

Set your ESM hostname/user/password interactively:

    $ msiem confi --set esm

Set the general config verbose/quiet/logfile/timeout/ssl_verify interactively:

    $ msiem config --set general

Enable quiet mode (no infos or warnings):

    $ msiem config --set general quiet true --set general verbose false
    



* **--print**  
  Print configuration fields, password base 64 truncated from the output. 
  
* **--set** '&lt;section&gt;' ['&lt;option&gt;' '&lt;value&gt;'] ['&lt;section&gt;' ['&lt;option&gt;' '&lt;value&gt;'] ...]  
  Set the config option to the specified value if passed (can be repeated), OR inveractively prompt for specified configuration section: 'esm' or 'general'.
  

<a name="options-msiem-alarms"></a>

# Options 'msiem alarms'

usage: msiem alarms [-h] [--action action] [--force] [--time_range time_range]
                    [--start_time time] [--end_time time] [--status status]
                    [--filters '&lt;field&gt;=&lt;regex&gt;' ['&lt;field&gt;=&lt;regex&gt;' ...]]
                    [--event_filters '&lt;field&gt;=&lt;regex&gt;' ['&lt;field&gt;=&lt;regex&gt;' ...]]
                    [--alarms_fields list of fields [list of fields ...]]
                    [--events_fields list of fields [list of fields ...]]
                    [--json] [--page_size page_size] [--pages pages]
                    [--no_events] [--query_events]

Query alarms with alarms and events based regex filters.  
Print, acknowledge, unacknowledge and delete alarms.  

Exemples:  

Acknowledges the (unacknowledged) alarms triggered in the last 
3 days that mention "HTTP: SQL Injection Attempt Detected" in 
the triggered event name and destinated to 10.55.16.99 :

    $ msiem alarms --action acknowledge -t LAST_24_HOURS --status unacknowledged --filters "ruleName=HTTP: SQL Injection Attempt Detected" "destIp=10.55.16.99"

Save the current day alarms as JSON:

    $ msiem alarms -t CURRENT_DAY --no_events --json

    



* **--action** action  
  What to do with the alarms, if not specified will print only. Chose from 'acknowledge','unacknowledge','delete'
  
* **--force**  
  Will not prompt for confirmation to do the specified action
  
* **--time\_range** time_range, **-t** time_range  
  Timerange, choose from CUSTOM, LAST_MINUTE, LAST_10_MINUTES, LAST_30_MINUTES, LAST_HOUR, CURRENT_DAY, PREVIOUS_DAY, LAST_24_HOURS, LAST_2_DAYS, LAST_3_DAYS, CURRENT_WEEK, PREVIOUS_WEEK, CURRENT_MONTH, PREVIOUS_MONTH, CURRENT_QUARTER, PREVIOUS_QUARTER, CURRENT_YEAR, PREVIOUS_YEAR
  
* **--start\_time** time, **--t1** time  
  Start trigger date
  
* **--end\_time** time, **--t2** time  
  End trigger date
  
* **--status** status  
  Status of the alarm. Chose from 'acknowledged','unacknowledged','all'
  
* **--filters** '&lt;field&gt;=&lt;regex&gt;' ['&lt;field&gt;=&lt;regex&gt;' ...], **-f** '&lt;field&gt;=&lt;regex&gt;' ['&lt;field&gt;=&lt;regex&gt;' ...]  
  List of alarm related field/matchvalue filters. Repeatable. 
      Alarm related fields can be : id, summary, assignee, severity, triggeredDate, acknowledgedDate, acknowledgedUsername, alarmName, events, and others
  
* **--event\_filters** '&lt;field&gt;=&lt;regex&gt;' ['&lt;field&gt;=&lt;regex&gt;' ...], **-e** '&lt;field&gt;=&lt;regex&gt;' ['&lt;field&gt;=&lt;regex&gt;' ...]  
  List of triggering event related field/matchvalue filters. Repeatable.
      Event related fields can be : ruleName, srcIp, destIp, protocol, lastTime, subtype, destPort, destMac, srcMac, srcPort, deviceName, sigId, normId, srcUser, destUser, normMessage, normDesc, host, domain, ipsId, etc...
      Or (if --query_events) : Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID, etc...
  
* **--alarms\_fields** list of fields [list of fields ...]  
  List of fields that appear in the alarm table. Overwritten by --json
  
* **--events\_fields** list of fields [list of fields ...]  
  List of fields that appear in the events sub tables. Default value: ['ruleName', 'srcIp', 'destIp']. If you use --query_events, this list will be used to query needed values, you must specify all fields you want to filter on with ewvent_filters. Default value if --query_events: ['Rule.msg', 'SrcIP', 'DstIP']. Overwritten by --json.
  
* **--json**  
  Prints only a JSON object to STDOUT output.  
  
* **--page\_size** page_size, **-p** page_size  
  Size of requests
  
* **--pages** pages, **-n** pages  
  Number of alarm pages to load
  
* **--no\_events**  
  Do not load the complete trigerring events informations. On SIEM v11.x, still load the events infos from notifyGetTriggeredNotification. (Else events field is a string).  
  
* **--query\_events**  
  Use the query module to retreive events, much more effcient. Event keys will be like 'Alert.SrcIP' instead of 'srcIp'
  

<a name="options-msiem-esm"></a>

# Options 'msiem esm'

usage: msiem esm [-h] [--version] [--time] [--disks] [--ram] [--callhome]
                 [--status] [--timezones]

Show ESM version and misc informations regarding your ESM.
    



* **--version**  
  Show ESM version
  
* **--time**  
  time (GMT)
  
* **--disks**  
  disk status
  
* **--ram**  
  ram status
  
* **--callhome**  
  True/False if callhome is active/not active
  
* **--status**  
  Statuses and a few other less interesting details : autoBackupEnabled, autoBackupDay, backupLastTime, backupNextTime, rulesAndSoftwareCheckEnabled, rulesAndSoftLastCheck, rulesAndSoftNextCheck
  
* **--timezones**  
  Current ESM timezone
  

<a name="options-msiem-ds"></a>

# Options 'msiem ds'

usage: msiem ds [-h] [-a &lt;file or folder&gt;] [-s [term]] [-l]
                [--delete &lt;datasource ID&gt; [&lt;datasource ID&gt; ...]]
                [--deleteclients &lt;datasource ID&gt; [&lt;datasource ID&gt; ...]]
                [--force]

Add datasources from CSV or INI files, list, search, remove.  

INI format: Single datasource per file.  
            
    [datasource]
    # name of datasource (required)
    name=testing_datasource
    # ip of datasource (ip or hostname required)
    ds_ip=10.10.1.34
    # hostname of te new datasource
    hostname=
    # type of datasource (required)
    type_id=65
    # id of parent device (required)
    parent_id=144116287587483648
    # True value designate a client datasource 
    client=

CSV Format: Multiple datasources per file

    name,ds_ip,hostname,type_id,parent_id,client
    Test_ds_1,10.10.1.41,datasource11.domain.com,65,144116287587483648,
    Test_ds_2,10.10.1.42,datasource12.domain.com,65,144116287587483648,
    Test_ds_3,10.10.1.43,datasource13.domain.com,65,144116287587483648,

Add Datasources with: 

    $ msiem ds --add "File or folder"
    



* **-a** &lt;file or folder&gt;, **--add** &lt;file or folder&gt;  
  Scan a directory or a file for new Datasource files and add them to the ESM. Datasources can be defined in CSV or INI format (see README.md).  
  
* **-s** [term], **--search** [term]  
  Search for datasource name, hostname, or IP.May require quotes around the name if thereare spaces.
  
* **-l**, **--list**  
  Display datasources.
  
* **--delete** &lt;datasource ID&gt; [&lt;datasource ID&gt; ...], **--remove** &lt;datasource ID&gt; [&lt;datasource ID&gt; ...]  
  Deletes the datasource and all the data. Be careful.
  
* **--deleteclients** &lt;datasource ID&gt; [&lt;datasource ID&gt; ...]  
  Deletes the datasource's clients and all the data. Be careful.
  
* **--force**  
  Do not ask the user input before deletion of the datasources / datasources client.
  

<a name="options-msiem-events"></a>

# Options 'msiem events'

usage: msiem events [-h] [--time_range time_range] [--start_time &lt;time&gt;]
                    [--end_time &lt;time&gt;] [--filters &lt;filter&gt; [&lt;filter&gt; ...]]
                    [--fields &lt;field&gt; [&lt;field&gt; ...]] [--json] [--limit &lt;int&gt;]
                    [--max &lt;int&gt;] [--grouped] [--add_note &lt;file or text&gt;]
                    [--listfields] [--listfilters]

Query events with filters, add note to events.  

With simple filters:

    $ msiem events --filters DstIP=127.0.0.1 SrcIP=22.0.0.0/8 --fields SrcIP DstIP   

Query events with pecific operatior and multiple values filters (filters are ANDed together inside a group filter). 
Print the results as JSON.  

    $ msiem events --filter SrcIP IN 22.0.0.0/8 10.0.0.0/8 --filter DSIDSigID IN 49190-4294967295 --fields SrcIP DstIP Rule.msg DSIDSigID --json
    



* **--time\_range** time_range, **-t** time_range  
  Timerange, choose from CUSTOM, LAST_MINUTE, LAST_10_MINUTES, LAST_30_MINUTES, LAST_HOUR, CURRENT_DAY, PREVIOUS_DAY, LAST_24_HOURS, LAST_2_DAYS, LAST_3_DAYS, CURRENT_WEEK, PREVIOUS_WEEK, CURRENT_MONTH, PREVIOUS_MONTH, CURRENT_QUARTER, PREVIOUS_QUARTER, CURRENT_YEAR, PREVIOUS_YEAR
  
* **--start\_time** &lt;time&gt;, **--t1** &lt;time&gt;  
  Start trigger date
  
* **--end\_time** &lt;time&gt;, **--t2** &lt;time&gt;  
  End trigger date
  
* **--filters** &lt;filter&gt; [&lt;filter&gt; ...], **-f** &lt;filter&gt; [&lt;filter&gt; ...]  
  List of Event field/value filters: '&lt;field&gt;=&lt;value&gt;' or '&lt;field&gt;' '&lt;operator&gt;' '&lt;value1&gt;' '&lt;value2&gt;...'. Repeatable. Will generate only EsmBasicValue filters.   
      Filter fields can be: Rule.msg, Alert.SrcPort, Alert.DstPort, Alert.SrcIP, Alert.DstIP, Alert.SrcMac, Alert.DstMac, Alert.LastTime, Rule.NormID, Alert.DSIDSigID, Alert.IPSIDAlertID, etc...
  
* **--fields** &lt;field&gt; [&lt;field&gt; ...]  
  List of fields that appear in the events table. Default value: ['Rule.msg', 'SrcIP', 'DstIP']. 
  
* **--json**  
  Prints only a JSON object to STDOUT output.  
  
* **--limit** &lt;int&gt;  
  Size of requests
  
* **--max** &lt;int&gt;, **--max\_query\_depth** &lt;int&gt;  
  Maximum number of reccursive time based divisions the loading process can apply to the query in order to load all events
  
* **--grouped**  
  Indicate a grouped events query, a IPSID filter must be provided and only one field value is accepted. 
  
* **--add\_note** &lt;file or text&gt;  
  Add a note to the events matching the filters. 
  
* **--listfields**  
  List all possible fields names
  
* **--listfilters**  
  List all possible fields names usable in filters
  

<a name="options-msiem-wl"></a>

# Options 'msiem wl'

usage: msiem wl [-h] [-l] [-t] [-e &lt;wl_name&gt;]
                [--add &lt;wl_name&gt; &lt;wl_type&gt; &lt;wl_name&gt; &lt;wl_type&gt;]
                [--delete &lt;wl ID&gt;]
                [-a &lt;wl_name&gt; &lt;file or values&gt;... [&lt;wl_name&gt; &lt;file or values&gt;... ...]]
                [--rmvalues &lt;wl_name&gt; &lt;file or values&gt;... [&lt;wl_name&gt; &lt;file or values&gt;... ...]]
                [--json]

Watchlist operations. 
    



* **-l**, **--list**  
  List the ESM watchlists and exit. 
  
* **-t**, **--types**  
  List all possible watchlists types and exit. 
  
* **-e** &lt;wl_name&gt;, **--values** &lt;wl_name&gt;  
  List watchlist values and exit. Redirect STDOUT to file to export data.  
  
* **--add** &lt;wl_name&gt; &lt;wl_type&gt; &lt;wl_name&gt; &lt;wl_type&gt;  
  NotImplemented. Create a static watchlist.
  
* **--delete** &lt;wl ID&gt;, **--remove** &lt;wl ID&gt;  
  NotImplemented. Deletes a Watchlist
  
* **-a** &lt;wl_name&gt; &lt;file or values&gt;... [&lt;wl_name&gt; &lt;file or values&gt;... ...], **--addvalues** &lt;wl_name&gt; &lt;file or values&gt;... [&lt;wl_name&gt; &lt;file or values&gt;... ...]  
  NotImplemented. Add values to a static watchlist. 
  
* **--rmvalues** &lt;wl_name&gt; &lt;file or values&gt;... [&lt;wl_name&gt; &lt;file or values&gt;... ...]  
  NotImplemented. Remove watchlist values from the watchlist. 
  
* **--json**  
  NotImplemented. Prints only a JSON object to STDOUT output.  
  

<a name="options-msiem-api"></a>

# Options 'msiem api'

usage: msiem api [-h] [-m &lt;method&gt;] [-d &lt;JSON string or file&gt;]
                 [-a &lt;key&gt;=&lt;value&gt; [&lt;key&gt;=&lt;value&gt; ...]] [-l]

Quickly make API requests to any enpoints with any data. Print resposne to sdtout as JSON.   

Request v2/alarmGetTriggeredAlarms:  

    $ msiem api --method "v2/alarmGetTriggeredAlarms?triggeredTimeRange=LAST_24_HOURS&status=&pageSize=500&pageNumber=1"

    



* **-m** &lt;method&gt;, **--method** &lt;method&gt;  
  SIEM API method name or NitroSession.PARAMS keyword. Exemple: 'v2/qryGetSelectFields' or 'get_possible_fields', see 'msiem api --list' for full details .
  
* **-d** &lt;JSON string or file&gt;, **--data** &lt;JSON string or file&gt;  
  POST data, in the case of a API method name call.  See the SIEM API docs for full details.  
  
* **-a** &lt;key&gt;=&lt;value&gt; [&lt;key&gt;=&lt;value&gt; ...], **--args** &lt;key&gt;=&lt;value&gt; [&lt;key&gt;=&lt;value&gt; ...]  
  Interpolation parameters, in the case of a NitroSession.PARAMS keyword call.  See 'msiem api --list' for full details.  
  
* **-l**, **--list**  
  List all available SIEM API calls as well as all supported calls with keywords and parameter mapping. All upper cases method names signals to use the private API methods. 
  
* **-V**, **--version**  
  Show version and exit
  

<a name="authors"></a>

# Authors

**msiem**
was written by Andy Walden, Tristan Landes &lt;&lt;&lt;UNSET --author_email OPTION&gt;&gt;&gt;.

<a name="distribution"></a>

# Distribution

The latest version of msiem may be downloaded from GitHub
[](https://github.com/mfesiem/msiem)
