import salt
import commands
import os
import salt.utils
# Change salt.utils in future release of salt to the following
#import salt.utils.platform
'''
Module to manage nis/ldap groups stored in the passwd file
'''

def __virtual__():
    '''
    Only works on POSIX-like systems
    '''
    #if salt.utils.platform.is_windows():
    if salt.utils.is_windows():
        return False, 'This module doesn\'t work on Windows.'

    return True

def list():
    '''
    Returns all avaliable netgroups in the passwd file
    this includes the '+::::::/sbin/nologin' entry.
    These Groups are identified by the "+@".

    .. code-block:: bash

    salt '*' netgroup.list
    '''
    NGlist = []
    for line in open('/etc/passwd','r').readlines():
        if "+@" in line:
            NGlist.append(line)
        elif "+::::::/sbin/nologin" in line:
            NGlist.append(line)

    return (NGlist)

def chk(name):
    '''
	Checks if a named group is available on the system
    returns True when Group is present and Flase if not.

        .. code-block:: bash

    salt '*' netgroup.chk name=L-ADMIN
	'''
    with open('/etc/passwd', 'r+') as newfile:

        line_found = any(name in line for line in newfile)

        if line_found:
            return True
        else:
            return False

def add(name):
    '''
    Adds a netgroup to the passwd file. It returns True when the group was created
    and False if the group was allready there.
    
    It also adds '+::::::/sbin/nologin' as a last line to the file if not already present.

    .. code-block:: bash

    salt '*' netgroup.add name=L-ADMIN
    '''
    delete("+::::::/sbin/nologin")

    with open('/etc/passwd', 'r+') as newfile:
        line_found = any(name in line for line in newfile)

        if not line_found:
            newfile.seek(0, os.SEEK_END)
            newfile.write('+@' + name +'::::::\n+::::::/sbin/nologin\n')
            return True
        else:
            newfile.seek(0, os.SEEK_END)
            newfile.write('+::::::/sbin/nologin\n')
            return False


def delete(name):
    '''
    Removes a netgroup from the passwd file if present.
    It returns True if a group was deletet and False if not.

    .. code-block:: bash

    salt '*' netgroup.delete name=L-ADMIN
    '''
    counter = 0
    #with open('/etc/passwd') as oldfile, open('/etc/newpasswd', 'w') as newfile:
    #FIX because python 2.6 dont like the above version 
    with open('/etc/passwd') as oldfile:
        with open('/etc/newpasswd', 'w') as newfile:
            for line in oldfile:
                if name not in line:
                    newfile.write(line)
                else:
                	counter += 1
    os.rename('/etc/newpasswd','/etc/passwd')

    if counter == 0:
    	# if Grp was not present and no delete happend
    	return False
    else:
    	# if Grp was present and delete happend
    	return True