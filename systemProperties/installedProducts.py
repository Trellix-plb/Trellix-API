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
import bisect

# Setting path for module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lib.trellixAPI as trellixAPI
from lib.trellixAPI import logger

def systemsProducts(devices):

    # Authenticate to Trellix API
    session = trellixAPI.Trellix()

    # Initiate device props list
    data = []

    logger.warning('Starting collecting products from {0} device(s)...'.format(len(devices)))
    logger.info('Devices list: {0}'.format(devices))

    # Collecting properties from each device
    for device in devices:
        
        # Get device id for each device in list
        device_id = session.getDeviceId(device)
        
        # If device has been found in ePO
        if device_id:
            logger.info('Device {0} id: {1}'.format(device, device_id))
            # Format device data
            device_data = {"name": device,
                           "id": device_id}

            # Collect products list for device
            product_list = session.getInstalledProducts(device_id)
            product_list_filtered = [product['attributes'] for product in product_list]

            # Add it to products list
            device_data["products"] = product_list_filtered
            data.append(device_data)

        # If device has not been found
        elif device_id == 0:
            logger.info('Device {0} not found'.format(device))

    return data


def __csvParser(data):

    # Parse json list to csv
    parsed_data = ''
    
    # Checking if data available
    if len(data) == 0:
        return 'No data found'
    
    product_list = []
    
    # Creating product list
    for device in data:
        for product in device['products']:
            if product['productFamilyName'] not in product_list:
                bisect.insort(product_list, product['productFamilyName'])
    logger.debug('List of all products found for CSV: {0}'.format(product_list))

    # Add System name property and add product list to CSV 
    product_list.insert(0, 'System Name')
    parsed_data = ','.join(product_list)

    # Collecting product versions from systems
    device_products_list = []
    for device in data:
        device_products = {key: '' for key in product_list}
        device_products['System Name'] = device['name']
        for product in device['products']:
            device_products[product['productFamilyName']] = product['productVersion']
        device_products = list(device_products.values())
        device_products_list.append(device_products)
        logger.debug('list of product versions collected from system {0}: {1}'.format(device, device_products_list))

        # Formating in CSV
        device_data = ','.join(device_products)
        parsed_data = '\n'.join([parsed_data, device_data])

    return parsed_data


def main():

    # Script usage
    parser = argparse.ArgumentParser(description = 'Get installed products from a systems list', usage = 'systemProperties <filename> -o [csv|json]')
    parser.add_argument('filename', type=str, help = 'Filepath containing device names')
    parser.add_argument('-o', '--output', nargs='?', default = 'json', type=str, help = 'Output format, can be csv or json. Output is json by default')

    # Parse arguments
    args = parser.parse_args()    

    # Checking if there is a device list
    if args.filename == None :
        logger.error('A file containing a system list is required. Aborting.')
        sys.exit()

    # format device list
    else:
        try:
            with open(args.filename, 'r') as devices_file:
                devices = [line.strip() for line in devices_file.readlines()]
        except:
            logger.error('Error while opening {0} file'.format(args.filename))
            sys.exit()

    # Collect system products
    data = systemsProducts(devices)

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
    
