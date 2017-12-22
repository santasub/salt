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
     es_host: '"SERVERNAME1", "SERVERNAME2", "SERVERNAME3"'
     es_port: '9200'
     es_index: 'salt-log-v1'
     es_index_date: True
     es_doc_type: 'default'
     es_number_of_shards: 5
     es_number_of_replicas: 1

'''

from __future__ import absolute_import
from datetime import tzinfo, timedelta
from elasticsearch.exceptions import TransportError

import subprocess
import datetime
import json
import os
import logging

log = logging.getLogger(__name__)

try:
   from elasticsearch import Elasticsearch
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
      es_index_date = elasticreactor_config.get('es_index', False)
      es_doc_type = elasticreactor_config.get('es_doc_type', 'default')
      es_number_of_shards = elasticreactor_config.get('es_number_of_shards', '1')
      es_number_of_replicas = elasticreactor_config.get('es_number_of_replicas', '0')

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
      'es_index_date': __opts__['elasticreactor']['es_index_date'],
      'es_doc_type': __opts__['elasticreactor']['es_doc_type'],
      'es_number_of_shards': __opts__['elasticreactor']['es_number_of_shards'],
      'es_number_of_replicas': __opts__['elasticreactor']['es_number_of_replicas']
   }

def CreateIndex():
   config = _get_elasticreator_configuration()
   es_host = config['es_host']
   es_port = config['es_port']
   es_index = config['es_index']
   es_index_date = config['es_index']
   es_doc_type = config['es_doc_type']
   es_number_of_shards = config['es_number_of_shards']
   es_number_of_replicas = config['es_number_of_replicas']

   if es_index_date:
      es_index = '{0}-{1}'.format(es_index, datetime.date.today().strftime('%Y.%m.%d')) 

   es_create = {
     'mappings': {
       'default': {
         'properties': {
           '@timestamp': {'type': 'date'},
           'case': {'type': 'keyword'},
           'change_count': {'type': 'long'},
           'data': {'type': 'keyword'},
           'error_count': {'type': 'long'},
           'fun': {'type': 'keyword'},
           'jid': {'type': 'keyword'},
           'master': {'type': 'keyword'},
           'minion': {'type': 'text','fields': {'keyword': {'type': 'keyword','ignore_above': 256}}}
         }
       }
     },
     'settings': {
       'index': {
         'number_of_shards': es_number_of_shards,
         'number_of_replicas': es_number_of_replicas,
       }
     }
   }

   es = Elasticsearch([{'host': es_host,'port': es_port}])

   try:
      #Write Settings and Mappings
      es.indices.create(index=es_index, body=json.dumps(es_create))

   except TransportError as e:
      # ignore already existing index
      if e.error == 'index_already_exists_exception':
         pass
      else:
         raise

def getInfo():
   config = _get_elasticreator_configuration()
   print config['es_host']
   print config['es_port']
   print config['es_index']
   print config['es_index_date']
   print config['es_doc_type']
   print config['es_number_of_shards']
   print config['es_number_of_replicas']