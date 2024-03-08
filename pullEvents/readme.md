# Pull Trellix threat events

## Script usage

```python pullThreatEvents.py -f <logfile> -s <syslog_server> -p <syslog_port>```

**-f logfile** is the file where to write threat events  
**-s syslog_server** is the address of syslog server where to send threat events  
**-p syslog_port** is the port of syslog server  

At least a log file or a syslog server must be specified. Both can be used at the same time.

**Examples:**  
```python pullThreatEvents.py -f /tmp/Trellix/threatevents.log```  
```python pullThreatEvents.py -s 127.0.0.1 -p 514```

## Log format

Log uses raw json data pulled from epo.  

**Sample:**  
```{'timestamp': '2024-03-07T13:09:06.118Z', 'autoguid': '8a7fc47e-d76c-417a-bc0f-2df602f406b5', 'detectedutc': '1709816932000', 'receivedutc': '1709816946118', 'agentguid': '75175a32-5a5a-4ee3-a906-012345678910', 'analyzer': 'ENDP_AM_1070', 'analyzername': 'Trellix Endpoint Security', 'analyzerversion': '10.7.0.5786', 'analyzerhostname': 'HOSTNAME', 'analyzeripv4': '1.1.1.1', 'analyzeripv6': '/0:0:0:0:0:0:0:0', 'analyzermac': '0123456789ab', 'analyzerdatversion': '5457.0', 'analyzerengineversion': '6700.10107', 'analyzerdetectionmethod': 'On-Access Scan', 'sourcehostname': None, 'sourceipv4': '1.1.1.1', 'sourceipv6': '/0:0:0:0:0:0:0:0', 'sourcemac': None, 'sourceusername': None, 'sourceprocessname': 'C:\\Windows\\System32\\cmd.exe', 'sourceurl': None, 'targethostname': None, 'targetipv4': '1.1.1.1', 'targetipv6': '/0:0:0:0:0:0:0:0', 'targetmac': None, 'targetusername': 'HOSTNAME\\Administrator', 'targetport': None, 'targetprotocol': None, 'targetprocessname': None, 'targetfilename': 'C:\\Users\\Administrator\\Documents\\malware.txt', 'threatcategory': 'av.detect', 'threateventid': 1278, 'threatseverity': '2', 'threatname': 'Installation Check', 'threattype': 'test', 'threatactiontaken': 'IDS_ALERT_ACT_TAK_DEL', 'threathandled': True, 'nodepath': '1\\1234569\\1234568\\1234567', 'targethash': '10c0d81225bac79e7c09a1278cd8f0e1', 'sourceprocesshash': None, 'sourceprocesssigned': None, 'sourceprocesssigner': None, 'sourcefilepath': None}```

## Settings

By default, each query will try to pull up to 1000 threat events. It can be changed in profile file, in **events_page_limit** but you can only reduce it because 1000 events is the maximum allowed per query.  
**events_cursor** contain information from the last event pulled. It is used by the API as a cursor to know which events are not pulled yet. If empty, it means that all events in ePO need to be pulled, so if you need to pull all threat events again you can just remove the value. Notice that API retention for events is 3 days.  
By default, this script pull events every 600 seconds, generating at least 144 query each day (it can be more if there are more than 1000 events to pull). It can be changed by updating *PULL_INTERVAL* constant. If you set a lower pull interval to have more reactivity, you can also comment the session.auth() line, which is used to refresh auth token that expires after 10 minutes. Remember you are limited to execute 2500 queries per day per API license.  
Syslog forwarding uses UDP
