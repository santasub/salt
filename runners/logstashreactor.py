# -*- coding: utf-8 -*-
'''
React to all jobs on a salt-master, looking for changes or errors.
If found return data to an logstash server for indexing.

:maintainer:    Andreas Linden <001@hotmail.ch>
:maturity:      New
:platform:      all

:configuration:

   Enable runners in the salt-master configuration
   # Runner modules
   runner_dirs:
     - /srv/_runners

   Create the file /etc/salt/master.d/reactor.conf and add the following lines to it
   reactor:
     - 'salt/job/*/ret/*':
       - /srv/reactor/salt_logstash_log.sls

   Create the file /srv/reactor/salt_logstash_log.sls and add the following lines to it
   salt_logstash_log:
     runner.logstashreactor.log_stuff:
       - data_str: {{ data|yaml_dquote }}

   Put this script to /srv/_runners/logstashreactor.py

   restart the salt-master

   In order to connect to a logstash Server, you must specify in the Salt master configuration the currently available server.
   logstashreactor:
     ls_host: 'SERVERNAME'
     ls_port: '5000'

'''

from __future__ import absolute_import
from datetime import tzinfo, timedelta

import subprocess
import datetime
import json
import os
import logging
import socket

log = logging.getLogger(__name__)

class UTC(tzinfo):
   def utcoffset(self, dt):
      return timedelta(0)

   def tzname(self, dt):
      return 'UTC'

   def dst(self, dt):
      return timedelta(0)

def __virtual__():
   '''
   Check to see if master config has the necessary config
   '''

   logstash_config = __opts__['logstashreactor'] if 'logstashreactor' in __opts__ else None

   if logstash_config:
      ls_host = logstashreactor_config.get('ls_host', None)
      ls_port = logstashreactor_config.get('ls_port', '5000')

      if not ls_host:
         return False, ("Logstash host not defined in config. Please see documentation")
   else:
      return False, ("Could not load logstashreactor configuration. Please see documentation") 

   return True

def _get_logstashreator_configuration():
   '''
   Return the elasticreactor configuration read from the master config
   '''
   return {
      'ls_host': __opts__['logstashreactor']['ls_host'],
      'ls_port': __opts__['logstashreactor']['ls_port'],
   }

def log_stuff(data_str):
   '''
   Check all the job data strings for Changes or Errors
   '''
   data = eval(data_str)
   error = False
   changes = False
   error_count = 0
   change_count = 0
   dryrun = False
   casetype = 'none'

   if type(data['return']) is dict:
      for state, ret in data['return'].iteritems():

         if not ret['result']:
            error = True
            error_count += 1

         if ret['changes']:
            changes = True
            change_count +=1

         # If test=true set DRYRUN
         if ret['result'] == None:
            dryrun = True

   if error:
      #If Error set changes to false to avoid dubblecall and ERROR is prior
      changes = False
      payload = subprocess.check_output(["salt-run", "jobs.lookup_jid", data['jid']])

      if dryrun:
         casetype = 'DRYRUN'
         change_count = 0
         error_count = 0
      else:
         casetype = 'ERROR'

      WriteToLs(data, casetype, change_count, error_count, payload)

   if changes:
      payload = subprocess.check_output(["salt-run", "jobs.lookup_jid", data['jid']])

      if dryrun:
         casetype = 'DRYRUN'
         change_count = 0
         error_count = 0
      else:
         casetype = 'CHANGE'

      WriteToLs(data, casetype, change_count, error_count, payload)

   return True

def WriteToLS(data, casetype, change_count, error_count, payload):
   '''
   Write the gathered data to an elasticsearch server
   '''
   config = _get_logstashreator_configuration()
   utc = UTC()
   master = os.uname()[1]
   minion_name = data['id']
   job_fun = data['fun']
   job_id = data['jid']

   ls_host = config['ls_host']
   ls_port = config['ls_port']

   try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   except socket.error as e:
      raise

   try:
      sock.connect((ls_host, ls_port))
   except socket.error as e:
      raise

   ls_data = {
         '@timestamp': datetime.datetime.now(utc).isoformat(),
         'case': casetype,
         'change_count': change_count,
         'error_count': error_count,
         'minion': minion_name,
         'master': master,
         'fun': job_fun,
         'jid': job_id,
         'data': payload
   }

   sock.send(json.dumps(ls_data))
   sock.close()

   return True