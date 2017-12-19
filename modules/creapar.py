# -*- coding: utf-8 -*-
from __future__ import absolute_import
import salt
import commands
import os
import subprocess
import salt.utils
# Change salt.utils in future release of salt to the following
#import salt.utils.path
#import salt.utils.platform

'''
Module to fix a parted bug with esx disks having a corrupt partitiontable.
Run this module with a device name to create a clean partition table on it.
'''
#HAS_FDISK = salt.utils.path.which('fdsik')
HAS_FDISK = salt.utils.which('fdisk')

def __virtual__():
    '''
    Only works on POSIX-like systems
    and if fdisk is available
    '''
    #if salt.utils.platform.is_windows():
    if salt.utils.is_windows():
        return False, 'This module doesn\'t work on Windows.'

    if not HAS_FDISK:
        return False, 'You need fdsik to use this module.'

    return True


def cr_table(device):
    '''
    Create a clean partition table on a device if not allready in use.
    returns True if table was written and returns devicename busy if not.

    .. code-block:: bash

    salt '*' creapar.cr_table device=/dev/sdc
    '''
    bashCommand='echo -e "w" | fdisk ' + device + ' >/dev/null 2>&1'

    try:
        output = subprocess.check_output(bashCommand, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        RC = exc.returncode
        OP = exc.output

        return device + " busy"
    else:
        return True      