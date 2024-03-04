# Applying and clearing tags

## Script usage

```python applyTag.py [-c] <tag> <systemlist> ```


**-c** is the optional switch to clear tag instead of apply  
**tag** is the tag to apply on devices. It must be already existing in ePO.  
**systemlist** is the file containing the list of devices that will apply tag. Each system per line. Example:  
```
host1
host2
host3
host4
host5
```
applyTagOnMany.py has the same usage.

**Examples:**  
To apply *api* tag on systemlist containing few systems:  
```python applyTag.py api systemlist```  
To clear tag *api* on systemlist containing many systems:  
```python -c applyTagOnMany.py api systemlist```

### Difference between applyTag and applyTagOnMany

The difference between applyTag.py and applyTagOnMany.py is their sending requests:
* applyTag.py will send one request per system in the file to gather information, while applyTagOnMany.py will always gather information from all systems (using device_page_limit setting)
* applyTag.py will send one request per system to apply tag, when applyTagOnMany.py will send only one request to apply tags on all specified systems

So it's more efficient to use applyTag.py if you want to applys tag on few systems: it will use 2 api queries per system.  
If you want to apply tags on many systems, applyTagOnMany.py will use: (*total_number_of_systems*)/*device_page_limit* + _1_ api queries.

Example: You have 10k systems in ePO and want to apply tag on 5 systems:  
* applyTag.py will consume 10 api queries
* applyTagOnMany.py will consume 501 api queries (with default device_page_limit * setting)

Example: You have 10k systems in ePO and want to apply tag on 2k systems:  
* applyTag.py will consume 4000 api queries
* applyTagOnMany.py will consume 501 api queries (with default device_page_limit setting)
