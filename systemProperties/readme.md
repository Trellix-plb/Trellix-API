# Collecting system properties

## Script usage

```python systemProperties.py <proplist> <systemlist> [-o csv|json] > <destfile>```

**proplist** is the list of system properties to be collected (see below available properties), seperated by commas. Can be 'all' to collect all properties.  
**systemlist** is the file containing the list of devices to collect properties. Can be 'all' to collect properties of all systems.  
**[-o csv|json]** is the optional output format. Default is json.  
**destfile** is the file where redirect the output.

**Examples:**  
Get hostname, last communication and tags for systems in systemlist:  
```python systemProperties.py name,lastUpdate,tags systemlist csv > systemproperties.csv```  
Get all properties of all systems in ePO:  
```python systemProperties.py all all > allprops.json```

**List of all available properties:**  
```
'id', 'name', 'parentId', 'epoGroup', 'agentGuid', 'lastUpdate', 'agentState', 'nodePath', 'agentPlatform', 'agentVersion','nodeCreatedDate', 'managed', 'tenantId', 'tags', 'excludedTags', 'managedState', 'computerName', 'domainName', 'ipAddress', 'osType', 'osVersion', 'cpuType', 'cpuSpeed', 'numOfCpu', 'totalPhysicalMemory', 'macAddress', 'userName', 'osPlatform','ipHostName', 'isPortable', 'installedProducts', 'assignedTags'
```