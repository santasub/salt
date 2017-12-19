# -*- coding: utf-8 -*-
'''
Add techusers to shadow file

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

    if 'techuser.chk_shadow' in __salt__:
        return True
    else:
        return False, 'techuser module could not be loaded'

def present(name):
    ret = { 
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': 'The techuser {0} is present in /etc/shadow'.format(name) 
     }

    '''
    Check if user is present
    '''
    ret['result'] = __salt__['techuser.chk_shadow'](name)

    if __opts__['test']:
        if not ret['result']:
            ret['comment'] = 'The techuser {0} would have been added to /etc/shadow'.format(name)
            ret['result'] = None

        return ret

    if not ret['result']:
        #USER is absent and have to be created
        ret['result'] = __salt__['techuser.add_shadow'](name)
        ret['changes'].update({'diff': {'old': '','new': name}})               
        ret['comment'] = 'The techuser {0} was added '.format(name)

    return ret

def absent(name):

    ret = { 
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': 'The techuser {0} is absent'.format(name) 
     }

    '''
    Check if user is absent
    '''
    ret['result'] = __salt__['techuser.chk_shadow'](name)

    if __opts__['test']:
        if ret['result']:
            ret['comment'] = 'The techuser {0} would have been removed from /etc/shadow'.format(name)
            ret['result'] = None
        else:
            ret['result'] = True

        return ret

    if ret['result']:
        #USER was present and has to be deleted
        ret['result'] = __salt__['techuser.delete_shadow'](name)
        ret['changes'].update({'diff': {'old': name,'new': ''}})
        ret['comment'] = 'The techuser {0} was deleted from /etc/shadow'.format(name)
    else:
        #becuase an absent user is False in chk function
        ret['result'] = True

    return ret

