# Trellix API library and scripts

Python scripts for Trellix API done by Philippe Le Bescond.  
Contact: philippe.le.bescond(at)trellix.com

## Disclaimer

>**This is not an official Trellix ressource. All scripts have been tested in a limited environment. Please do your own tests before any important operation in your tenant. I decline any reponsability if you have any issue with those scripts.**

## Description

This script can apply tags in ePO SaaS using a system list in a file. It works only on ePO SaaS, not on ePO on premise. A Trellix API licence is also required to access ePO SaaS API, you can run 2500 API queries per day, per API licence you own.

## Configuration

You may need to install these dependancies:  
```requests```  
To resolve these dependancies you can use: pip install *package*

First you must configure **profile** file where are stored your tenant details. 3 settings must be provided:
* **id** : is API client login
* **secret** : is API client password
* **x-api-key** : is tenant API key

Both information can be retrieved from [Trellix developer portal](https://developer.manage.trellix.com/mvision/selfservice/access_manag).
API client credential must be generated; this operation can take few days.

Few others settings can be customized:
* **log_level**: By default set to WARN, it can be set to INFO for more details, DEBUG for troubleshooting, or ERROR to display only errors
* **log_path**: If empty, the log file will be written in working directory. You can force a specific folder here
* **device_page_limit**: Is the number of systems gathered by each api request from applyTagOnMany.py script. This value should be increased to reduce the number of queries sent to gather information from all systems in ePO.

## Scripts list

* [Applying / clearing tag scripts](applyTag)
* [Collecting system properties script](systemProperties)
