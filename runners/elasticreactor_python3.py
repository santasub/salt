# -*- coding: utf-8 -*-
'''
React to all jobs on a salt-master, looking for changes or errors.
If found return data to an Logstash înstanz for indexing in elastic.

:maintainer:    Andreas Linden <001@hotmail.ch>
:maturity:      New
:platform:      all

To enable this reactor the elasticsearch python client must be installed
on the salt-master server.

:configuration:

   Enable runners in the salt-master configuration
   # Runner modules
   runner_dirs:
     - /srv/_runners

   Create the file /etc/salt/master.d/reactor.conf and add the following lines to it
   reactor:
     - 'salt/job/*/ret/*':
       - /srv/reactor/salt_elastic_log.sls

   Create the file /srv/reactor/salt_elastic_log.sls and add the following lines to it
   salt_elastic_log:
     runner.elasticreactor.log_stuff:
       - data_str: {{ data|yaml_dquote }}

   Put this script to /srv/_runners/elasticreactor.py

   restart the salt-master

   In order to connect to a elasticsearch Server, you must specify in the Salt master configuration the currently available server.
   elasticreactor:
     ls_host: 'SERVERNAME'
     ls_port: '5000'

'''

from __future__ import absolute_import
from datetime import tzinfo, timedelta

import subprocess
import datetime
import os
import logging
import socket

try:
  import json
except ImportError:
  import simplejson as json

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

  elasticreactor_config = __opts__['elasticreactor'] if 'elasticreactor' in __opts__ else None

  if elasticreactor_config:

    ls_host = elasticreactor_config.get('ls_host', None)
    ls_port = elasticreactor_config.get('ls_port', '5000')

    if not ls_host:
      return False, ("logstash host not defined in config. Please see documentation")

  else:
    return False, ("Could not load Logstash configuration. Please see documentation")

  return True

def _get_logstash_configuration():
  '''
  Return the elasticreactor configuration read from the master config
  '''
  return {
     'ls_host': __opts__['elasticreactor']['ls_host'],
     'ls_port': __opts__['elasticreactor']['ls_port']
  }

def log_stuff(data_str):
  '''
  Check all the job data strings for Changes or Errors
  '''
  config = _get_logstash_configuration()
  data = eval(data_str)
  error = False
  changes = False
  error_count = 0
  change_count = 0
  dryrun = False
  casetype = 'none'
  ids_w_ch = ''
  ids_w_er = ''

  if type(data['return']) is dict:
    for state, ret in data['return'].items():

      if not ret['result']:
        error = True
        error_count += 1

        ids_w_er = ids_w_er + 'StateID: ' + str(ret['__id__'] + '\n')

      if ret['changes']:
        changes = True
        change_count +=1

        ids_w_ch = ids_w_ch + 'StateID: ' + str(ret['__id__'] + '\n')

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

    WriteToLs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload)

  if changes:
    payload = subprocess.check_output(["salt-run", "jobs.lookup_jid", data['jid']])

    if dryrun:
      casetype = 'DRYRUN'
      change_count = 0
      error_count = 0
    else:
      casetype = 'CHANGE'

    WriteToLs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload)

  return True

def WriteToLs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload):
  '''
  Write the gathered data to an logstash server
  '''
  config = _get_logstash_configuration()
  utc = UTC()
  master = os.uname()[1]
  minion_name = data['id']
  job_fun = data['fun']
  job_id = data['jid']

  ls_host = config['ls_host']
  ls_port = config['ls_port']

  ls_data = {}

  ls_data['@timestamp'] = datetime.datetime.now(utc).isoformat()
  ls_data['case'] = casetype
  ls_data['change_count'] = change_count
  ls_data['error_count'] = error_count
  ls_data['minion'] = minion_name
  ls_data['master'] = master
  ls_data['fun'] = job_fun
  ls_data['jid'] = job_id
  ls_data['a_stateid_change'] = ids_w_ch
  ls_data['a_stateid_error'] = ids_w_er
  ls_data['data'] = payload.decode("utf-8")

  try:
    tcpcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  except socket.error as e:
    raise

  try:
    tcpcon.connect((ls_host, int(ls_port)))
  except socket.error as e:
    raise

  tcpcon.send((json.dumps(ls_data).encode("utf-8")))
  tcpcon.close()

  return True


