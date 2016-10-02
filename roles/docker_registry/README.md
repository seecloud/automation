docker_registry
=========

Deployment of docker private registry with TLS support

Requirements
------------

Ubuntu 14.04 with Ansible >= 2.1 and Docker >= 1.12.1

Role Variables
--------------

- registry_certs_path - generated keys location
- container_address - docker registry name + port
- key_length
- key_name
- valid_time
- company_name
- company_country
- registry_role - possible values: 'server' or 'client'
- docker_registry_tar - path to the registry.tar docker image (default is files)
- docker_custom_tars_path - path with  all images tars, which will be pushed into registry (default is files/custom)

Dependencies
------------

- common
- keepalived (for registry_role 'server')

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: 192.168.122.3
        roles:
          - { role: docker_registry, registry_role: "server"}

    - hosts: test
        roles:
            - { role: docker_registry, registry_role: "client"}

* test - group with all environment nodes

License
-------

BSD

Author Information
------------------

Mirantis
