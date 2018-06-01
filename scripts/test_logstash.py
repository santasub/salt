# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import tzinfo, timedelta

import subprocess
import datetime
import json
import os
import socket

class UTC(tzinfo):
  def utcoffset(self, dt):
    return timedelta(0)

  def tzname(self, dt):
    return 'UTC'

  def dst(self, dt):
    return timedelta(0)

ls_data = {
    '@timestamp': datetime.datetime.now(utc).isoformat(),
    "fqdn": "testhostname.com",
    "message": 'hello world',
    "type": "aix_syslogs",
  }

ls_host = 'SERVERNAME.COM'
ls_port = 10666

utc = UTC()
try:
#  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
except socket.error as e:
  raise


try:
  sock.connect((ls_host, ls_port))
except socket.error as e:
  raise

sock.send(json.dumps(ls_data))
sock.close()