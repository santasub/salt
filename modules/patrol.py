# -*- coding: utf-8 -*-
'''
Module to manage the bmc patrol operations management
use it to "set" & "end" the Maintenance Mode and more.
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

__virtualname__ = 'patrol'

def __virtual__():
    '''
    Only works on POSIX-like systems
    '''
    #if salt.utils.platform.is_windows():
    if salt.utils.is_windows():
        return False, 'This module doesn\'t work on Windows.'

    if not os.path.isfile('/var/patrol/scripts/maintenance'):
        return False, 'Patrol is not Installed.'

    return __virtualname__

def chk_nostart():
    '''
    Returns True if the patrol_nostart flag exists and False if not.
    ('/var/patrol/patrol_nostart').

       .. code-block:: bash

    salt '*' patrol.chk_nostart
    '''
    result = __salt__['file.file_exists']('/var/patrol/patrol_nostart')

    return bool(result)

def enable():
    '''
    Removes the patrol_nostart flag and starts the Patrol Service and
    enables it from starting on boottime.
    Returns True if succesfull and False if not.

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

def disable():
    '''
    Creates the patrol_nostart flag and stops the Patrol Service and
    disables it from starting on boottime.
    Returns True if succesfull and False if not.

       .. code-block:: bash

    salt '*' patrol.chk_nostartsal
    '''
    result_rm_Flag = True
    result_service_disabled = True
    result_service_stoped = True

    if not __salt__['file.file_exists']('/var/patrol/patrol_nostart'):
       result_rm_Flag = __salt__['file.write']('/var/patrol/patrol_nostart')

    if __salt__['service.enabled']('PatrolAgent'):
        result_service_disabled = __salt__['service.disable']('PatrolAgent')

    if __salt__['service.status']('PatrolAgent'):
        result_service_stoped = __salt__['service.stop']('PatrolAgent')

    if result_rm_Flag and result_service_disabled and result_service_stoped:
        return bool(True)
    else:
        return bool(False)

def chk_maint():
    '''
    Check if the minion is in Maintenance Mode.
    Returns True if the System is in Maintenance
    and False if not.

        .. code-block:: bash

    salt '*' patrol.chk_maint
    '''
    cmd='/var/patrol/scripts/maintenance --sstatus >/dev/null 2>&1'

    result = __salt__['cmd.run'](cmd, output_loglevel='quiet', python_shell=False)

    return bool(result)

def get_maint_info():
    '''
    Get information about the Maintenance in progress.
    returns the information string if Maintenance is set
    and 'No Maintenance set' if not.

        .. code-block:: bash

    salt '*' patrol.get_maint_info
    '''
    nostart = ''

    if chk_nostart():
        nostart = ' ### This Server has the patrol_nostart flag.'

    status = chk_maint()

    if status:
        cmd='/var/patrol/scripts/maintenance -status'

        result = __salt__['cmd.run'](cmd, output_loglevel='quiet', python_shell=False)

        #remove empty lines from string
        result = os.linesep.join([s for s in result.splitlines() if s])
        return result + nostart
    else:
        return 'No Maintenance set!' + nostart

def set_maint(duration, msg='', user='', specialID='', sleep=False):
    '''
    Set Maintenance on a Minion for a given time.
    Minimum parameter is duration the rest is Optional.
    duration: 1h/1min
    specialID: pre defined id to set a special Maintenance
    user: user to set maintenance with
    msg: Message to set
    sleep: Set to True if you want to wait for 60 Sec till maintenance is set.

        .. code-block:: bash

    salt '*' patrol.set_maint duration=1h specialID='/this/is/just/a/sample' user=patrol msg='Message_to_set' sleep=True debug=True
    '''
    cmd1=''
    cmd2=''
    cmd3=''
    cmd4=''

    if duration:
        if specialID:
            cmd1='-acv ' + specialID + ' '

        if user:
            cmd2='-user ' + user + ' '

        if msg:
            cmd3='-msg ' + msg + ' '

        if sleep:
            cmd4='--sleep'

        cmd='/var/patrol/scripts/maintenance -t ' + duration + ' ' + cmd1 + cmd2 + cmd3 + cmd4

        result = __salt__['cmd.run'](cmd, output_loglevel='quiet', python_shell=False)

        return bool(result)

def end_maint(specialID='', sleep=False):
    '''
    End Maintenance on a Minion.
    The param specialID is Optional. Set sleep=True to wait for 60 Sec

        .. code-block:: bash

    salt '*' patrol.end_maint specialID='/this/is/just/a/sample'
    '''
    cmd1=''
    cmd2=''

    if not chk_maint():
        return False, 'The System is not in Maintenance'

    if specialID:
        cmd1='-acv ' + specialID + ' '

    if sleep:
        cmd2='--sleep'

    cmd='/var/patrol/scripts/maintenance -t END ' + cmd1 + cmd2

    result = __salt__['cmd.run'](cmd, output_loglevel='quiet', python_shell=False)

    return bool(result)