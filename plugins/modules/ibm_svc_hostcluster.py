#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_svc_hostcluster
short_description: This module manages host cluster on IBM Spectrum Virtualize family storage systems
version_added: "1.5.0"
description:
  - Ansible interface to manage 'mkhostcluster', 'chhostcluster' and 'rmhostcluster' host commands.
options:
    name:
        description:
            - Specifies a name or label for the new host cluster object.
        required: true
        type: str
    state:
        description:
            - Creates (C(present)) or removes (C(absent)) a host cluster.
        choices: [ absent, present ]
        required: true
        type: str
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
    ownershipgroup:
        description:
            - The name of the ownership group to which the host cluster object is being added.
            - Parameters I(ownershipgroup) and I(noownershipgroup) are mutually exclusive.
            - Applies when I(state=present).
        type: str
        version_added: '1.6.0'
    noownershipgroup:
        description:
            - If specified True, the host cluster object is removed from the ownership group to which it belongs.
            - Parameters I(ownershipgroup) and I(noownershipgroup) are mutually exclusive.
            - Applies when I(state=present) to modify an existing hostcluster.
        type: bool
        version_added: '1.6.0'
    removeallhosts:
        description:
            - Specifies that all hosts in the host cluster and the associated host cluster object be deleted.
            - Applies when I(state=absent).
        type: bool
    log_path:
        description:
            - Path of debug log file.
        type: str
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
author:
    - Shilpi Jain (@Shilpi-J)
notes:
    - This module supports C(check_mode).
'''

EXAMPLES = '''
- name: Define a new host cluster
  ibm.spectrum_virtualize.ibm_svc_hostcluster:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: present
    ownershipgroup: group1
- name: Update the ownershipgroup of a host cluster
  ibm.spectrum_virtualize.ibm_svc_hostcluster:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: present
    noownershipgroup: True
- name: Delete a host cluster
  ibm.spectrum_virtualize.ibm_svc_hostcluster:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: absent
    removeallhosts: True
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVChostcluster(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                ownershipgroup=dict(type='str'),
                noownershipgroup=dict(type='bool'),
                removeallhosts=dict(type='bool')
            )
        )

        self.changed = ""

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
        self.ownershipgroup = self.module.params.get('ownershipgroup', '')
        self.noownershipgroup = self.module.params.get('noownershipgroup', '')
        self.removeallhosts = self.module.params.get('removeallhosts', '')

        # Handling missing mandatory parameter name
        if not self.name:
            self.module.fail_json(msg='Missing mandatory parameter: name')

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path,
            token=self.module.params['token']
        )

    def get_existing_hostcluster(self):
        merged_result = {}

        data = self.restapi.svc_obj_info(cmd='lshostcluster', cmdopts=None,
                                         cmdargs=[self.name])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    def hostcluster_probe(self, data):
        props = []
        if self.removeallhosts:
            self.module.fail_json(msg="Parameter 'removeallhosts' can be used only while deleting hostcluster")

        if self.ownershipgroup and self.noownershipgroup:
            self.module.fail_json(msg="You must not pass in both 'ownershipgroup' and "
                                      "'noownershipgroup' to the module.")

        if data['owner_name'] and self.noownershipgroup:
            props += ['noownershipgroup']

        if self.ownershipgroup and (not data['owner_name'] or self.ownershipgroup != data['owner_name']):
            props += ['ownershipgroup']

        if props is []:
            props = None

        self.log("hostcluster_probe props='%s'", data)
        return props

    def hostcluster_create(self):
        if self.removeallhosts:
            self.module.fail_json(msg="Parameter 'removeallhosts' cannot be passed while creating hostcluster")

        if self.module.check_mode:
            self.changed = True
            return

        # Make command
        cmd = 'mkhostcluster'
        cmdopts = {'name': self.name}

        if self.ownershipgroup:
            cmdopts['ownershipgroup'] = self.ownershipgroup

        self.log("creating host cluster command opts '%s'",
                 self.ownershipgroup)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("create host cluster result '%s'", result)

        if 'message' in result:
            self.changed = True
            self.log("create host cluster result message '%s'", (result['message']))
        else:
            self.module.fail_json(
                msg="Failed to create host cluster [%s]" % self.name)

    def hostcluster_update(self, modify):
        if self.module.check_mode:
            self.changed = True
            return

        self.log("updating host cluster '%s'", self.name)
        cmd = 'chhostcluster'
        cmdopts = {}
        if 'ownershipgroup' in modify:
            cmdopts['ownershipgroup'] = self.ownershipgroup
        elif 'noownershipgroup' in modify:
            cmdopts['noownershipgroup'] = self.noownershipgroup

        if cmdopts:
            cmdargs = [self.name]
            self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
            # Any error will have been raised in svc_run_command
            # chhost does not output anything when successful.
            self.changed = True
            self.log("Properties of %s updated", self.name)

    def hostcluster_delete(self):
        if self.module.check_mode:
            self.changed = True
            return

        self.log("deleting host cluster '%s'", self.name)

        cmd = 'rmhostcluster'
        cmdopts = {}
        cmdargs = [self.name]

        if self.removeallhosts:
            cmdopts = {'force': True}
            cmdopts['removeallhosts'] = self.removeallhosts

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chhost does not output anything when successful.
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = []

        hc_data = self.get_existing_hostcluster()

        if hc_data:
            if self.state == 'absent':
                self.log("CHANGED: host cluster exists, but requested "
                         "state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chhostcluster should be called
                modify = self.hostcluster_probe(hc_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: host cluster does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.state == 'present':
                if not hc_data:
                    self.hostcluster_create()
                    msg = "host cluster %s has been created." % self.name
                else:
                    # This is where we would modify
                    self.hostcluster_update(modify)
                    msg = "host cluster [%s] has been modified." % self.name
            elif self.state == 'absent':
                self.hostcluster_delete()
                msg = "host cluster [%s] has been deleted." % self.name

            if self.module.check_mode:
                msg = "skipping changes due to check mode"
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "host cluster [%s] did not exist." % self.name
            else:
                msg = "host cluster [%s] already exists. No modifications done." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVChostcluster()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
