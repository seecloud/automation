# Docker private registry
#### Requirements
1. Access to nodes via ssh key for root user
2. Proper resolving by hostname on the machine, which you are using for deployment

#### How to deploy
0. Configure network settings for your registry (roles/common/defaults/main.yml)
```
docker_registry_name: "registry" # hostname for access 
docker_registry_ip: "192.168.122.250" # virtual ip (should be in the proper network)
```
1. Add to inventory file under [all] section list with hostnames  
Example:
```
    [all]  
    pr1  
    pr2  
    pr3  
    
    [all:vars]
    ansible_user="root"
```
2. Edit init_runner.yml with proper roles for keepalived/registry  
Example
```
---
- hosts: all
  roles:
      - common

- hosts: pr1
  roles:
     - { role: keepalived, keepalived_state: "master" }

- hosts: pr2
  roles:
     - { role: keepalived, keepalived_state: "backup" }

- hosts: pr1
  roles:
      - { role: docker_registry, registry_role: "server"}

- hosts: all
  roles:
      - { role: docker_registry, registry_role: "client"}


```
3. Edit notify_runner.yml (this one is called during failover) with proper settings for docker registry server/clients
Example
```
---
- hosts: localhost
  connection: local
  roles:
      - { role: docker_registry, registry_role: "server"}

- hosts: all
  roles:
      - { role: docker_registry, registry_role: "client"}
```

After deployment you can use registry in this way:
```
docker pull registry:5000/elasticsearch
```