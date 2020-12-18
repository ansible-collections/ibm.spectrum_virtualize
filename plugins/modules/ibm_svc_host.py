#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: ibm_svc_host
short_description: This module manages hosts on IBM Spectrum Virtualize
                   Family storage systems.
version_added: "2.10"

description:
  - Ansible interface to manage 'mkhost' and 'rmhost' host commands.

options:
    name:
        description:
            - Specifies a name or label for the new host object
        required: true
        type: str
    state:
        description:
            - Creates (C(present)) or removes (C(absent)) a host
        choices: [ absent, present ]
        required: true
        type: str
    clustername:
        description:
            - The hostname or management IP of the
              Spectrum Virtualize storage system
        type: str
        required: true
    domain:
        description:
            - Domain for the Spectrum Virtualize storage system
        type: str
    username:
        description:
            - REST API username for the Spectrum Virtualize storage system
        required: true
        type: str
    password:
        description:
            - REST API password for the Spectrum Virtualize storage system
        required: true
        type: str
    fcwwpn:
        description:
            - List of Initiator WWPNs to be added to the host. The complete list of WWPNs must be provided.
        required: false
        type: str
    iscsiname:
        description:
            - Initiator IQN to be added to the host
        required: false
        type: str
    iogrp:
        description:
            - Specifies a set of one or more input/output (I/O)
              groups from which the host can access the volumes
        default: '0:1:2:3'
        required: false
        type: str
    protocol:
        description:
            - Specifies the protocol used by the host to
              communicate with the storage system
        default: 'scsi'
        type: str
        required: false
        choices: [ "scsi", "nvme" ]
    type:
        description:
            - Specifies the type of host
        default:
        required: false
        type: str
    log_path:
        description:
            - Path of debug log file
        type: str
    validate_certs:
        description:
            - Validates certification
        type: bool
author:
    - Sreshtant Bohidar (@Sreshtant-Bohidar)
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to create an iSCSI host
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Define a new iSCSI host
      ibm_svc_host:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: host4test
        state: present
        iscsiname: iqn.1994-05.com.redhat:2e358e438b8a
        iogrp: 0:1:2:3
        protocol: scsi
        type: generic

- name: Using the IBM Spectrum Virtualize collection to create an FC host
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Define a new FC host
      ibm_svc_host:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: host4test
        state: present
        fcwwpn: 100000109B570216:1000001AA0570266
        iogrp: 0:1:2:3
        protocol: scsi
        type: generic

- name: Using the IBM Spectrum Virtualize collection to delete a host
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete host
      ibm_svc_host:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: host4test
        state: absent
'''

RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVChost(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                fcwwpn=dict(type='str', required=False),
                iscsiname=dict(type='str', required=False),
                iogrp=dict(type='str', required=False, default='0:1:2:3'),
                protocol=dict(type='str', required=False,
                              default='scsi',
                              choices=['scsi', 'nvme']),
                type=dict(type='str')
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Optional
        self.fcwwpn = self.module.params.get('fcwwpn', '')
        self.iscsiname = self.module.params.get('iscsiname', '')
        self.iogrp = self.module.params.get('iogrp', '')
        self.protocol = self.module.params.get('protocol', '')
        self.type = self.module.params.get('type', '')

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def get_existing_host(self):
        merged_result = {}

        data = self.restapi.svc_obj_info(cmd='lshost', cmdopts=None,
                                         cmdargs=[self.name])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    # TBD: Implement a more generic way to check for properties to modify.
    def host_probe(self, data):
        props = []
        # TBD: The parameter is fcwwpn but the view has fcwwpn label.
        if self.type:
            if self.type != data['type']:
                props += ['type']

        if self.fcwwpn:
            self.existing_fcwwpn = [node["WWPN"] for node in data['nodes'] if "WWPN" in node]
            self.input_fcwwpn = self.fcwwpn.split(":")
            if set(self.existing_fcwwpn).symmetric_difference(set(self.input_fcwwpn)):
                props += ['fcwwpn']

        if props is []:
            props = None

        self.log("host_probe props='%s'", data)
        return props

    def host_create(self):
        if self.module.check_mode:
            self.changed = True
            return

        if (not self.fcwwpn) and (not self.iscsiname):
            self.module.fail_json(msg="You must pass in fcwwpn or iscsiname "
                                      "to the module.")
        if self.fcwwpn and self.iscsiname:
            self.module.fail_json(msg="You must not pass in both fcwwpn and "
                                      "iscsiname to the module.")

        if not self.protocol:
            self.module.fail_json(msg="You must pass in protocol "
                                      "to the module.")

        self.log("creating host '%s'", self.name)

        # Make command
        cmd = 'mkhost'
        cmdopts = {'name': self.name, 'force': True}
        if self.fcwwpn:
            cmdopts['fcwwpn'] = self.fcwwpn
        elif self.iscsiname:
            cmdopts['iscsiname'] = self.iscsiname

        if self.protocol:
            cmdopts['protocol'] = self.protocol
        if self.iogrp:
            cmdopts['iogrp'] = self.iogrp
        if self.type:
            cmdopts['type'] = self.type

        self.log("creating host command '%s' opts '%s'",
                 self.fcwwpn, self.type)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("create host result '%s'", result)

        if 'message' in result:
            self.changed = True
            self.log("create host result message '%s'", (result['message']))
        else:
            self.module.fail_json(
                msg="Failed to create host [%s]" % self.name)

    def host_fcwwpn_update(self):
        to_be_removed = ':'.join(list(set(self.existing_fcwwpn) - set(self.input_fcwwpn)))
        if to_be_removed:
            self.restapi.svc_run_command(
                'rmhostport',
                {'fcwwpn': to_be_removed, 'force': True},
                [self.name]
            )
            self.log('%s removed from %s', to_be_removed, self.name)
        to_be_added = ':'.join(list(set(self.input_fcwwpn) - set(self.existing_fcwwpn)))
        if to_be_added:
            self.restapi.svc_run_command(
                'addhostport',
                {'fcwwpn': to_be_added, 'force': True},
                [self.name]
            )
            self.log('%s added to %s', to_be_added, self.name)

    def host_update(self, modify):
        # update the host
        self.log("updating host '%s'", self.name)
        # TBD: Be smarter handling many properties.
        if 'fcwwpn' in modify:
            self.host_fcwwpn_update()
            self.changed = True
            self.log("fcwwpn of %s updated", self.name)
        if 'type' in modify:
            cmd = 'chhost'
            cmdopts = {}
            cmdopts['type'] = self.type
            cmdargs = [self.name]
            self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
            # Any error will have been raised in svc_run_command
            # chhost does not output anything when successful.
            self.changed = True
            self.log("type of %s updated", self.name)

    def host_delete(self):
        self.log("deleting host '%s'", self.name)

        cmd = 'rmhost'
        cmdopts = None
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chhost does not output anything when successful.
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = []

        host_data = self.get_existing_host()

        if host_data:
            if self.state == 'absent':
                self.log("CHANGED: host exists, but requested "
                         "state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chhost should be called
                modify = self.host_probe(host_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: host does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not host_data:
                        self.host_create()
                        msg = "host %s has been created." % self.name
                    else:
                        # This is where we would modify
                        self.host_update(modify)
                        msg = "host [%s] has been modified." % self.name
                elif self.state == 'absent':
                    self.host_delete()
                    msg = "host [%s] has been deleted." % self.name
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "host [%s] did not exist." % self.name
            else:
                msg = "host [%s] already exists." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVChost()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
