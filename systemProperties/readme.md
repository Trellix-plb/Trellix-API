# Collecting system properties and installed products

## systemProperties script usage

```python systemProperties.py <proplist> <systemlist> [-o csv|json] > <destfile>```

**proplist** is the list of system properties to be collected (see below available properties), seperated by commas without any space. Can be 'all' to collect all properties. Properties are case sensitive.
**systemlist** is the file containing the list of devices to collect properties. Can be 'all' to collect properties of all systems.  
**[-o csv|json]** is the optional output format. Default is json.  
**destfile** is the file where redirect the output.

**Examples:**  
Get hostname, last communication and tags for systems in systemlist:  
```python systemProperties.py name,lastUpdate,tags systemlist -o csv > systemproperties.csv```  
Get all properties of all systems in ePO:  
```python systemProperties.py all all > allprops.json```

**List of all available properties:**  
```
'id', 'name', 'parentId', 'epoGroup', 'agentGuid', 'lastUpdate', 'agentState', 'nodePath', 'agentPlatform', 'agentVersion','nodeCreatedDate', 'managed', 'tenantId', 'tags', 'excludedTags', 'managedState', 'computerName', 'domainName', 'ipAddress', 'osType', 'osVersion', 'cpuType', 'cpuSpeed', 'numOfCpu', 'totalPhysicalMemory', 'macAddress', 'userName', 'osPlatform','ipHostName', 'isPortable', 'installedProducts', 'assignedTags'
```

## installedProducts script usage

```python systemProducts.py <systemlist> [-o csv|json] > <destfile>```

**systemlist** is the file containing the list of devices to collect Trellix products versions.  
**[-o csv|json]** is the optional output format. Default is json.  
**destfile** is the file where redirect the output.  

**Example:**  
Get installed products for systems in systemlist and write the in a csv file:  
```python systemProperties.py name,lastUpdate,tags systemlist -o csv > installedproducts.csv``` 