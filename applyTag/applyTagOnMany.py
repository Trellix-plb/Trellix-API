#!/usr/bin/env python3
#
# Massively apply tag script
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

def applyTagOnMany(tag, devices, clear = False):
    # Authenticate to Trellix API
    session = trellixAPI.Trellix()

    # Get tag id
    tag_id = session.getTagId(tag)

    if tag_id == 0:
        logger.error('Tag {0} is not found'.format(tag))
        sys.exit()
    logger.info('{0} tag id is {1}.'.format(tag, tag_id))


    # Get all devices in ePO
    session.getAllDevices()

    # Filter device id in args
    device_id_list = []

    for device in devices:
        device_id = [i for i,j in session.deviceList.items() if j == device]
        device_id_list.extend(device_id)

    logger.info('Filtered device id list: {0}'.format(device_id_list))

    # Creating json formatted devices list
    device_list = []

    # Filter devices where operate tag applying or clearing
    for id in device_id_list:
        # XNOR with isTagApplied and clear
        if not(session.isTagApplied(id, tag) ^ clear):
            device_list.append(id)  
        else:
            if clear:
                logger.info('Tag is not applied on device {0}'.format(id)) 
            else:
                logger.info('Tag already applied on device {0}'.format(id)) 

    logger.info('devices list where applying or clearing tag: {0}'.format(device_list))

    # Clearing or appling tag
    if clear:
        logger.debug('JSON system list where to clear tag {0}'.format(device_list))
        logger.info('Starting clear tag on {0} device(s).'.format(len(device_list)))
        session.clearTag(tag_id, device_list)
    else:
        logger.debug('JSON system list where to apply tag {0}'.format(device_list))
        logger.info('Starting apply tag on {0} device(s).'.format(len(device_list)))
        session.applyTag(tag_id, device_list)    

    logger.warning('ApplyTagOnMany script done.') 

def main():

    # Script usage
    parser = argparse.ArgumentParser(description='Apply tag on a large list of device names', usage='applyTag.py [tag] [filename]')
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

    # Log applying or clearing tag
    if args.clear:
        logger.warning('Clearing tag on {0} device(s).'.format(len(devices))) 
    else:
        logger.warning('Applying tag on {0} device(s).'.format(len(devices)))

    # Run applyTagOnMany
    applyTagOnMany(args.tag, devices, args.clear)


if __name__ == "__main__":
    main()

