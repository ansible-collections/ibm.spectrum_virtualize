#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_svc_manage_portset
short_description: This module manages portset configuration on IBM Spectrum Virtualize family storage systems
version_added: "1.8.0"
description:
  - Ansible interface to manage IP portsets 'mkportset', 'chportset' and 'rmportset' commands.
options:
    clustername:
        description:
            - The hostname or management IP of the Spectrum Virtualize storage system.
        required: true
        type: str
    domain:
        description:
            - Domain for the Spectrum Virtualize storage system.
            - Valid when hostname is used for the parameter I(clustername).
        type: str
    username:
        description:
            - REST API username for the Spectrum Virtualize storage system.
            - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
        type: str
    password:
        description:
            - REST API password for the Spectrum Virtualize storage system.
            - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
        type: str
    token:
        description:
            - The authentication token to verify a user on the Spectrum Virtualize storage system.
            - To generate a token, use the M(ibm.spectrum_virtualize.ibm_svc_auth) module.
        type: str
    log_path:
        description:
            - Path of debug log file.
        type: str
    state:
        description:
            - Creates (C(present)) or Deletes (C(absent)) the IP portset.
        choices: [ present, absent ]
        required: true
        type: str
    name:
        description:
            - Specifies the name of portset.
        type: str
        required: true
    portset_type:
        description:
            - Specifies the type for the portset.
            - Applies only during creation of portset.
        choices: [ host, replication ]
        default: host
        type: str
    ownershipgroup:
        description:
            - The name of the ownership group to which the portset object is being mapped.
            - Parameters I(ownershipgroup) and I(noownershipgroup) are mutually exclusive.
            - Applies when I(state=present).
        type: str
    noownershipgroup:
        description:
            - Specify to remove the ownership group from portset.
            - Parameters I(ownershipgroup) and I(noownershipgroup) are mutually exclusive.
            - Applies only during updation of portset.
        type: bool
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
author:
    - Sanjaikumaar M (@sanjaikumaar)
notes:
    - This module supports C(check_mode).
'''

EXAMPLES = '''
- name: Create a portset
  ibm.spectrum_virtualize.ibm_svc_manage_portset:
   clustername: "{{cluster}}"
   username: "{{username}}"
   password: "{{password}}"
   name: portset1
   portset_type: host
   ownershipgroup: owner1
   state: present
- name: Update a portset
  ibm.spectrum_virtualize.ibm_svc_manage_portset:
   clustername: "{{cluster}}"
   username: "{{username}}"
   password: "{{password}}"
   name: portset1
   noownershipgroup: true
   state: present
- name: Delete a portset
  ibm.spectrum_virtualize.ibm_svc_manage_portset:
   clustername: "{{cluster}}"
   username: "{{username}}"
   password: "{{password}}"
   name: portset1
   state: absent
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import (
    IBMSVCRestApi, svc_argument_spec,
    get_logger
)
from ansible.module_utils._text import to_native


class IBMSVCPortset:

    def __init__(self):
        argument_spec = svc_argument_spec()
        argument_spec.update(
            dict(
                state=dict(
                    type='str',
                    required=True,
                    choices=['present', 'absent']
                ),
                name=dict(
                    type='str',
                    required=True,
                ),
                portset_type=dict(
                    type='str',
                    default='host',
                    choices=['host', 'replication']
                ),
                ownershipgroup=dict(
                    type='str',
                ),
                noownershipgroup=dict(
                    type='bool',
                )
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # Required parameters
        self.name = self.module.params['name']
        self.state = self.module.params['state']
        # Optional parameters
        self.portset_type = self.module.params.get('portset_type', '')
        self.ownershipgroup = self.module.params.get('ownershipgroup', '')
        self.noownershipgroup = self.module.params.get('noownershipgroup', '')

        self.basic_checks()

        # Varialbe to cache data
        self.portset_details = None

        # logging setup
        self.log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, self.log_path)
        self.log = log.info
        self.changed = False
        self.msg = ''

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=self.log_path,
            token=self.module.params['token']
        )

    def basic_checks(self):
        if self.state == 'present':
            if not self.name:
                self.module.fail_json(msg='Missing mandatory parameter: name')

            if self.ownershipgroup and self.noownershipgroup:
                self.module.fail_json(msg='Mutually exclusive parameter: ownershipgroup, noownershipgroup')
        else:
            fields = [f for f in ['ownershipgroup', 'noownershipgroup'] if getattr(self, f)]

            if any(fields):
                self.module.fail_json(msg='{0} should not be passed when state=absent'.format(', '.join(fields)))

    def is_portset_exists(self):
        merged_result = {}
        data = self.restapi.svc_obj_info(
            cmd='lsportset',
            cmdopts=None,
            cmdargs=[self.name]
        )

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        self.portset_details = merged_result

        return merged_result

    def create_portset(self):
        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'mkportset'
        cmdopts = {
            'name': self.name,
            'type': self.portset_type if self.portset_type else 'host'
        }

        if self.ownershipgroup:
            cmdopts['ownershipgroup'] = self.ownershipgroup

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log('Portset (%s) created', self.name)
        self.changed = True

    def portset_probe(self):
        updates = []

        if self.ownershipgroup and self.ownershipgroup != self.portset_details['owner_name']:
            updates.append('ownershipgroup')
        if self.noownershipgroup:
            updates.append('noownershipgroup')

        self.log("Modifications to be done: %s", updates)

        return updates

    def update_portset(self, updates):
        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'chportset'
        cmdopts = dict((k, getattr(self, k)) for k in updates)
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts=cmdopts, cmdargs=cmdargs)
        self.log('Portset (%s) updated', self.name)
        self.changed = True

    def delete_portset(self):
        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'rmportset'
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts=None, cmdargs=cmdargs)
        self.log('Portset (%s) deleted', self.name)
        self.changed = True

    def apply(self):
        if self.is_portset_exists():
            if self.state == 'present':
                modifications = self.portset_probe()
                if any(modifications):
                    self.update_portset(modifications)
                    self.msg = 'Portset ({0}) updated.'.format(self.name)
                else:
                    self.msg = 'Portset ({0}) already exists. No modifications done.'.format(self.name)
            else:
                self.delete_portset()
                self.msg = 'Portset ({0}) deleted.'.format(self.name)
        else:
            if self.state == 'absent':
                self.msg = 'Portset ({0}) does not exist. No modifications done.'.format(self.name)
            else:
                self.create_portset()
                self.msg = 'Portset ({0}) created.'.format(self.name)

        if self.module.check_mode:
            self.msg = 'skipping changes due to check mode.'

        self.module.exit_json(
            changed=self.changed,
            msg=self.msg
        )


def main():
    v = IBMSVCPortset()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
