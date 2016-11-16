#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
inventory_generator
~~~~~~~~~~~~~~~~~~~

Ansible inventory generator for seecloud automation,
based on Kargo inventory generator
"""

import argparse
import random
import re
import string
import sys

import ansible.utils.display as display
import requests

display = display.Display()

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_cluster_name():
    try:
        word_site = ("http://svnweb.freebsd.org/csrg/share/dict/"
                     "words?view=co&content-type=text/plain")
        response = requests.get(word_site)
        words = response.content.splitlines()
        cluster_name = random.choice(words).decode("utf-8")
    except Exception:
        cluster_name = id_generator()
    if not re.match('^(?:[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?)$', cluster_name):
        get_cluster_name()
    return(cluster_name.lower())


class CfgInventory(object):
    '''Read classic ansible inventory file.'''

    def __init__(self, options, platform):
        self.options = options
        self.platform = platform
        self.inventorycfg = options['inventory_path']
        self.cparser = configparser.ConfigParser(allow_no_value=True)
        self.inventory = {'all': {'hosts': []},
                          'kube-master': {'hosts': []},
                          'etcd': {'hosts': []},
                          'elasticsearch_nodes': {'hosts': []},
                          'glusterfs_nodes': {'hosts': []},
                          'keepalived_nodes': {'hosts': []},
                          'kube-node': {'hosts': []},
                          'k8s-cluster:children': {'hosts': [
                              {'hostname': 'kube-node', 'hostvars': []},
                              {'hostname': 'kube-master', 'hostvars': []}
                          ]},
                          }

    def format_inventory(self, masters, nodes, etcds,
                         elastics, glusters, keepaliveds):
        new_inventory = {'all': {'hosts': []},
                         'kube-master': {'hosts': []},
                         'etcd': {'hosts': []},
                         'elasticsearch_nodes': {'hosts': []},
                         'glusterfs_nodes': {'hosts': []},
                         'keepalived_nodes': {'hosts': []},
                         'kube-node': {'hosts': []},
                         'k8s-cluster:children': {'hosts': [
                             {'hostname': 'kube-node', 'hostvars': []},
                             {'hostname': 'kube-master', 'hostvars': []}
                             ]},
                         }
        hostnames = {}

        if self.platform == 'openstack':
            if self.options['floating_ip']:
                ip_type = 'public_v4'
            else:
                ip_type = 'private_v4'
            # handle masters
            new_instances = []
            for master in masters:
                new_instances.append({'public_ip': (master['openstack']
                                                    [ip_type]),
                                      'name': master['item']})
            masters = new_instances
            # handle nodes
            new_instances = []
            for node in nodes:
                new_instances.append({'public_ip': node['openstack'][ip_type],
                                      'name': node['item']})
            nodes = new_instances
            # handle etcds
            new_instances = []
            for etcd in etcds:
                new_instances.append({'public_ip': etcd['openstack'][ip_type],
                                      'name': etcd['item']})
            etcds = new_instances
            # handle elastics
            new_instances = []
            for elastic in elastics:
                new_instances.append({'public_ip': (elastic['openstack']
                                                    [ip_type]),
                                      'name': elastic['item']})
            elastics = new_instances
            # handle glusterfs
            new_instances = []
            for gluster in glusters:
                new_instances.append({'public_ip': (gluster['openstack']
                                                    [ip_type]),
                                      'name': gluster['item']})
            glusters = new_instances
            # handle keepaliveds
            new_instances = []
            for keepalived in keepaliveds:
                new_instances.append({'public_ip': (keepalived['openstack']
                                                    [ip_type]),
                                      'name': keepalived['item']})
            keepaliveds = new_instances

        if not self.options['add_node']:
            if not masters and len(nodes) == 1:
                masters = [nodes[0]]
            elif not masters:
                masters = nodes[0:2]
            if not etcds and len(nodes) >= 3:
                etcds = nodes[0:3]
            elif not etcds and len(nodes) < 3:
                etcds = [nodes[0]]
            elif etcds and len(etcds) < 3:
                etcds = [etcds[0]]
            if not elastics and len(nodes) >= 3:
                elastics = nodes[0:3]
            elif not elastics and len(nodes) < 3:
                elastics = [nodes[0]]
            elif elastics and len(elastics) < 3:
                elastics = [elastics[0]]
            if not glusters and len(nodes) >= 3:
                glusters = nodes[0:3]
            elif not glusters and len(nodes) < 3:
                glusters = [nodes[0]]
            elif glusters and len(glusters) < 3:
                glusters = [glusters[0]]
            if not keepaliveds and len(nodes) >= 2:
                keepaliveds = nodes[0:2]
            elif not keepaliveds and len(nodes) < 2:
                keepaliveds = [nodes[0]]
            elif keepaliveds and len(keepaliveds) < 2:
                keepaliveds = [keepaliveds[0]]

        if self.platform is 'openstack':
            if self.options['add_node']:
                current_inventory = self.read_inventory()
                cluster_name = '-'.join(
                    (current_inventory['all']['hosts']
                     [0]['hostname']).split('-')[:-1]
                )
                new_inventory = current_inventory
            else:
                cluster_name = 'k8s-' + get_cluster_name()
            if self.options['use_private_ip']:
                instance_ip = 'private_ip'
            else:
                instance_ip = 'public_ip'
            for host in (nodes + masters + etcds +
                         elastics + glusters + keepaliveds):
                new_inventory['all']['hosts'].append(
                    {'hostname': '%s' % host['name'], 'hostvars': [
                        {'name': 'ansible_ssh_host',
                         'value': host[instance_ip]}
                        ]}
                )
            if not self.options['add_node']:
                for host in nodes:
                    new_inventory['kube-node']['hosts'].append(
                        {'hostname': '%s' % host['name'],
                         'hostvars': []}
                    )
                for host in masters:
                    new_inventory['kube-master']['hosts'].append(
                        {'hostname': '%s' % host['name'],
                         'hostvars': []}
                    )
                for host in etcds:
                    new_inventory['etcd']['hosts'].append(
                        {'hostname': '%s' % host['name'],
                         'hostvars': []}
                    )
                for host in elastics:
                    new_inventory['elasticsearch_nodes']['hosts'].append(
                        {'hostname': '%s' % host['name'],
                         'hostvars': []}
                    )
                for host in glusters:
                    new_inventory['glusterfs_nodes']['hosts'].append(
                        {'hostname': '%s' % host['name'],
                         'hostvars': []}
                    )
                for host in keepaliveds:
                    new_inventory['keepalived_nodes']['hosts'].append(
                        {'hostname': '%s' % host['name'],
                         'hostvars': []}
                    )
        elif self.platform == 'metal':
            for host in (nodes + masters + etcds +
                         elastics + glusters + keepaliveds):
                if '[' in host:
                    r = re.search('(^.*)\[(.*)\]', host)
                    inventory_hostname = r.group(1)
                    var_str = r.group(2)
                    hostvars = list()
                    for var in var_str.split(','):
                        hostvars.append({'name': var.split('=')[0],
                                         'value': var.split('=')[1]})
                else:
                    inventory_hostname = host
                    hostvars = []

                if inventory_hostname not in hostnames.keys():
                    hostnames[inventory_hostname] = hostvars
                elif hostvars != hostnames[inventory_hostname]:
                    hostnames[inventory_hostname] = hostvars + hostnames[inventory_hostname]

            for host, hostvars in hostnames.iteritems():
                    new_inventory['all']['hosts'].append(
                        {'hostname': host, 'hostvars': hostvars}
                    )
            for host in nodes:
                new_inventory['kube-node']['hosts'].append(
                    {'hostname': host.split('[')[0], 'hostvars': []}
                )
            for host in masters:
                new_inventory['kube-master']['hosts'].append(
                    {'hostname': host.split('[')[0], 'hostvars': []}
                )
            for host in etcds:
                new_inventory['etcd']['hosts'].append(
                    {'hostname': host.split('[')[0], 'hostvars': []}
                )
            for host in elastics:
                new_inventory['elasticsearch_nodes']['hosts'].append(
                    {'hostname': host.split('[')[0], 'hostvars': []}
                )
            for host in glusters:
                new_inventory['glusterfs_nodes']['hosts'].append(
                    {'hostname': host.split('[')[0], 'hostvars': []}
                )
            for host in keepaliveds:
                new_inventory['keepalived_nodes']['hosts'].append(
                    {'hostname': host.split('[')[0], 'hostvars': []}
                )
        return(new_inventory)

    def write_inventory(self, masters, nodes, etcds,
                        elastics, glusters, keepaliveds):
        '''Generates inventory.'''
        failed = False
        inventory = self.format_inventory(masters, nodes, etcds,
                                          elastics, glusters, keepaliveds)
        if not self.options['add_node']:
            if (('masters_list' in self.options.keys() and len(masters) < 2) or
               ('masters_list' not in self.options.keys() and len(nodes) < 2)):
                display.error('You should set at least 2 masters')
                failed = True
            if (('etcds_list' in self.options.keys() and len(etcds) < 3) or
               ('etcds_list' not in self.options.keys() and len(nodes) < 3)):
                display.error(('You should set at least 3'
                               ' nodes for etcd clustering'))
                failed = True
            if (('elastics_list' in self.options.keys()
                and len(elastics) < 3) or
               ('elastics_list' not in self.options.keys()
               and len(nodes) < 3)):
                display.error(('You should set at least 3'
                               ' nodes for elasticsearch'))
                failed = True
            if (('glusters_list' in self.options.keys()
                and len(glusters) < 3) or
               ('glusters_list' not in self.options.keys()
               and len(nodes) < 3)):
                display.error(('You should set at least 3'
                               ' nodes for glusterfs cluster'))
                failed = True
            if (('keepaliveds_list' in self.options.keys()
                and len(keepaliveds) < 2) or
               ('keepaliveds_list' not in self.options.keys()
               and len(nodes) < 2)):
                display.error('You should set at least 2 nodes for keepalived')
                failed = True
        if failed and not self.options['force']:
            sys.exit(1)
        open(self.inventorycfg, 'w').close()
        for key, value in inventory.items():
            self.cparser.add_section(key)
            for host in value['hosts']:
                hostvars = str()
                varlist = list()
                for var in host['hostvars']:
                    varlist.append("%s=%s" % (var['name'], var['value']))
                hostvars = " ".join(varlist)
                self.cparser.set(key, "%s\t\t%s" % (host['hostname'], hostvars))
        with open(self.inventorycfg, 'wb') as configfile:
            display.banner('WRITTING INVENTORY')
            self.cparser.write(configfile)
            display.display(
                'Inventory generated : %s'
                % self.inventorycfg, color='green'
            )


def prepare(options):
    if options['is_openstack']:
        platform = 'openstack'
    else:
        platform = 'metal'
    Cfg = CfgInventory(options, platform)
    Cfg.write_inventory(
        options['masters_list'],
        options['nodes_list'],
        options['etcds_list'],
        options['elastics_list'],
        options['glusters_list'],
        options['keepaliveds_list']
    )
if __name__ == "__main__":
    # Main parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', '--inventory', dest='inventory_path', required=True,
        help=('Inventory file path. Defaults to '
              '<path parameter>/inventory.cfg')
    )
    parser.add_argument(
        '-o', '--openstack', dest='is_openstack', action='store_true',
        help=''
    )
    parser.add_argument(
        '-f', '--force', dest='force', action='store_true',
        help='Ignores errors with count of nodes while creating inventory'
    )
    parser.add_argument(
        '--add', dest='add_node', action='store_true',
        help="Add node to an existing cluster"
    )
    parser.add_argument(
        '--etcds', dest='etcds_list', metavar='N', nargs='+', default=[],
        help='Number of etcd, these instances will just act as etcd members'
    )
    parser.add_argument(
        '--masters', dest='masters_list', metavar='N', nargs='+', default=[],
        help=('Number of masters, these instances will not '
              'run workloads, master components only')
    )
    parser.add_argument(
        '--nodes', dest='nodes_list', metavar='N', nargs='+',
        required=True, help='List of nodes'
    )
    parser.add_argument(
        '--elastics', dest='elastics_list', metavar='N', nargs='+', default=[],
        help='Number of elastic search nodes'
    )
    parser.add_argument(
        '--keepaliveds', dest='keepaliveds_list', metavar='N',
        nargs='+', default=[], help='Number of keepalived nodes'
    )
    parser.add_argument(
        '--glusters', dest='glusters_list', metavar='N', nargs='+', default=[],
        help='Number of glusters nodes'
    )

    # Parse arguments
    args = parser.parse_args()
    if args.inventory_path is None:
        args.configfile = 'inventory.cfg'
    prepare(vars(args))
