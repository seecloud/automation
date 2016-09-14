#!/bin/bash

# This script is running on keepalived events
# For master state it deploys registry
# For backup and fail states - ignore

#!/bin/bash

ENDSTATE=$1

case $ENDSTATE in
    "BACKUP") # Perform action for transition to BACKUP state
              exit 0
              ;;
    "FAULT")  # Perform action for transition to FAULT state
              exit 0
              ;;
    "MASTER") # Perform action for transition to MASTER state
			  logger Deploying docker private registry
              ANSIBLE_HOST_KEY_CHECKING=False /usr/bin/ansible-playbook -i /opt/ansible/docker_private_registry/inventory /opt/ansible/docker_private_registry/notify_runner.yml
              ;;
    *)        echo "Unknown state ${ENDSTATE} for VRRP ${TYPE} ${NAME}"
              exit 1
              ;;
esac