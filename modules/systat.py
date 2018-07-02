# -*- coding: utf-8 -*-
'''
Module to get system metrics and informations to log them into a elastic/logstash instance 
'''
from __future__ import absolute_import
import salt
import commands
import os
import subprocess
import logging
import salt.utils

# Change salt.utils in future release of salt to the following
#import salt.utils.platform

log = logging.getLogger(__name__)

__virtualname__ = 'systat'

def __virtual__():
    '''
    Only works on POSIX-like systems
    '''
    #if salt.utils.platform.is_windows():
    if salt.utils.is_windows():
        return False, 'This module doesn\'t work on Windows.'

    return __virtualname__

def get_systemtyp():
    '''
    Returns True if the patrol_nostart flag exists and False if not.
    ('/var/patrol/patrol_nostart').

       .. code-block:: bash

    salt '*' patrol.chk_nostart
    '''
    result = __grains__['cpuarch']

    return bool(result)

def enable():
    '''
    Enables Patrol on this Server by removing the patrol_nostart Flag.
    It also starts and enables the PatrolAgent service.

       .. code-block:: bash

    salt '*' patrol.chk_nostart
    '''
    result_set_Flag = True
    result_service_enabled = True
    result_service_started = True

    if __salt__['file.file_exists']('/var/patrol/patrol_nostart'):
        result_set_Flag = __salt__['file.remove']('/var/patrol/patrol_nostart')

    if not __salt__['service.enabled']('PatrolAgent'):
        result_service_enabled = __salt__['service.enable']('PatrolAgent')

    if not __salt__['service.status']('PatrolAgent'):
        result_service_started = result = __salt__['service.start']('PatrolAgent')

    if result_set_Flag and result_service_enabled and result_service_started:
        return bool(True)
    else:
        return bool(False)
