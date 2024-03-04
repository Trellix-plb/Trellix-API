#!/usr/bin/env python3
#
# Simple apply tag script
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

def applyTag(tag, devices, clear = False):
    
    # Authenticate to Trellix API
    session = trellixAPI.Trellix()

    # Get tag id
    tag_id = session.getTagId(tag)

    if tag_id == 0:
        logger.error('Tag {0} is not found'.format(tag))
        sys.exit()
    logger.info('{0} tag id is {1}.'.format(tag, tag_id))

    # Apply tag on each device
    for device in devices:
        
        # Get device id for each device in list
        device_id = session.getDeviceId(device)
        
        # If device has been found in ePO
        if device_id:
            logger.info('Device {0} id: {1}'.format(device, device_id))
            if clear:
                logger.debug('Clearing tag on device {0} with id {1}'.format(device, device_id))
                session.clearTag(tag_id, device_id)
            else:
                logger.debug('Applying tag on device {0} with id {1}'.format(device, device_id))
                session.applyTag(tag_id, device_id)
            
        # If device has not been found
        elif device_id == 0:
            logger.info('Device {0} not found'.format(device))

    logger.warning('ApplyTag script done.')  


def main():
    
    # Script usage
    parser = argparse.ArgumentParser(description='Apply tag on a list of device names', usage='applyTag.py [tag] [filename]')
    parser.add_argument('tag', type=str, help='Tag to apply on device. Must be already existing in ePO')
    parser.add_argument('filename', type=str, help='Filepath containing device names')
    parser.add_argument('-c', '--clear', action='store_true', help = '(Optional) Clear tag from system instead of apply')


    # Parse arguments
    args = parser.parse_args()

    # format file to device list
    try:
        with open(args.filename, 'r') as devices_file:
            devices = [line.strip() for line in devices_file.readlines()]
    except:
        logger.error('Error while opening {0} file'.format(args.filename))
        sys.exit()

    logger.info('devices list: {0}'.format(devices))

    # Log applying or clearing tag
    if args.clear:
        logger.warning('Clearing tag on {0} device(s).'.format(len(devices))) 
    else:
        logger.warning('Applying tag on {0} device(s).'.format(len(devices)))
    
    # Apply or clear tag
    applyTag(args.tag, devices, args.clear)

if __name__ == "__main__":
    main()

