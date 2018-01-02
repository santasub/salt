# -*- coding: utf-8 -*-
'''
React to all jobs on a salt-master, looking for changes or errors.
If found return data to an elasticsearch server for indexing.

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
     es_port: '9200'
     es_index: 'salt-log-v1'
     es_doc_type: 'default'

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
      es_index = elasticreactor_config.get('es_index', 'salt-log-v1')
      es_doc_type = elasticreactor_config.get('es_doc_type', 'default')

      if not es_host:
         return False, ("Elasticsearch host not defined in config. Please see documentation")

   else:
      return False, ("Could not load elasticreactor configuration. Please see documentation") 

   return True

def _get_elasticreator_configuration():
   '''
   Return the elasticreactor configuration read from the master config
   '''
   return {
      'es_host': __opts__['elasticreactor']['es_host'],
      'es_port': __opts__['elasticreactor']['es_port'],
      'es_index': __opts__['elasticreactor']['es_index'],
      'es_doc_type': __opts__['elasticreactor']['es_doc_type']
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

      WriteToEs(data, casetype, change_count, error_count, payload)

   if changes:
      payload = subprocess.check_output(["salt-run", "jobs.lookup_jid", data['jid']])

      if dryrun:
         casetype = 'DRYRUN'
         change_count = 0
         error_count = 0
      else:
         casetype = 'CHANGE'

      WriteToEs(data, casetype, change_count, error_count, payload)

   return True

def WriteToEs(data, casetype, change_count, error_count, payload):
   '''
   Write the gathered data to an elasticsearch server
   '''
   config = _get_elasticreator_configuration()
   utc = UTC()
   master = os.uname()[1]
   minion_name = data['id']
   job_fun = data['fun']
   job_id = data['jid']

   es_data = {
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

   es_host = config['es_host']
   es_port = config['es_port']
   es_index = config['es_index']
   es_index_date = config['es_index']
   es_doc_type= config['es_doc_type']

   if es_index_date:
      es_index = '{0}-{1}'.format(es_index, datetime.date.today().strftime('%Y.%m.%d')) 

   es = Elasticsearch([{'host': es_host,'port': es_port}])

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

def WriteToLS(data, casetype, change_count, error_count, payload):
   '''
   Write the gathered data to an elasticsearch server
   '''
   config = _get_elasticreator_configuration()
   utc = UTC()
   master = os.uname()[1]
   minion_name = data['id']
   job_fun = data['fun']
   job_id = data['jid']

   ls_host = config['es_host']
   ls_port = config['es_port']
   ls_index = config['es_index']
   ls_index_date = config['es_index']
   ls_doc_type= config['es_doc_type']

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