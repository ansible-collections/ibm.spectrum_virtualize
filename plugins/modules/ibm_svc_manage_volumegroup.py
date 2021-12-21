#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: ibm_svc_manage_volumegroup
short_description: This module manages volume groups on IBM Spectrum Virtualize family storage systems
version_added: "1.6.0"
description:
  - Ansible interface to manage 'mkvolumegroup', 'chvolumegroup', and 'rmvolumegroup'
    commands.
options:
    name:
        description:
            - Specifies the name for the volume group.
        required: true
        type: str
    state:
        description:
            - Creates or updates (C(present)) or removes (C(absent)) a volume group.
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
            - To generate a token, use the ibm_svc_auth module.
        type: str
    log_path:
        description:
            - Path of debug log file.
        type: str
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
    ownershipgroup:
        description:
            - The name of the ownership group to which the object is being added.
            - I(ownershipgroup) is mutually exclusive with parameters I(safeguardpolicyname) and I(noownershipgroup).
            - Applies when C(state=present).
        type: str
    noownershipgroup:
        description:
            - If specified True, the object is removed from the ownership group to which it belongs.
            - Parameters I(ownershipgroup) and I(noownershipgroup) are mutually exclusive.
            - Applies when C(state=present).
        type: bool
    safeguardpolicyname:
        description:
            - The name of the Safeguarded policy to be assigned to the volume group.
            - I(safeguardpolicyname) is mutually exclusive with parameters I(nosafeguardpolicy) and I(ownershipgroup).
            - Applies when C(state=present).
        type: str
    nosafeguardpolicy:
        description:
            - If specified True, removes the Safeguarded policy assigned to the volume group.
            - Parameters I(safeguardpolicyname) and I(nosafeguardpolicy) are mutually exclusive.
            - Applies when C(state=present).
        type: bool
    policystarttime:
        description:
            - Specifies the time when the first Safeguarded backup is to be taken.
            - I(safeguardpolicyname) is required when using I(policystarttime).
            - The accepted format is YYMMDDHHMM.
            - Applies when C(state=present).
        type: str
author:
    - Shilpi Jain(@Shilpi-J)
notes:
    - This module supports C(check_mode).
'''

EXAMPLES = '''
- name: Using Spectrum Virtualize collection to create a volume group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create a new volume group
      ibm_svc_manage_volumegroup:
        clustername: "{{ clustername }}"
        domain: "{{ domain }}"
        username: "{{ username }}"
        password: "{{ password }}"
        log_path: /tmp/playbook.debug
        name: vg0
        state: present
- name: Using Spectrum Virtualize collection to delete a volume group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete a volume group
      ibm_svc_manage_volumegroup:
        clustername: "{{ clustername }}"
        domain: "{{ domain }}"
        username: "{{ username }}"
        password: "{{ password }}"
        log_path: /tmp/playbook.debug
        name: vg0
        state: absent
- name: Using Spectrum Virtualize collection to update a volume group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Update existing volume group to remove ownershipgroup and attach a safeguardpolicy to it
      ibm_svc_manage_volumegroup:
        clustername: "{{ clustername }}"
        domain: "{{ domain }}"
        username: "{{ username }}"
        password: "{{ password }}"
        log_path: /tmp/playbook.debug
        name: vg0
        state: present
        noownershipgroup: True
        safeguardpolicyname: sg1
'''

RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import \
    IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCVG(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                ownershipgroup=dict(type='str', required=False),
                noownershipgroup=dict(type='bool', required=False),
                safeguardpolicyname=dict(type='str', required=False),
                nosafeguardpolicy=dict(type='bool', required=False),
                policystarttime=dict(type='str', required=False),
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
        self.ownershipgroup = self.module.params.get('ownershipgroup', None)
        self.noownershipgroup = self.module.params.get('noownershipgroup', None)
        self.safeguardpolicyname = self.module.params.get('safeguardpolicyname', None)
        self.nosafeguardpolicy = self.module.params.get('nosafeguardpolicy', None)
        self.policystarttime = self.module.params.get('policystarttime', None)

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

    def get_existing_vg(self):
        merged_result = {}

        data = self.restapi.svc_obj_info(cmd='lsvolumegroup', cmdopts=None,
                                         cmdargs=[self.name])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    def vg_probe(self, data):
        props = {}
        if self.ownershipgroup and self.noownershipgroup:
            self.module.fail_json(msg="You must not pass in both 'ownershipgroup' and "
                                      "'noownershipgroup' to the module.")

        if self.safeguardpolicyname and self.nosafeguardpolicy:
            self.module.fail_json(msg="You must not pass in both 'safeguardpolicyname' and "
                                      "'nosafeguardpolicy' to the module.")

        if self.ownershipgroup and self.safeguardpolicyname:
            self.module.fail_json(msg="You must not pass in both 'ownershipgroup' and "
                                      "'safeguardpolicyname' to the module.")

        if self.ownershipgroup and self.policystarttime:
            self.module.fail_json(msg="'policystarttime' can be used with safeguardpolicyname only.")

        if self.nosafeguardpolicy and self.policystarttime:
            self.module.fail_json(msg="'policystarttime' can be used with safeguardpolicyname only.")

        if self.policystarttime and not self.safeguardpolicyname and not data['safeguarded_policy_name']:
            self.module.fail_json(msg="'policystarttime' can be used with safeguardpolicyname only.")

        if self.ownershipgroup and (not data['owner_name'] or self.ownershipgroup != data['owner_name']):
            props['ownershipgroup'] = self.ownershipgroup

        if self.noownershipgroup and data['owner_name']:
            props['noownershipgroup'] = self.noownershipgroup

        if self.safeguardpolicyname and (not data['safeguarded_policy_name'] or self.safeguardpolicyname != data['safeguarded_policy_name']):
            props['safeguardpolicyname'] = self.safeguardpolicyname
            if self.policystarttime:
                props['policystarttime'] = self.policystarttime
        elif self.safeguardpolicyname and self.safeguardpolicyname == data['safeguarded_policy_name']:
            if self.policystarttime and (not data['safeguarded_policy_start_time'] or (self.policystarttime + "00") != data['safeguarded_policy_start_time']):
                props['safeguardpolicyname'] = self.safeguardpolicyname
                props['policystarttime'] = self.policystarttime

        if self.nosafeguardpolicy and data['safeguarded_policy_name']:
            props['nosafeguardpolicy'] = self.nosafeguardpolicy

        self.log("volumegroup props = '%s'", props)

        return props

    def vg_create(self):
        if self.ownershipgroup and self.noownershipgroup:
            self.module.fail_json(msg="You must not pass in both 'ownershipgroup' and "
                                      "'noownershipgroup' to the module.")

        if self.safeguardpolicyname and self.nosafeguardpolicy:
            self.module.fail_json(msg="You must not pass in both 'safeguardpolicyname' and "
                                      "'nosafeguardpolicy' to the module.")

        if self.ownershipgroup and self.safeguardpolicyname:
            self.module.fail_json(msg="You must not pass in both 'ownershipgroup' and "
                                      "'safeguardpolicyname' to the module.")

        if self.module.check_mode:
            self.changed = True
            return

        self.log("creating volume group '%s'", self.name)

        # Make command
        cmd = 'mkvolumegroup'
        cmdopts = {'name': self.name}
        if self.ownershipgroup:
            cmdopts['ownershipgroup'] = self.ownershipgroup

        if self.safeguardpolicyname and self.policystarttime:
            cmdopts['safeguardedpolicy'] = self.safeguardpolicyname
            cmdopts['policystarttime'] = self.policystarttime
        elif self.safeguardpolicyname:
            cmdopts['safeguardedpolicy'] = self.safeguardpolicyname

        self.log("creating volumegroup '%s'", cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("create volume group result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("create volume group result message %s", result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create volume group [%s]" % self.name)

    def vg_update(self, modify):
        if self.module.check_mode:
            self.changed = True
            return

        # update the volume group
        self.log("updating volume group '%s' ", self.name)

        if modify:
            self.log("updating volume group with properties %s", modify)
            cmd = 'chvolumegroup'
            cmdargs = [self.name]
            for prop in modify:
                cmdopts = {}
                if 'noownershipgroup' in modify and 'nosafeguardpolicy' in modify:
                    cmdopts['noownershipgroup'] = True
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                    cmdopts = {}
                    cmdopts['nosafeguardedpolicy'] = True
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                elif 'nosafeguardpolicy' in modify and 'ownershipgroup' in modify:
                    cmdopts['nosafeguardedpolicy'] = True
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                    cmdopts = {}
                    cmdopts["ownershipgroup"] = self.ownershipgroup
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                elif 'noownershipgroup' in modify and 'safeguardpolicyname' in modify:
                    cmdopts['noownershipgroup'] = True
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                    cmdopts = {}
                    if 'policystarttime' in modify:
                        cmdopts['safeguardedpolicy'] = self.safeguardpolicyname
                        cmdopts['policystarttime'] = self.policystarttime
                    else:
                        cmdopts['safeguardedpolicy'] = self.safeguardpolicyname
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                elif 'noownershipgroup' in modify:
                    cmdopts['noownershipgroup'] = True
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                elif 'nosafeguardpolicy' in modify:
                    cmdopts['nosafeguardedpolicy'] = True
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                elif 'ownershipgroup' in modify:
                    cmdopts["ownershipgroup"] = self.ownershipgroup
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                elif 'safeguardpolicyname' in modify and 'policystarttime' in modify:
                    cmdopts['safeguardedpolicy'] = self.safeguardpolicyname
                    cmdopts['policystarttime'] = self.policystarttime
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                elif 'safeguardpolicyname' in modify:
                    cmdopts['safeguardedpolicy'] = self.safeguardpolicyname
                    self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
                else:
                    self.log("Unsupported Parameter")

            # Any error would have been raised in svc_run_command
            self.changed = True

    def vg_delete(self):
        if self.module.check_mode:
            self.changed = True
            return

        self.log("deleting volume group '%s'", self.name)

        cmd = 'rmvolumegroup'
        cmdopts = None
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
        # Any error will have been raised in svc_run_command
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = {}
        vg_data = self.get_existing_vg()

        if vg_data:
            if self.state == 'absent':
                self.log(
                    "CHANGED: Volume group exists, requested state is 'absent'")
                changed = True
            elif self.state == 'present':
                modify = self.vg_probe(vg_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log(
                    "CHANGED: Volume group does not exist, but requested state is 'present'")
                changed = True
        if changed:
            if self.state == 'present':
                if not vg_data:
                    self.vg_create()
                    msg = "volume group %s has been created." % self.name
                else:
                    self.vg_update(modify)
                    msg = "volume group [%s] has been modified." % self.name
            elif self.state == 'absent':
                self.vg_delete()
                msg = "volume group [%s] has been deleted." % self.name

            if self.module.check_mode:
                msg = 'skipping changes due to check mode.'
        else:
            self.log("exiting with no changes")
            if self.state in ['absent']:
                msg = "Volume group [%s] does not exist." % self.name
            else:
                msg = "No Modifications detected, Volume group already exists."

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCVG()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
