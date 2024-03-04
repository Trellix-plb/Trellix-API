#!/usr/bin/env python3
#
# Collect systems properties script
#
# Copyright (C) 2023 Philippe Le Bescond
#
# Contact : philippe.le.bescond(at)trellix.com

import requests
import json
import argparse
import os
import sys

# Setting path for module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lib.trellixAPI as trellixAPI
from lib.trellixAPI import logger

def systemsProperties(props, devices = []):

    # Authenticate to Trellix API
    session = trellixAPI.Trellix()

    # Initiate device props list
    data = []

    # Collecting properties of all devices if no specific devices
    if len(devices) == 0:
        
        # Collecting all props if all is specified
        if 'all' in props:
            return session.collectAllProperties()
        # Else collect specfified props
        else:
            return session.collectAllProperties(props)

    else:
        logger.warning('Starting collecting properties from {0} device(s)...'.format(len(devices)))
        logger.info('Devices list: {0}'.format(devices))

        # Collecting properties from each device
        for device in devices:
            
            # Get device id for each device in list
            device_id = session.getDeviceId(device)
            
            # If device has been found in ePO
            if device_id:
                logger.info('Device {0} id: {1}'.format(device, device_id))

                # Collect all props if all is specified
                if 'all' in props:
                    data.append(session.collectProperties(device_id))
                # Else collect specfified props
                else:
                    data.append(session.collectProperties(device_id, props))

            # If device has not been found
            elif device_id == 0:
                logger.info('Device {0} not found'.format(device))

        return data


def __csvParser(data):

    # Parse json list to csv
    parsed_data = ''
    
    # Adding csv columns in first line
    parsed_data = ','.join(list(data[0].keys()))
    
    # Parsing each device data
    for device in data:

        device_data = []

        for key in device:
            # Replacing commas by semicolon in properties (espcially tags) to avoid issue in CSV
            device_data.append(str(device[key]).replace(',',';'))

        device_data = ','.join(device_data)
        parsed_data = '\n'.join([parsed_data, device_data])

    return parsed_data


def main():

    # Script usage
    parser = argparse.ArgumentParser(description = 'Get system properties of list of device names', usage = 'systemProperties <properties> <filename> -o [csv|json]')
    parser.add_argument(
        'properties', type = str, help = 'List of properties to collect. Must be a list of properties separated by commas, from those properties:\n'
        'id, name, parentId, epoGroup, agentGuid, lastUpdate, agentState, nodePath, agentPlatform, agentVersion,'
        'nodeCreatedDate, managed, tenantId, tags, excludedTags, managedState, computerName, domainName, ipAddress,'
        'osType, osVersion, cpuType, cpuSpeed, numOfCpu, totalPhysicalMemory, macAddress, userName, osPlatform,'
        'ipHostName, isPortable, installedProducts, assignedTags'
    )
    parser.add_argument('filename', type=str, help = 'Filepath containing device names')
    parser.add_argument('-o', '--output', nargs='?', default = 'json', type=str, help = 'Output format, can be csv or json. Output is json by default')

    # Parse arguments
    args = parser.parse_args()    

    # Creating the list of properties to collect
    props = args.properties.split(',')

    # Checking if there is a device list
    if args.filename == None or args.filename.casefold() == 'all' :
        devices = []

    # format device list
    else:
        try:
            with open(args.filename, 'r') as devices_file:
                devices = [line.strip() for line in devices_file.readlines()]
        except:
            logger.error('Error while opening {0} file'.format(args.filename))
            sys.exit()

    # Collect system properties
    data = systemsProperties(props, devices)

    # Write data
    if args.output.casefold() == 'csv':
        parsed_data = __csvParser(data)
        print(parsed_data)

    else:
        parsed_data = {}
        parsed_data['data'] = data
        print(json.dumps(parsed_data, indent = 4))


if __name__ == "__main__":
    
    main()
    logger.warning('systemProperties script done.')
    
