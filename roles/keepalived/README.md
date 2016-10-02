keepalived
=========

Configure keepalived in MASTER/BACKUP state

Requirements
------------

Keepalived installed or binary with dependencies placed in proper folder

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

None

Example Playbook
----------------

How to use:

	---
	- hosts: 192.168.122.3
	  roles:
	     - { role: keepalived, keepalived_state: "master" }

	- hosts: 192.168.122.4
	  roles:
	     - { role: keepalived, keepalived_state: "backup" }


License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
