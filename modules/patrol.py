# -*- coding: utf-8 -*-
import salt
import commands
import os
import subprocess
import salt.utils
# Change salt.utils in future release of salt to the following
#import salt.utils.platform
'''
Module to amange the bmc patrol operations management
use it to "set" & "end" the Maintenance Mode and more.
'''

def __virtual__():
    '''
    Only works on POSIX-like systems
    '''
    #if salt.utils.platform.is_windows():
    if salt.utils.is_windows():
        return False, 'This module doesn\'t work on Windows.'

    if not __salt__['pkg.version']('COOPPatrolAgent'):
        return False, 'Patrol is not Installed.'

    '''
    if os.path.isfile('/var/patrol/patrol_nostart'):
        return False, 'This Server has the patrol_nostart flag.'
    if not os.path.isfile('/var/patrol/scripts/maintenance'):
        return False, 'Can not find the Patrol maintenance script.'
    '''
    return True

def chk_nostart():
    '''
    Returns True if the patrol_nostart flag exists and False if not.
    ('/var/patrol/patrol_nostart').

       .. code-block:: bash

    salt '*' patrol.chk_nostart
    '''

    if os.path.isfile('/var/patrol/patrol_nostart'):
        return True
    else:
        return False

def chk_maint():
    '''
    Check if the minion is in Maintenance Mode.
    Returns True if the System is in Maintenance
    and False if not.

        .. code-block:: bash

    salt '*' patrol.chk_maint
    '''

    cmd='/var/patrol/scripts/maintenance --sstatus >/dev/null 2>&1'

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        RC = exc.returncode
        OP = exc.output

        return True
    else:
        return False

def get_maint_info():
    '''
    Get information about the Maintenance in progress.
    returns the information string if Maintenance is set
    and 'No Maintenance set' if not.

        .. code-block:: bash

    salt '*' patrol.get_maint_info
    '''
    nostart = ''

    if chk_nostart:
        nostart = ' This Server has the patrol_nostart flag.'

    status = chk_maint()

    if status:
        cmd='/var/patrol/scripts/maintenance -status'

        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            RC = exc.returncode
            OP = exc.output

            return False, 'The command could not be executed'

        #remove empty lines from string
        output = os.linesep.join([s for s in output.splitlines() if s])
        return output + ' ### ' + nostart
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
        try:
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        except subprocess.CalledProcessError as exc:
                RC = exc.returncode
                OP = exc.output

                return False
        else:
                return True

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

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        RC = exc.returncode
        OP = exc.output

        return False
    else:
        return True