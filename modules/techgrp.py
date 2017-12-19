import salt
import commands
import os
import salt.utils
# Change salt.utils in future release of salt to the following
#import salt.utils.path
#import salt.utils.platform
'''
Module to manage tech groups stored in the group file.

WARNING: dont use this module to create local groups.
use salt.module.group insted

This Module is used to Create Technical groups that are allready
stored in the META or LDAP and allocal useradd would not work.

'''
def __virtual__():
    '''
    Only works on POSIX-like systems
    '''
    #if salt.utils.platform.is_windows():
    if salt.utils.is_windows():
        return False, 'This module doesn\'t work on Windows.'

    return True

def list(name):
    '''
    Returns the requested group entry from the group file.

    .. code-block:: bash

    CLI Example:

    salt '*' techgrp.list foo
    '''

    name2lst = str(name + ':x')

    NGlist = []
    for line in open('/etc/group','r').readlines():
        if name2lst in line:
            NGlist.append(line)
    return (NGlist)

def chk(name):
    '''
    Checks if a given group is available on the system
    returns True when the group is present and False if not.

    This is a local file check only.

        .. code-block:: bash

    CLI Example:

    salt '*' techgrp.chk name=foo
	'''
    name2chk = str(name + ':x')

    with open('/etc/group', 'r+') as newfile:

        line_found = any(name2chk in line for line in newfile)

        if line_found:
            return True
        else:
            return False

def add(name, gid):
    '''
    Adds a Techgroup to the group file. It returns True when the group was created
    and False if the group was allready there.

    WARNING: this is not to be used for normal linux group!
    use salt.module.group.add insted
    
    .. code-block:: bash
    
    CLI Example:

    salt '*' techgrp.add name=foo gid=123

    '''

    if not chk(name):
        #group does not exist
        with open('/etc/group', 'r+') as newfile:
            newfile.seek(0, os.SEEK_END)
            newfile.write(str(name) + ':x:' + str(gid) + ':\n')
        return True
    else:
        return False


def delete(name):
    '''
    Removes a group from the group file if present.

    WARNING: this is not to be used for normal linux users!
    use salt.module.group.delete insted

    It returns True if a group was deletet and False if not.

    .. code-block:: bash

    CLI Example:

    salt '*' techgrp.delete name=foo
    '''
    
    name2del = str(name + ':x')
    counter = 0
    #with open('/etc/passwd') as oldfile, open('/etc/newpasswd', 'w') as newfile:
    #FIX because python 2.6 dont like the above version 
    with open('/etc/group') as oldfile:
        with open('/etc/newgroup', 'w') as newfile:
            for line in oldfile:
                if name2del not in line:
                    newfile.write(line)
                else:
                	counter += 1
    os.rename('/etc/newgroup','/etc/group')

    if counter == 0:
    	# if Grp was not present and no delete happend
    	return False
    else:
    	# if Grp was present and delete happend
    	return True
