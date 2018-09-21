# -*- coding: utf-8 -*-
'''
React to all jobs on a salt-master, looking for changes or errors.
If found return data to an elasticsearch or Logstash server for indexing.

:maintainer:    Andreas Linden <001@hotmail.ch>
:maturity:      New
:depends:       `elasticsearch-py <https://elasticsearch-py.readthedocs.io/en/latest/>`_
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
     es_host: 'SERVERNAME'
     ls_host: 'SERVERNAME'
     es_port: '9200'
     ls_port: '5000'
     es_index: 'salt-log-v1'
     es_doc_type: 'default'
     send_elastic: 'True'
     send_logstash: 'True'

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

try:
  from elasticsearch import Elasticsearch
  from elasticsearch.exceptions import TransportError
  HAS_ELASTIC = True
except ImportError:
  HAS_ELASTIC = False

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
  if not HAS_ELASTIC:
    return False, 'Could not import elasticsearch. Python client is not installed.'

  elasticreactor_config = __opts__['elasticreactor'] if 'elasticreactor' in __opts__ else None

  if elasticreactor_config:
    es_host = elasticreactor_config.get('es_host', None)
    es_port = elasticreactor_config.get('es_port', '9200')

    ls_host = elasticreactor_config.get('ls_host', None)
    ls_port = elasticreactor_config.get('ls_port', '5000')

    es_index = elasticreactor_config.get('es_index', 'salt-log-v1')
    es_index_date = elasticreactor_config.get('es_index_date', False)
    es_doc_type = elasticreactor_config.get('es_doc_type', 'default')

    send_elastic = elasticreactor_config.get('send_elastic', True)
    send_logstash = elasticreactor_config.get('send_logstash', False)


    if send_elastic:
      if not es_host:
        return False, ("Elasticsearch host not defined in config. Please see documentation")

    if send_logstash:
      if not ls_host:
        return False, ("logstash host not defined in config. Please see documentation")

  else:
    return False, ("Could not load elasticreactor or Logstash configuration. Please see documentation")

  return True

def _get_elasticreator_configuration():
  '''
  Return the elasticreactor configuration read from the master config
  '''
  return {
     'es_host': __opts__['elasticreactor']['es_host'],
     'es_port': __opts__['elasticreactor']['es_port'],
     'ls_host': __opts__['elasticreactor']['ls_host'],
     'ls_port': __opts__['elasticreactor']['ls_port'],
     'es_index': __opts__['elasticreactor']['es_index'],
     'es_index_date': __opts__['elasticreactor']['es_index_date'],
     'es_doc_type': __opts__['elasticreactor']['es_doc_type'],
     'send_elastic': __opts__['elasticreactor']['send_elastic'],
     'send_logstash': __opts__['elasticreactor']['send_logstash']
  }

def log_stuff(data_str):
  '''
  Check all the job data strings for Changes or Errors
  '''
  config = _get_elasticreator_configuration()
  data = eval(data_str)
  error = False
  changes = False
  error_count = 0
  change_count = 0
  dryrun = False
  casetype = 'none'
  ids_w_ch = ''
  ids_w_er = ''
  send_elastic = config['send_elastic']
  send_logstash = config['send_logstash']

  if type(data['return']) is dict:
    for state, ret in data['return'].iteritems():
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

    if send_elastic:
      WriteToEs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload)

    if send_logstash:
      WriteToLs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload)

  if changes:
    payload = subprocess.check_output(["salt-run", "jobs.lookup_jid", data['jid']])

    if dryrun:
      casetype = 'DRYRUN'
      change_count = 0
      error_count = 0
    else:
      casetype = 'CHANGE'

    if send_elastic:
      WriteToEs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload)

    if send_logstash:
      WriteToLs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload)

  return True

def WriteToEs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload):
 '''
 Write the gathered data to an elasticsearch server
 '''
 config = _get_elasticreator_configuration()
 utc = UTC()
 master = os.uname()[1]
 minion_name = data['id']
 job_fun = data['fun']
 job_id = data['jid']

 es_data = {}

 es_data['@timestamp'] = datetime.datetime.now(utc).isoformat()
 es_data['case'] = casetype
 es_data['change_count'] = change_count
 es_data['error_count'] = error_count
 es_data['minion'] = minion_name
 es_data['master'] = master
 es_data['fun'] = job_fun
 es_data['jid'] = job_id
 es_data['_stateid_change'] = ids_w_ch
 es_data['_stateid_error'] = ids_w_er
 es_data['data'] = payload

 es_host = config['es_host']
 es_port = config['es_port']
 es_index = config['es_index']
 es_index_date = config['es_index_date']
 es_doc_type= config['es_doc_type']

 if es_index_date:
    es_index = '{0}-{1}'.format(es_index, datetime.date.today().strftime('%Y.%m.%d'))

 es = Elasticsearch([{'host': str(es_host),'port': int(es_port)}])

 try:
   es.index(index=es_index, doc_type=es_doc_type, body=json.dumps(es_data))

 except TransportError as e:
  # ignore already existing index
  if e.error == 'index_already_exists_exception':
    pass
  else:
    raise

  #log.debug('es_host: ' + es_host + ' es_port: ' + es_port + ' es_index: ' + es_index + ' es_doc_type: ' + es_doc_type)
  return True

def WriteToLs(data, casetype, change_count, error_count, ids_w_ch, ids_w_er, payload):
  '''
  Write the gathered data to an elasticsearch server
  '''
  config = _get_elasticreator_configuration()
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
  ls_data['_stateid_change'] = ids_w_ch
  ls_data['_stateid_error'] = ids_w_er
  ls_data['data'] = payload

  try:
    tcpcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  except socket.error as e:
    raise

  try:
    tcpcon.connect((ls_host, int(ls_port)))
  except socket.error as e:
    raise

  tcpcon.send((json.dumps(ls_data) + '\n'))
  tcpcon.close()

  return True
