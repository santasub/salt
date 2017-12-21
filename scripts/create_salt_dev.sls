#--------------------------------------------------------------------------------
#
# Statetype:      HELPER
# Description:    Creates a Salt Testing server with local gitrepo.
#                 This script is used in a Suse-Manager3X as Salt-Master Setup.
#                 It Needs a ENVIRONMENT gain set to ENTW
# Implemented:    27.11.2017
# Owner:          santasub
#
#--------------------------------------------------------------------------------
{% set local_repo_path = '/srv/salt/mystack' %}
{% set remote_repo_path = 'http://github.com/yourgit/salt-states/yourstack.git' %}

{% if grains['ENVIRONMENT'] == 'ENTW' %}
Remove HighstateJOB:
  schedule.absent:
    - name: HighstateJOB

InstallGit:
  pkg.installed:
    - name: git

CreateFileRoots:
  file.directory:
    - name: /srv/salt
    - user: root
    - group: root
    - makedirs: True
    - dir_mode: 0755
    - file_mode: 0755

Remove susemanager.conf:
  file.absent:
    - name: /etc/salt/minion.d/susemanager.conf

AddConf:
  file.blockreplace:
    - name: /etc/salt/minion
    - marker_start: "# SALT Test configuration override START do not remove"
    - content: |
        file_client: local
        file_roots:
          base:
            - {{ local_repo_path }}
    - marker_end: "# SALT Test configuration override END do not remove"
    - append_if_not_found: True
    - backup: '.bak'
    - show_changes: True

{% if not salt['file.directory_exists'](local_repo_path) %}
CloneRepo:
  git.latest:
    - name: {{ remote_repo_path }}
    - target: {{ local_repo_path }}
    - user: root
{% else %}
GiveErrMSG:
  cmd.run:
    - name: echo "{{ local_repo_path }} repository is allready present. Please remove it first or run 'git fetch -f' to update!"
{% endif %}

RestartMinion:
  service.running:
    - name: salt-minion
    - watch:
      - file: /etc/salt/minion
{% else %}
GiveEnvErrMSG:
  cmd.run:
    - name: echo "You cannot put an TEST/PRDO System in dev mode --> You should have known that!"
{% endif %}
