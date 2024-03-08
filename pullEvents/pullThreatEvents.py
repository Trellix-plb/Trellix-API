#!/usr/bin/env python3
#
# Simple pull threat events script
#
# Copyright (C) 2023 Philippe Le Bescond
#
# Contact : philippe.le.bescond(at)trellix.com

import json
import argparse
import os
import sys
import logging
from logging.handlers import SysLogHandler
import time

# Setting path for module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lib.trellixAPI as trellixAPI
from lib.trellixAPI import logger

### Constants ###

# Pull interval in seconds
PULL_INTERVAL = 600
LOGGER_NAME = 'Trellix threat event'

### Functions ###

def main():
    
    # Script usage
    parser = argparse.ArgumentParser(description='Pull threat events from Trellix ePO SaaS',
                                     usage='pullThreatEvents.py [-f file] [-s syslog_server] [-p syslog_port]')
    parser.add_argument('-f', '--file', type=str, help='File where to write threat events')
    parser.add_argument('-s', '--server', type=str, help='Syslog server address where to send threat events')
    parser.add_argument('-p', '--port', type=int, help='Syslog server address where to send threat events')

    # Parse arguments
    args = parser.parse_args()

    # Checking arguments
    file = args.file != None
    syslog = args.server != None
    port = args.port != None

    # Verifying at least file or server is specified
    if not(file or syslog):
        logger.error('Failed to execute PullThreatEvent, at least a file (-f) or a syslog server (-s) must be specified')
        sys.exit()
    
    # Verifying syslog adress and port are specified
    if syslog ^ port:
        logger.error('Failed to execute PullThreatEvent, Both syslog server (-s) and syslog port (-p) must be specified')
        sys.exit()

    # Open Trellix API session
    session = trellixAPI.Trellix()

    # Configure file logger
    if args.file != None:
        logger.info('Setting up log file to write threat events in {0}'.format(args.file))
        file_logger = logging.getLogger(LOGGER_NAME)
        file_log_handler = logging.FileHandler(args.file)
        file_logger.addHandler(file_log_handler)
        file_logger.setLevel(level=logging.INFO)

    # Configue syslog logger
    if args.server != None:
        logger.info('Setting up Syslog server to send threat events to {0}:{1}'.format(args.server, args.port))
        syslog_logger = logging.getLogger(LOGGER_NAME)
        syslog_log_handler = SysLogHandler(address=(args.server, args.port))
        syslog_logger.addHandler(syslog_log_handler)
        syslog_logger.setLevel(level=logging.INFO)

    logger.warning('Starting collecting new threat events...')

    # Pull event loop
    while True:
        # Reauth each pull to refresh token (useful if PULL_INTERVAL >= 600)
        session.auth()

        # Pull threat events events
        logger.info('Pulling new threat events...')
        event_list = session.pullThreatEvents()
        logger.debug('List of pulled events:')
        logger.debug(event_list)

        # Write each event in correct loggers
        if file and syslog:
            for event in event_list:
                print(type(event))
                file_logger.info(event)
                syslog_logger.info(event)

        elif file:
            for event in event_list:
                file_logger.info(event)

        elif syslog:
            for event in event_list:
                syslog_logger.info('New event:')
                syslog_logger.info(event)

        # Wait next pull
        logger.debug('Waiting {0} seconds until next pull'.format(PULL_INTERVAL))
        time.sleep(PULL_INTERVAL)
        

if __name__ == "__main__":
    main()

