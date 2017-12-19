#--------------------------------------------------------------------------------
#
# Statetype:    SW
# Description:  HOW TO SALT 
# Implemented:  14.06.2017
# Owner:        santasub
#
#--------------------------------------------------------------------------------
{% if 'i_should_not_set_this_grain_on_a_server' in grains["SOFTWAREGROUPS"] %}
######################
# SALT BASIC STUFF
######################
# FILES
/tmp/salt_test.txt:
  file.managed:
    - user: root
    - group: root
    - mode: 0644
    - source: salt://PATH/TO/YOUR/TEMPLATE/FILES/salt_test.template
    - template: jinja

# FOLDERS
/tmp/test/:
  file.directory:
    - user: root
    - group: root
    - mode: 0755

# USERS
testuser:
  user.present:
    - shell: /usr/bin/ksh
    - uid: 754
    - gid: 754
    - home: /opt/testuser
    - createhome: true
    - fullname: 'test Account for Demo'

# TECH USERS
test user passwd:
  techuser.present:
    - name: test
    - uid: 13123
    - gid: 13123
    - home: /opt/test
    - shell: /bin/bash
    - fullname: techn. user test

# TECH USERS SHADOW
test user shadow:
  techuser_shadow.present:
    - name: test

# GROUPS
testgroup:
  group.present:
    - gid: 754
    - system: True
    - addusers:
      - jonny

# COOP TECH GROUPS
test group:
  techgrp.present:
    - name: test
    - gid: 13123

# NISNET Groups
L-ADM:
  netgroup.present:
    - name: L-ADM

# SERVICES DAEMONS
sshd:
  service.running:
    - enable: True

# RPMS
install test rpm:
  pkg.installed:
    - name: git
#OR
git:
  pkg.installed: []

######################
# VARIABLES
######################

# Assign value to variable
{% set VAR_A = "value_a" %}

# Variable Concatenation 
{% set VAR_B = "much" %}
{% set CONCATENATED_STRING = 'This is now a ' + VAR_B + ' longer string' %}

######################
# IF
######################

# IF variable has Value
{% if VAR_A == "value_a" %}
Return Variable_1:
  cmd.run:
    - name: echo '{{ VAR_A }}'
{% endif %}

# IF variable startswith a specific string
{% if grains['DMZ'].startswith('dmz_sz') -%}
Return Variable_2:
  cmd.run:
    - name: echo '{{ grains['DMZ'] }}'
{% endif %}

#IF installed pkg has a specific version
{% if salt['pkg.version']('systemd') == '228-132.1' %}
Return Variable_3:
  cmd.run:
    - name: echo '{{ pkg.version']('systemd') }}'
{% endif %}

# IF FILE DOES NOT EXISTS
{% if not salt['file.file_exists']('/tmp/salt_test.txt') %}
Return Variable_4:
  cmd.run:
    - name: echo '{{ file.file_exists']('/tmp/salt_test.txt') }}'
{% endif %}

######################
# Relative path
######################

# Set relative Path for statefiles separatet with .
{% set statepath_sls = sls.split('.')[:-1] | join('.') %}

# Sample
{% import_yaml statepath_sls + '/instances/file_to_imort.yml' as imported_file %}

# Set relative Path for template and file imports separatet with /
{% set statepath_template = sls.split('.')[:-1] | join('/') %}

# Sample
/the/path/to/your/file.txt:
  file.managed:
    - user: root
    - group: root
    - mode: 0644
    - source: salt://{{ statepath_template }}/files/service.template
    - template: jinja

######################
# Grain Brake
######################
{% if 'your_software_name' in grains["SOFTWAREGROUPS"] %}
Return Variable_5:
  cmd.run:
    - name: echo 'install your software now.'
{% endif %}

{% endif %}