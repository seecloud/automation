common
=========

Installs required packages for docker private registry, creates required folders

Requirements
------------

Ubuntu 14.04

Role Variables
--------------

- docker_registry_name - hostname for private registry (used to resolve into docker_registry_ip)
- docker_registry_ip - virtual ip address, used for keepalived and registry access
- msa_files_src - source folder for ansible playbooks, which will be copied to all nodes
- msa_files_dest - destination folder for ansible playbooks

Dependencies
------------

None

Example Playbook
----------------

    - hosts: test
      roles:
          - common
* test - group of hosts, descirbed in the inventory file

License
-------

BSD

Author Information
------------------

Mirantis
