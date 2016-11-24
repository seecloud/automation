# Automated deployment of the OSS infrastructure
*Kubernetes deployment based on the roles, taken from [Kargo project](https://github.com/kubernetes-incubator/kargo)  
#### Requirements
1. CentOS7 nodes, installed from iso, which was builded by [OSS image builder](https://github.com/seecloud/os-image-builder)  
1. Access to nodes via ssh key for root user
2. Proper resolving by hostname on the machine, which you are using for deployment

#### How to deploy
1. Generate inventory file (minimum required nodes - 3):
```
utils/inventory-generator --nodes node1 node2 node3
```
2. Run bootstrap playbook for loading required packages (required internet connection)
```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory/bootstrap.cfg bootstrap.yml
```
3. Configure network settings for private registry in automation.yml
```
docker_registry_ip: "192.168.122.250" # virtual ip (use free address in you environment network)
```
4. Run playbook (doesn't require internet connection)
```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory/automation.cfg automation-runner.yml
```