#!/usr/bin/env python3
"""
Basic Trellix API library

Copyright (C) 2023 Philippe Le Bescond
 
Contact : philippe.le.bescond(at)trellix.com
"""

import requests
import json
import os
import sys
import logging
import time

### Constants ###

# Profile file path
PROFILE = '../profile'

# List of all available props used in collect properties functions
AVAILABLE_PROPS = ['id', 'name', 'parentId', 'epoGroup', 'agentGuid', 'lastUpdate', 'agentState', 'nodePath', 'agentPlatform',
                    'agentVersion','nodeCreatedDate', 'managed', 'tenantId', 'tags', 'excludedTags', 'managedState', 'computerName',
                    'domainName', 'ipAddress', 'osType', 'osVersion', 'cpuType', 'cpuSpeed', 'numOfCpu', 'totalPhysicalMemory',
                    'macAddress', 'userName', 'osPlatform','ipHostName', 'isPortable', 'installedProducts', 'assignedTags'
]

# Load configuration from profile file
try:
    with open(PROFILE, 'r') as profile_file:
        profile = json.load(profile_file)
except:
    with open('profile', 'r') as profile_file:
        profile = json.load(profile_file)

         
### Logger setup ###

# Log settings
if profile['log_level'] == 'DEBUG':
    logging.basicConfig(level=logging.DEBUG)
elif profile['log_level'] == 'INFO':
    logging.basicConfig(level=logging.INFO)
elif profile['log_level'] == 'WARN':
    logging.basicConfig(level=logging.WARN)
elif profile['log_level'] == 'ERROR':
    logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger('Trellix API')

# Log format
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

# Log file configuration
file_handler = logging.FileHandler(profile['log_path']+'TrellixAPI.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


### Trellix API Class ###

class Trellix:
    """
    Trellix API session object
    """
    
    def __init__(self):
        """
        Create a new session to Trellix API
        Result: Trellix object, contaning session information
        """
   
        # Session settings
        self.headers = profile['api_headers']
        self.url = profile['api_url']
        self.pagelimit = profile['device_page_limit']

        auth_headers = profile['auth_headers']

        auth = (profile['id'],profile['secret'])

        data = profile['auth_payload']

        self.__auth()

        # Simple query to check id settings are correct (get 1 system properties)
        simple_query = self.url + 'devices?fields=id&page%5Boffset%5D=0&page%5Blimit%5D=1'
        response = requests.get(simple_query, headers=self.headers)
        logger.debug('Tenant check result: {0}'.format(response))
        if not response.status_code == 200:
            self.__responseCheck(response)                         
        

    def __auth(self):
        """
        Authenticate to Trellix API
        """
        
        logger.debug('Trying to authenticate to Trellix API')

        # Session settings
        try:
            with open(PROFILE, 'r') as profile_file:
                profile = json.load(profile_file)
        except:
            with open('profile', 'r') as profile_file:
                profile = json.load(profile_file)


        auth_headers = profile['auth_headers']

        auth = (profile['id'],profile['secret'])

        data = profile['auth_payload']

        attempts = 5
        retries = attempts

        # Start authentication loop
        while retries:
            
            logger.debug('Attempt {0} of {1} to connect to Trellix API:'.format((attempts+1)-retries,attempts))
            # Send authentication request

            response = requests.post(profile['auth_url'], headers=auth_headers, auth=auth, data=data)

            logger.debug('Authentication request payload: {0}'.format(response.json()))

            # Stop if wrong credentials
            if not response.status_code == 200:
                logger.error('Authentication failed: {0} {1}'.format(response.json()['error_description'], response))
                sys.exit()

            # Get session token
            try:
                
                self.token = response.json()['access_token']
                
                # Rebuilding API headers
                self.headers = profile['api_headers']
                self.headers['Authorization'] += self.token
                logger.debug('Authentication successful. Status code: {0}'.format(response))
                return response
            except:
                logger.debug('Authentication failed: {0}'.format(response))
                logger.debug('Retrying in 10 seconds...')
                time.sleep(10)
            
            retries -= 1
        
        # All attempts failed
        if retries == 0:
            logger.error('Impossible to authenticate to Trellix API. Ending operation...')
            sys.exit()
    

    def __responseCheck(self, response):
        """
        Verifies if API response is correct or return an error
        Params: response, returned by the API
        Result: True if response is correct, False if response is an error
        """

        # List of known errors
        known_errors = {
            "Unauthorized": "Token has expired. Trying to refresh...",
            "Not Authorized to access the resource": "Please verify the account has appropriate scopes",
        }
        
        # Connection successful
        if response.status_code < 400:
            logger.debug('Request is successful: {0}'.format(response))
            return True
        
        # Error 401 check
        elif response.status_code == 401:
            logger.debug('Reponse content: {0}'.format(response.text))

            try:
                logger.debug('Reponse message: {0}'.format(response.json()['message']))
                message = response.json()['message']
                logger.error('Access denied: {0} {1}. {2}'.format(response, message, known_errors[message]))
                if message == 'Unauthorized':
                    self.__auth()
                    return False
            except Exception as e:
                logger.debug(str(e))
                logger.error('Access denied. Please verify your x-api-key and API url.')
            sys.exit()

        # Other responses check
        elif response.status_code == 404:
            logger.info('Device not existing. Status code: {0}'.format(response))
            return False
        elif response.status_code == 409:
            logger.info('Tag is already applied. Status code: {0}'.format(response))
            return False
        else:
            logger.info('Unknown error. Status code: {0}'.format(response))
            logger.debug(response.text)
            sys.exit()

    
    def __request(self, type, query, post = {}):
        """
        Internal request function to manage timeouts
        Params:
            type: must be 'get', 'post' or 'delete' string
            query: string containing query
        Result:
            request result
        """

        if type == 'get':
            response = requests.get(query, headers=self.headers)
            # If response code is 401, it might be a timeout, so we try to auth again
            if response.status_code == 401:
                logger.debug('Query return 401 error, it might be a timeout. Trying to refresh session...')
                self.__auth()

                logger.debug('New attempt to run query {0}:'.format(query))
                response = requests.get(query, headers=self.headers)

            return response

        elif type == 'post':
            response = requests.post(query, headers=self.headers, json=post)
            # If response code is 401, it might be a timeout, so we try to auth again
            if response.status_code == 401:
                logger.debug('Query return 401 error, it might be a timeout. Trying to refresh session...')
                self.__auth()

                logger.debug('New attempt to run query {0}:'.format(query))
                response = requests.post(query, headers=self.headers, json=post)

            return response
        
        elif type == 'delete':
            response = requests.delete(query, headers=self.headers, json=post)
            # If response code is 401, it might be a timeout, so we try to auth again
            if response.status_code == 401:
                logger.debug('Query return 401 error, it might be a timeout. Trying to refresh session...')
                self.__auth()

                logger.debug('New attempt to run query {0}:'.format(query))
                response = requests.delete(query, headers=self.headers, json=post)

            return response
        
        else:
            logger.error('Error in __request function: query is not "get" or "post". Aborting.')
            sys.exit()


    def getTagId(self, tag):
        """
        Get tag id from tag name
        Params: tag, string containing tag name
        Result: tag id, int
        """

        # Forge query
        tag_query = self.url + 'tags?filter=%7B%22EQ%22%3A%7B%22name%22%20%3A%20%22' + tag + '%22%7D%7D&fields=id,name'
        logger.debug('getTagId query: {0}'.format(tag_query))

        # Send query
        response = self.__request('get', tag_query)
        logger.debug('getTagId response: {0}'.format(response.json()))

        # Return tag id if query is successful
        if self.__responseCheck(response):
            
            # Verify tag has been found and return tag id
            try:
                tag_id = response.json()['data'][0]['id']
                logger.debug('Tag has been found in tag catalog, tag {0} id is {1}.'.format(tag, tag_id))
                return tag_id
            # Return 0 if tag is not found in ePO
            except:
                logger.info('Tag {0} is not found in Tag catalog in ePO'.format(tag))
                return 0

        # Return -1 if query failed
        else:
            logger.info('Failed to find tag {0}. Status code: {1}'.format(tag, response.status_code))
            return 0


    def getDeviceId(self, device):
        """
        From device name, get device id
        Params: device, string containing device name
        Result: device id, int
        """

        # Forge query
        device_query = self.url + 'devices?filter=%7B%22EQ%22%3A%7B%22name%22%20%3A%20%22' + device + '%22%7D%7D'
        logger.debug('getDeviceId query: {0}'.format(device_query))

        # Send query
        response = self.__request('get', device_query)
        logger.debug('getDeviceId response: {0}'.format(response.json()))

        # Return device id if query is successful
        if self.__responseCheck(response):

            # Verify if a device has been found and return device id
            try:
                device_id = response.json()['data'][0]['id']
                logger.debug('Device has been found in system tree, device {0} id is {1}.'.format(device, device_id))
                return device_id
            # Return 0 if device is not found in ePO
            except:
                logger.info('Device {0} is not found in system tree in ePO'.format(device))
                return 0

        # Return 0 if query failed
        else:
            logger.info('Failed to find device {0}. Status code: {1}'.format(device, response.status_code))
            return 0


    def getAllDevices(self):
        """
        List all devices registered in ePO and their applied tags
        Result: 
            self.deviceList, dict formatted as "device id":"device name"
            self.tagsApplied, dict formatted as "device id":"tags list"            
        """
        
        # Forge query
        offset = 0
        device_query = self.url + 'devices?fields=id,name,tags&page%5Boffset%5D=' + str(offset) + '&page%5Blimit%5D=' + str(self.pagelimit)
        

        # Dictionnaries initialisation
        self.deviceList = {}
        self.tagsApplied = {}
        
        # Query loop to browse system list
        while device_query:
            logger.debug('getAllDevices sent query: {0}'.format(device_query))
            logger.debug('Headers: {0}'.format(self.headers))
            response = self.__request('get', device_query)
            logger.debug('getAllDevices response: {0}'.format(response))
            
            if self.__responseCheck(response):
                data = response.json()

                for i in range(len(data['data'])):
                    self.deviceList[int(data['data'][i]['id'])] = data['data'][i]['attributes']['name']
                    self.tagsApplied[int(data['data'][i]['id'])] = data['data'][i]['attributes']['tags']

                try:
                    device_query = data['links']['next']
                    logger.debug('getAllDevices next query: {0}'.format(device_query))
                except:
                    device_query = ""
                    logger.debug('getAllDevices next query: none')
                
            
        
        # Dictionnary completed
        logger.info('Devices information successfully pulled from ePO')
        logger.debug('System list generated from ePO: {0}'.format(self.deviceList))
        logger.debug('List of all applied tags per device: {0}'.format(self.tagsApplied))


    def isTagApplied(self, deviceId, tag):
        """
        Verifies if tag is applied to a system
        Params:
            deviceId: int contaning device id
            tag: string containing tag name
        Result: Boolean
        """

        return tag in list(self.tagsApplied[deviceId].split(", "))
            

    def applyTag(self, tag_id, device_id):
        """
        Apply tag on a system or a list of systems
        Params:
            tag_id: int of tag to apply
            device_id: can be a int with single device id, a string with single device name
            or a list of systems formatted in JSON like: {"type": "devices", "id": device id}
        Result: Boolean if tag has been applied
        """
        
        sys_len = 1

        # Forge query
        apply_tag_query = self.url + 'tags/' + tag_id + '/relationships/devices'

        # Forge payload for the post query
        post = {
            "data": [
                {
                    "type": "devices",
                    "id": 0
                }
            ]
        }
        
        if isinstance(device_id, list):
            post['data'] = device_id
            logger.info('Applying tag using system list')
            sys_len = len(device_id)
        elif isinstance(device_id, int):
            post['data'][0]['id'] = device_id
            logger.info('Applying tag using system id')
        elif isinstance(device_id, str):
            post['data'][0]['id'] = int(device_id)
            logger.info('Applying tag using system id (string)')
        
        # If no systems are targeted
        if sys_len == 0:
            logger.info('Tag is already applied on all systems.')
            return True

        logger.debug('ApplyTag query: {0}'.format(apply_tag_query))
        logger.debug('ApplyTag payload: {0}'.format(post))

        # Send post query
        response = self.__request('post', apply_tag_query, post)
        logger.debug('ApplyTag response: {0}'.format(response))
        
        if response.status_code == 204:
            logger.info('Tag successfully applied on {0} systems. Status code {1}'.format(sys_len, response))
            return True

        # return response check result if failed
        return self.__responseCheck(response)
   
    
    def clearTag(self, tag_id, device_id):
        """
        Clear tag on a system or a list of systems
        Params:
            tag_id: int of tag to clear
            device_id: can be a int with single device id, a string with single device name
            or a list of systems formatted in JSON like: {"type": "devices", "id": device id}
        Result: Boolean if tag has been cleared
        """

        sys_len = 1

        # Forge query
        clear_tag_query = self.url + 'tags/' + tag_id + '/relationships/devices'

        # Forge payload for the delete query
        delete = {
            "data": [
                {
                    "type": "devices",
                    "id": 0
                }
            ]
        }
        
        if isinstance(device_id, list):
            delete['data'] = device_id
            logger.info('Clearing tag using system list')
            sys_len = len(device_id)
        elif isinstance(device_id, int):
            delete['data'][0]['id'] = device_id
            logger.info('Clearing tag using system id')
        elif isinstance(device_id, str):
            delete['data'][0]['id'] = int(device_id)
            logger.info('Clearing tag using system id (string)')
        
        # If no systems are targeted
        if sys_len == 0:
            logger.info('Tag is already cleared on all systems.')
            return True

        logger.debug('ClearTag query: {0}'.format(clear_tag_query))
        logger.debug('ClearTag payload: {0}'.format(delete))

        # Send delete query
        response = response = self.__request('delete', clear_tag_query, delete)
        logger.debug('ClearTag response: {0}'.format(response))
        
        if response.status_code == 204:
            logger.info('Tag successfully cleared on {0} systems. Status code {1}'.format(sys_len, response))
            return True

        # return response check result if failed
        return self.__responseCheck(response)
    
    def collectProperties(self, device_id, props = AVAILABLE_PROPS):
        """
        Get device properties
        Params:
            device_id: int
            props: list of all device properties to gather
        Result:
            json containing device information
        """

        # Filtering props
        logger.info('Checking if properties exists...')
        filtered_props = list(filter(lambda x: x in props, AVAILABLE_PROPS))
        if len(filtered_props) == 0:
            logger.error('Properties in argument are not available')
            sys.exit()
        logger.info('List of properties that will be collected: {0}'.format(filtered_props))

        # Throwing unavailable props
        wrong_props = []
        for prop in props:
            if prop not in AVAILABLE_PROPS:
                wrong_props.append(prop)

        logger.info('List of properties that are not existing and will not be collected: {0}'.format(wrong_props))

        # Forge query
        props_query = self.url + 'devices/' + device_id + '?fields=' + ','.join(filtered_props)
        logger.debug('collectProperties query: {0}'.format(props_query))

        # Send query
        response = self.__request('get', props_query)
        logger.debug('collectProperties response: {0}'.format(response.json()))

        # Return device properties query is successful
        if self.__responseCheck(response):
            return response.json()['data']['attributes']

        # Return 0 if query failed
        else:
            logger.info('Impossible to query properties for device id {0}. Status code: {1}'.format(device_id, response.status_code))
            return 0
        

    def collectAllProperties(self, props = AVAILABLE_PROPS):
        """
        Get all devices properties
        Params:
            props: list of all device properties to gather. If not specified, collect all properties
        Result:
            List of json data containing devices information
        """
        
        # Create new list to store properties
        all_props = []

        # Filtering props
        logger.info('Checking if properties exists...')
        filtered_props = list(filter(lambda x: x in props, AVAILABLE_PROPS))
        if len(filtered_props) == 0:
            logger.error('Properties in argument are not available')
            sys.exit()
        logger.info('List of properties that will be collected: {0}'.format(filtered_props))

        # Throwing unavailable props
        wrong_props = []
        for prop in props:
            if prop not in AVAILABLE_PROPS:
                wrong_props.append(prop)

        logger.info('List of properties that are not existing and will not be collected: {0}'.format(wrong_props))

        # Forge first query
        offset = 0
        props_query = self.url + 'devices?fields=' + ','.join(filtered_props) + '&page%5Boffset%5D=' + str(offset) + '&page%5Blimit%5D=' + str(self.pagelimit)
        logger.debug('collectProperties query: {0}'.format(props_query))

        # Query loop to browse system list
        while props_query:
            logger.debug('collectAllProperties sent query: {0}'.format(props_query))
            logger.debug('Headers: {0}'.format(self.headers))
            response = self.__request('get', props_query)
            logger.debug('collectAllProperties response: {0}'.format(response))
            
            if self.__responseCheck(response):
                data = response.json()
                logger.debug('Data collected: {0}'.format(data))

                for i in range(len(data['data'])):
                    all_props.append(data['data'][i]['attributes'])

                try:
                    props_query = data['links']['next']
                    logger.debug('getAllDevices next query: {0}'.format(props_query))
                except:
                    props_query = ""
                    logger.debug('getAllDevices next query: none')

        return all_props
      