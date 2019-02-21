# -*- coding: utf-8 -*-
'''
Module to get system metrics and informations to log them into a elastic/logstash instance
'''
from __future__ import absolute_import
from datetime import tzinfo, timedelta

import subprocess
import datetime
import os
import logging
import socket
import salt

try:
  import json
except ImportError:
  import simplejson as json

log = logging.getLogger(__name__)

__virtualname__ = 'systat'

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
  Only works on POSIX-like systems
  '''
  #if salt.utils.platform.is_windows():
  if salt.utils.is_windows():
    return False, 'This module doesn\'t work on Windows.'


  if not HAS_ELASTIC:
    return False, 'Could not import elasticsearch. Python client is not installed.'

  return __virtualname__


def _get_CORPORATION():
    '''
    '''
    result = __grains__.get('CORPORATION')

    return result

def _get_CSBVERS():
    '''
    '''
    result = __grains__.get('CSBVERS')

    return result

def _get_DMZ():
    '''
    '''
    result = __grains__.get('DMZ')

    return result

def _get_ENVIRONMENT():
    '''
    '''
    result = __grains__.get('ENVIRONMENT')

    return result

def _get_FLAGS():
    '''
    '''
    result = __grains__.get('FLAGS')

    return result

def _get_HIGHSTATE():
    '''
    '''
    result = __grains__.get('HIGHSTATE')

    return result

def _get_LOCATION():
    '''
    '''
    result = __grains__.get('LOCATION')

    return result

def _get_PILOT():
    '''
    '''
    result = __grains__.get('PILOT')

    return result

def _get_SOFTWAREGROUPS():
    '''
    '''
    result = __grains__.get('SOFTWAREGROUPS')

    return result

def _get_SSDs():
    '''
    '''
    result = __grains__.get('SSDs')

    return result

def _get_biosreleasedate():
    '''
    '''
    result = __grains__.get('biosreleasedate')

    return result

def _get_biosversion():
    '''
    '''
    result = __grains__.get('biosversion')

    return result

def _get_cpu_flags():
    '''
    '''
    result = __grains__.get('cpu_flags')

    return result

def _get_cpu_model():
    '''
    '''
    result = __grains__.get('cpu_model')

    return result

def _get_cpuarch():
    '''
    '''
    result = __grains__.get('cpuarch')

    return result

def _get_cpusockets():
    '''
    '''
    result = __grains__.get('cpusockets')

    return result

def _get_disks():
    '''
    '''
    result = __grains__.get('disks')

    return result

def _get_dns_domain():
    '''
    '''
    result = __salt__['grains.get']('dns:domain')

    return result

def _get_dns_ip4_nameservers():
    '''
    '''
    result = __salt__['grains.get']('dns:ip4_nameservers')

    return result

def _get_dns_ip6_nameservers():
    '''
    '''
    result = __salt__['grains.get']('dns:ip6_nameservers')

    return result

def _get_dns_nameservers():
    '''
    '''
    result = __salt__['grains.get']('dns:nameservers')

    return result

def _get_dns_options():
    '''
    '''
    result = __salt__['grains.get']('dns:options')

    return result

def _get_dns_search():
    '''
    '''
    result = __salt__['grains.get']('dns:search')

    return result

def _get_dns_sortlist():
    '''
    '''
    result = __salt__['grains.get']('dns:sortlist')

    return result

def _get_domain():
    '''
    '''
    result = __grains__.get('domain')

    return result

def _get_fqdn():
    '''
    '''
    result = __grains__.get('fqdn')

    return result

def _get_fqdn_ip4():
    '''
    '''
    result = __grains__.get('fqdn_ip4')

    return result

def _get_fqdn_ip6():
    '''
    '''
    result = __grains__.get('fqdn_ip6')

    return result

def _get_fqdns():
    '''
    '''
    result = __grains__.get('fqdns')

    return result

def _get_gid():
    '''
    '''
    result = __grains__.get('gid')

    return result

def _get_gpus_model():
    '''
    '''
    result = __salt__['grains.get']('gpus:model')

    return result

def _get_gpus_vendor():
    '''
    '''
    result = __salt__['grains.get']('gpus:vendor')

    return result

def _get_groupname():
    '''
    '''
    result = __grains__.get('groupname')

    return result

def _get_host():
    '''
    '''
    result = __grains__.get('host')

    return result

def _get_hwaddr_interfaces_eth0():
    '''
    '''
    result = __salt__['grains.get']('hwaddr_interfaces:eth0')

    return result

def _get_hwaddr_interfaces_lo():
    '''
    '''
    result = __salt__['grains.get']('hwaddr_interfaces:lo')

    return result

def _get_id():
    '''
    '''
    result = __grains__.get('id')

    return result

def _get_init():
    '''
    '''
    result = __grains__.get('init')

    return result

def _get_ip4_interfaces_eth0():
    '''
    '''
    result = __salt__['grains.get']('ip4_interfaces:eth0')

    return result

def _get_ip4_interfaces_lo():
    '''
    '''
    result = __salt__['grains.get']('ip4_interfaces:lo')

    return result

def _get_ip6_interfaces_eth0():
    '''
    '''
    result = __salt__['grains.get']('ip6_interfaces:eth0')

    return result

def _get_ip6_interfaces_lo():
    '''
    '''
    result = __salt__['grains.get']('ip6_interfaces:lo')

    return result

def _get_ipv4():
    '''
    '''
    result = __grains__.get('ipv4')

    return result

def _get_ipv6():
    '''
    '''
    result = __grains__.get('ipv6')

    return result

def _get_kernel():
    '''
    '''
    result = __grains__.get('kernel')

    return result

def _get_kernelrelease():
    '''
    '''
    result = __grains__.get('kernelrelease')

    return result

def _get_locale_info_defaultencoding():
    '''
    '''
    result = __salt__['grains.get']('locale_info:defaultencoding')

    return result

def _get_locale_info_defaultlanguage():
    '''
    '''
    result = __salt__['grains.get']('locale_info:defaultlanguage')

    return result

def _get_locale_info_detectedencoding():
    '''
    '''
    result = __salt__['grains.get']('locale_info:detectedencoding')

    return result

def _get_localhost():
    '''
    '''
    result = __grains__.get('localhost')

    return result

def _get_lsb_distrib_codename():
    '''
    '''
    result = __grains__.get('lsb_distrib_codename')

    return result

def _get_lsb_distrib_id():
    '''
    '''
    result = __grains__.get('lsb_distrib_id')

    return result

def _get_lsb_distrib_release():
    '''
    '''
    result = __grains__.get('lsb_distrib_release')

    return result

def _get_machine_id():
    '''
    '''
    result = __grains__.get('machine_id')

    return result

def _get_manufacturer():
    '''
    '''
    result = __grains__.get('manufacturer')

    return result

def _get_master():
    '''
    '''
    result = __grains__.get('master')

    return result

def _get_mem_total():
    '''
    '''
    result = __grains__.get('mem_total')

    return result

def _get_nodename():
    '''
    '''
    result = __grains__.get('CORPORATION')

    return result

def _get_num_cpus():
    '''
    '''
    result = __grains__.get('num_cpus')

    return result

def _get_num_gpus():
    '''
    '''
    result = __grains__.get('num_gpus')

    return result

def _get_os():
    '''
    '''
    result = __grains__.get('os')

    return result

def _get_os_family():
    '''
    '''
    result = __grains__.get('os_family')

    return result

def _get_osarch():
    '''
    '''
    result = __grains__.get('osarch')

    return result

def _get_oscodename():
    '''
    '''
    result = __grains__.get('oscodename')

    return result

def _get_osfinger():
    '''
    '''
    result = __grains__.get('osfinger')

    return result

def _get_osfullname():
    '''
    '''
    result = __grains__.get('osfullname')

    return result

def _get_osmajorrelease():
    '''
    '''
    result = __grains__.get('osmajorrelease')

    return result

def _get_osrelease():
    '''
    '''
    result = __grains__.get('osrelease')

    return result

def _get_osrelease_info():
    '''
    '''
    result = __grains__.get('osrelease_info')

    return result

def _get_path():
    '''
    '''
    result = __grains__.get('path')

    return result

def _get_pid():
    '''
    '''
    result = __grains__.get('pid')

    return result

def _get_productname():
    '''
    '''
    result = __grains__.get('productname')

    return result

def _get_ps():
    '''
    '''
    result = __grains__.get('ps')

    return result

def _get_pythonexecutable():
    '''
    '''
    result = __grains__.get('pythonexecutable')

    return result

def _get_pythonpath():
    '''
    '''
    result = __grains__.get('pythonpath')

    return result

def _get_pythonversion():
    '''
    '''
    result = __grains__.get('pythonversion')

    return result

def _get_saltpath():
    '''
    '''
    result = __grains__.get('saltpath')

    return result

def _get_saltversion():
    '''
    '''
    result = __grains__.get('saltversion')

    return result

def _get_saltversioninfo():
    '''
    '''
    result = __grains__.get('saltversioninfo')

    return result

def _get_serialnumber():
    '''
    '''
    result = __grains__.get('serialnumber')

    return result

def _get_server_id():
    '''
    '''
    result = __grains__.get('server_id')

    return result

def _get_shell():
    '''
    '''
    result = __grains__.get('shell')

    return result

def _get_susemanager_activation_key():
    '''
    '''
    result = __salt__['grains.get']('susemanager:activation_key')

    return result

def _get_systemd_features():
    '''
    '''
    result = __salt__['grains.get']('systemd:features')

    return result

def _get_systemd_version():
    '''
    '''
    result = __salt__['grains.get']('systemd:version')

    return result

def _get_total_num_cpus():
    '''
    '''
    result = __grains__.get('total_num_cpus')

    return result

def _get_uid():
    '''
    '''
    result = __grains__.get('uid')

    return result

def _get_username():
    '''
    '''
    result = __grains__.get('username')

    return result

def _get_uuid():
    '''
    '''
    result = __grains__.get('uuid')

    return result

def _get_virtual():
    '''
    '''
    result = __grains__.get('virtual')

    return result

def _get_zmqversion():
    '''
    '''
    result = __grains__.get('zmqversion')

    return result

def _get_netgroups():
    '''
    '''
    result = __salt__['netgroup.list']()

    return result

def _get_loggedones():
    '''
    '''
    cmd = 'last'
    result = __salt__['cmd.run'](cmd, output_loglevel='quiet', python_shell=False)

    return result

def _get_uptime():
    '''
    '''
    cmd = 'uptime'
    result = __salt__['cmd.run'](cmd, output_loglevel='quiet', python_shell=False)

    return result

def _get_geo_cords():

    location = _get_LOCATION()

    geo_cords = 'none'

    if location == 'basel':
        geo_cords = 'u0mqkyqcj4cf'

    if location == 'bern':
      geo_cords = 'u0m5p3z0ffhk'

    if location == 'bern_rz':
      geo_cords = 'u0m5p3z0ffhk'

    return geo_cords

def _get_geo_iso_3166_2():

    location = _get_LOCATION()

    geo_iso = 'none'

    if location == 'basel':
        geo_iso = 'CH-BS'

    if location == 'bern':
        geo_iso = 'CH-BE'

    return geo_iso

def get_infos():
  ls_data = {}

  ls_data['@timestamp'] = datetime.datetime.now(UTC()).isoformat()
  ls_data['CORPORATION'] = str(_get_CORPORATION())
  ls_data['CSBVERS'] = str(_get_CSBVERS())
  ls_data['DMZ'] = str(_get_DMZ())
  ls_data['ENVIRONMENT'] = str(_get_ENVIRONMENT())
  ls_data['FLAGS'] = str(_get_FLAGS())
  ls_data['HIGHSTATE'] = str(_get_HIGHSTATE())
  ls_data['LOCATION'] = str(_get_LOCATION())
  ls_data['PILOT'] = str(_get_PILOT())
  ls_data['SOFTWAREGROUPS'] = str(_get_SOFTWAREGROUPS())
  ls_data['SSDs'] = str(_get_SSDs())
  ls_data['biosreleasedate'] = str(_get_biosreleasedate())
  ls_data['biosversion'] = str(_get_biosversion())
  ls_data['cpu_flags'] = str(_get_cpu_flags())
  ls_data['cpu_model'] = str(_get_cpu_model())
  ls_data['cpuarch'] = str(_get_cpuarch())
  ls_data['cpusockets'] = str(_get_cpusockets())
  ls_data['disks'] = str(_get_disks())
  ls_data['dns_domain'] = str(_get_dns_domain())
  ls_data['dns_ip4_nameservers'] = str(_get_dns_ip4_nameservers())
  ls_data['dns_ip6_nameservers'] = str(_get_dns_ip6_nameservers())
  ls_data['dns_nameservers'] = str(_get_dns_nameservers())
  ls_data['dns_options'] = str(_get_dns_options())
  ls_data['dns_search'] = str(_get_dns_search())
  ls_data['dns_sortlist'] = str(_get_dns_sortlist())
  ls_data['domain'] = str(_get_domain())
  ls_data['fqdn'] = str(_get_fqdn())
  ls_data['fqdn_ip4'] = str(_get_fqdn_ip4())
  ls_data['fqdn_ip6'] = str(_get_fqdn_ip6())
  ls_data['fqdns'] = str(_get_fqdns())
  ls_data['gid'] = str(_get_gid())
  ls_data['gpus_model'] = str(_get_gpus_model())
  ls_data['gpus_vendor'] = str(_get_gpus_vendor())
  ls_data['groupname'] = str(_get_groupname())
  ls_data['host'] = str(_get_host())
  ls_data['hwaddr_interfaces_eth0'] = str(_get_hwaddr_interfaces_eth0())
  ls_data['hwaddr_interfaces_lo'] = str(_get_hwaddr_interfaces_lo())
  ls_data['id'] = str(_get_id())
  ls_data['init'] = str(_get_init())
  ls_data['ip4_interfaces_eth0'] = str(_get_ip4_interfaces_eth0())
  ls_data['ip4_interfaces_lo'] = str(_get_ip4_interfaces_lo())
  ls_data['ip6_interfaces_eth0'] = str(_get_ip6_interfaces_eth0())
  ls_data['ip6_interfaces_lo'] = str(_get_ip6_interfaces_lo())
  ls_data['ipv4'] = str(_get_ipv4())
  ls_data['ipv6'] = str(_get_ipv6())
  ls_data['kernel'] = str(_get_kernel())
  ls_data['kernelrelease'] = str(_get_kernelrelease())
  ls_data['locale_defaultencoding'] = str(_get_locale_info_defaultencoding())
  ls_data['locale_defaultlanguage'] = str(_get_locale_info_defaultlanguage())
  ls_data['locale_detectedencoding'] = str(_get_locale_info_detectedencoding())
  ls_data['localhost'] = str(_get_localhost())
  ls_data['lsb_distrib_codename'] = str(_get_lsb_distrib_codename())
  ls_data['lsb_distrib_id'] = str(_get_lsb_distrib_id())
  ls_data['lsb_distrib_release'] = str(_get_lsb_distrib_release())
  ls_data['machine_id'] = str(_get_machine_id())
  ls_data['manufacturer'] = str(_get_manufacturer())
  ls_data['master'] = str(_get_master())
  ls_data['mem_total'] = str(_get_mem_total())
  ls_data['nodename'] = str(_get_nodename())
  ls_data['num_cpus'] = str(_get_num_cpus())
  ls_data['num_gpus'] = str(_get_num_gpus())
  ls_data['os'] = str(_get_os())
  ls_data['os_family'] = str(_get_os_family())
  ls_data['osarch'] = str(_get_osarch())
  ls_data['oscodename'] = str(_get_oscodename())
  ls_data['osfinger'] = str(_get_osfinger())
  ls_data['osfullname'] = str(_get_osfullname())
  ls_data['osmajorrelease'] = str(_get_osmajorrelease())
  ls_data['osrelease'] = str(_get_osrelease())
  ls_data['osrelease_info'] = str(_get_osrelease_info())
  ls_data['path'] = str(_get_path())
  ls_data['pid'] = str(_get_pid())
  ls_data['productname'] = str(_get_productname())
  ls_data['ps'] = str(_get_ps())
  ls_data['pythonexecutable'] = str(_get_pythonexecutable())
  ls_data['pythonpath'] = str(_get_pythonpath())
  ls_data['pythonversion'] = str(_get_pythonversion())
  ls_data['saltpath'] = str(_get_saltpath())
  ls_data['saltversion'] = str(_get_saltversion())
  ls_data['saltversioninfo'] = str(_get_saltversioninfo())
  ls_data['serialnumber'] = str(_get_serialnumber())
  ls_data['server_id'] = str(_get_server_id())
  ls_data['shell'] = str(_get_shell())
  ls_data['susemanager_activation_key'] = str(_get_susemanager_activation_key())
  ls_data['systemd_features'] = str(_get_systemd_features())
  ls_data['systemd_version'] = str(_get_systemd_version())
  ls_data['total_num_cpus'] = str(_get_total_num_cpus())
  ls_data['uid'] = str(_get_uid())
  ls_data['username'] = str(_get_username())
  ls_data['uuid'] = str(_get_uuid())
  ls_data['virtual'] = str(_get_virtual())
  ls_data['zmqversion'] = str(_get_zmqversion())
  ls_data['netgroups'] = str(_get_netgroups())
  ls_data['loggedones'] = str(_get_loggedones())
  ls_data['uptime'] = str(_get_uptime())
  ls_data['geo_cords'] = str(_get_geo_cords())
  ls_data['geo_iso'] = str(_get_geo_iso_3166_2())

  ls_host = 'SERVERNAME'
  ls_port = '9200'
  ls_index = 'system_info'
  ls_index_date = 'True'
  ls_doc_type= 'default'

  if ls_index_date:
    ls_index = '{0}-{1}'.format(ls_index, datetime.date.today().strftime('%Y.%m.%d'))

  ls = Elasticsearch([{'host': str(ls_host),'port': int(ls_port)}])

  try:
    ls.index(index=ls_index, doc_type=ls_doc_type, body=json.dumps(ls_data))

  except TransportError as e:
    # ignore already existing index
    if e.error == 'index_already_exists_exception':
      pass
    else:
      raise
  #log.debug('es_host: ' + es_host + ' es_port: ' + es_port + ' es_index: ' + es_index + ' es_doc_type: ' + es_doc_type)
  return True
