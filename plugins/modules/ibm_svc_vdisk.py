#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: ibm_svc_vdisk
short_description: This module manages volumes on IBM Spectrum Virtualize
                   Family storage systems.
description:
  - Ansible interface to manage 'mkvdisk' and 'rmvdisk' volume commands.
version_added: "2.10"
options:
  name:
    description:
      - Specifies a name to assign to the new volume
    required: true
    type: str
  state:
    description:
      - Creates (C(present)) or removes (C(absent)) a volume
    choices: [ absent, present ]
    required: true
    type: str
  clustername:
    description:
    - The hostname or management IP of the Spectrum Virtualize storage system
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
  mdiskgrp:
    description:
    - Specifies one or more storage pool names to use when
      creating this volume
    type: str
  easytier:
    description:
    - Defines use of easytier with VDisk
    type: str
    default: 'off'
    choices: [ 'on', 'off', 'auto' ]
  size:
    description:
    - Defines size of VDisk
    type: str
  unit:
    description:
    - Defines the size option for the storage unit
    type: str
    choices: [ b, kb, mb, gb, tb, pb ]
    default: mb
  validate_certs:
    description:
    - Validates certification
    type: bool
  log_path:
    description:
    - Path of debug log file
    type: str
  rsize:
    description:
    - Defines how much physical space is initially allocated to the thin-provisioned volume in %.
      If rsize is not passed, the volume created is a standard volume.
    type: str
  autoexpand:
    description:
    - Specifies that thin-provisioned volume copies can automatically expand their real capacities
    type: bool
author:
    - Sreshtant Bohidar(@Sreshtant-Bohidar)
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to create a volume
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create volume
      ibm_svc_vdisk:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: volume0
        state: present
        mdiskgrp: Pool0
        easytier: 'off'
        size: "4294967296"
        unit: b

- name: Using the IBM Spectrum Virtualize collection to create a thin-provisioned volume
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create volume
      ibm_svc_vdisk:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: volume0
        state: present
        mdiskgrp: Pool0
        easytier: 'off'
        size: "4294967296"
        unit: b
        rsize: '20%'
        autoexpand: true

- name: Using the IBM Spectrum Virtualize collection to delete a volume
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete volume
      ibm_svc_vdisk:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: volume0
        state: absent
'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCvdisk(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                mdiskgrp=dict(type='str', required=False),
                size=dict(type='str', required=False),
                unit=dict(type='str', default='mb', choices=['b', 'kb',
                                                             'mb', 'gb',
                                                             'tb', 'pb']),
                easytier=dict(type='str', default='off', choices=['on', 'off',
                                                                  'auto']),
                rsize=dict(type='str', required=False),
                autoexpand=dict(type='bool', required=False)
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
        self.mdiskgrp = self.module.params['mdiskgrp']
        self.size = self.module.params['size']
        self.unit = self.module.params['unit']
        self.easytier = self.module.params.get('easytier', None)
        self.rsize = self.module.params['rsize']
        self.autoexpand = self.module.params['autoexpand']

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def get_existing_vdisk(self):
        merged_result = {}

        data = self.restapi.svc_obj_info(cmd='lsvdisk', cmdopts=None,
                                         cmdargs=[self.name])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    # TBD: Implement a more generic way to check for properties to modify.
    def vdisk_probe(self, data):
        props = []

        # TBD: The parameter is easytier but the view has easy_tier label.
        if self.easytier:
            if self.easytier != data['easy_tier']:
                props += ['easytier']

        if props is []:
            props = None

        self.log("vdisk_probe props='%s'", data)
        return props

    def vdisk_create(self):
        if self.module.check_mode:
            self.changed = True
            return

        if not self.mdiskgrp:
            self.module.fail_json(msg="You must pass in "
                                      "mdiskgrp to the module.")
        if not self.size:
            self.module.fail_json(msg="You must pass in size to the module.")
        if not self.unit:
            self.module.fail_json(msg="You must pass in unit to the module.")
        self.log("creating vdisk '%s'", self.name)

        # Make command
        cmd = 'mkvdisk'
        cmdopts = {}
        if self.mdiskgrp:
            cmdopts['mdiskgrp'] = self.mdiskgrp
        if self.size:
            cmdopts['size'] = self.size
        if self.unit:
            cmdopts['unit'] = self.unit
        if self.easytier:
            cmdopts['easytier'] = self.easytier
        if self.rsize:
            cmdopts['rsize'] = self.rsize
        if self.autoexpand:
            cmdopts['autoexpand'] = self.autoexpand
        cmdopts['name'] = self.name
        self.log("creating vdisk command %s opts %s", cmd, cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("create vdisk result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("create vdisk result message %s", result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create vdisk [%s]" % self.name)

    def vdisk_update(self, modify):
        # update the vdisk
        self.log("updating vdisk '%s'", self.name)

        cmd = 'chvdisk'
        cmdopts = {}

        # TBD: Be smarter handling many properties.
        if 'easytier' in modify:
            cmdopts['easytier'] = self.easytier
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chvdisk does not output anything when successful.
        self.changed = True

    def vdisk_delete(self):
        self.log("deleting vdisk '%s'", self.name)

        cmd = 'rmvdisk'
        cmdopts = None
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmvdisk does not output anything when successful.
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = []

        vdisk_data = self.get_existing_vdisk()

        if vdisk_data:
            if self.state == 'absent':
                self.log("CHANGED: vdisk exists, but requested "
                         "state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chvdisk should be called
                modify = self.vdisk_probe(vdisk_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: vdisk does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not vdisk_data:
                        self.vdisk_create()
                        msg = "vdisk %s has been created." % self.name
                    else:
                        # This is where we would modify
                        self.vdisk_update(modify)
                        msg = "vdisk [%s] has been modified." % self.name
                elif self.state == 'absent':
                    self.vdisk_delete()
                    msg = "vdisk [%s] has been deleted." % self.name
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "vdisk [%s] did not exist." % self.name
            else:
                msg = "vdisk [%s] already exists." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCvdisk()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
