# -*- coding: utf-8 -*-
'''
Add Netgroups to passwd

'''
# Import python libs
from __future__ import absolute_import
import logging
import salt.utils
# Change salt.utils in future release of salt to the following
#import salt.utils.platform

log = logging.getLogger(__name__)

def __virtual__():
    '''
    Only works on POSIX-like systems
    '''
    #if salt.utils.platform.is_windows():
    if salt.utils.is_windows():
        return False, 'This module doesn\'t work on Windows.'

    if 'netgroup.chk' in __salt__:
        return True
    else:
        return False, 'netgroup module could not be loaded'

def present(name):
    ret = { 
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': 'The netgroup {0} is present in /etc/passwd'.format(name) 
     }

    '''
    Check if Netgroup is present
    '''
    ret['result'] = __salt__['netgroup.chk'](name)

    if __opts__['test']:
        if not ret['result']:
            ret['comment'] = 'The netgroup {0} would have been added to /etc/passwd'.format(name)
            ret['result'] = None

        return ret

    if not ret['result']:
        #GRP is absent and have to be created
        ret['result'] = __salt__['netgroup.add'](name)
        ret['changes'].update({'diff': {'old': '','new': name}})               
        ret['comment'] = 'The netgroup {0} was added to /etc/passwd'.format(name)

    return ret

def absent(name):

    ret = { 
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': 'The netgroup {0} is absent'.format(name) 
     }

    '''
    Check if Netgroup is absent
    '''
    ret['result'] = __salt__['netgroup.chk'](name)

    if __opts__['test']:
        if ret['result']:
            ret['comment'] = 'The netgroup {0} would have been removed from /etc/passwd'.format(name)
            ret['result'] = None
        else:
            ret['result'] = True

        return ret

    if ret['result']:
        #GRP was present and has to be deleted
        ret['result'] = __salt__['netgroup.delete'](name)
        ret['changes'].update({'diff': {'old': name,'new': ''}})
        ret['comment'] = 'The netgroup {0} was removed from /etc/passwd'.format(name)
    else:
        #becuase an absent user is False in chk function
        ret['result'] = True

    return ret

