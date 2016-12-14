# Automated deployment of the OSS infrastructure
*Kubernetes deployment based on the roles, taken from [Kargo project](https://github.com/kubernetes-incubator/kargo)  
#### Requirements for deployment node
1. CentOS 7 / Ubuntu 16.04
2. Packages installed: python-pip, python-netaddr
#### Requirements for target nodes
1. CentOS7 nodes, installed from iso, which was builded by [OSS image builder](https://github.com/seecloud/os-image-builder)  
2. Access to nodes via ssh key for root user
3. Proper resolving by hostname on the machine, which you are using for deployment
4. Ansible, docker-py

#### How to deploy
1. Generate inventory file (minimum required nodes - 3):
```
utils/inventory-generator --nodes node1 node2 node3
```
2. Run bootstrap playbook for loading required packages (required internet connection)
```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory/bootstrap.cfg bootstrap-runner.yml
```
3. Run playbook (doesn't require internet connection)
```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory/automation.cfg automation-runner.yml
```

#### Overriding default options

You can override some default settings. For example:
- build_oss_images=false - skip building of oss images on CCP
- deploy_oss_images=false - skip deployment of oss images on CCP
- keepalived_ip=10.1.1.8 - specify virtual ip for docker private registry (it is generated automatically by default)

To apply this options - execute ansible-playbook with --extra-vars:
```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory/automation.cfg automation-runner.yml --extra-vars "keepalived_ip=10.1.1.8 build_oss_images=false"