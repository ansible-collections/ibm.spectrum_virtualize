#!/usr/bin/python
# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ibm_svc_mdisk
short_description: This module manages MDisks on IBM Spectrum Virtualize
                   Family storage systems.
description:
  - Ansible interface to manage 'mkarray' and 'rmmdisk' MDisk commands.
version_added: "2.10"
options:
  name:
    description:
      - The MDisk name
    required: true
    type: str
  state:
    description:
      - Creates (C(present)) or removes (C(absent)) the MDisk
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
      - Domain for the IBM Spectrum Virtualize storage system
    type: str
  username:
    description:
      - REST API username for the IBM Spectrum Virtualize storage system
    required: true
    type: str
  password:
    description:
      - REST API password for the IBM Spectrum Virtualize storage system
    required: true
    type: str
  drive:
    description:
      - Drive(s) to use as members of the RAID array
    type: str
  mdiskgrp:
    description:
      - The storage pool (mdiskgrp) to which you want to add the MDisk
    type: str
    required: true
  log_path:
    description:
      - Debugs log for this file
    type: str
  validate_certs:
    description:
      - Validate certification
    type: bool
  level:
    description:
      - level
    type: str
    choices: ['raid0', 'raid1', 'raid5', 'raid6', 'raid10']
  encrypt:
    description:
      - encrypt
    type: str
    default: 'no'
    choices: ['yes', 'no']
author:
    - Peng Wang(@wangpww)
'''
EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to create a new MDisk array
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create MDisk and named mdisk20
      ibm_svc_mdisk:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        name: mdisk20
        state: present
        level: raid0
        drive: '5:6'
        encrypt: no
        mdiskgrp: pool20

- name: Using the IBM Spectrum Virtualize collection to delete an MDisk array
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete MDisk named mdisk20
      ibm_svc_mdisk:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        name: mdisk20
        state: absent
        mdiskgrp: pool20
'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger


class IBMSVCmdisk(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                level=dict(type='str', choices=['raid0', 'raid1', 'raid5',
                                                'raid6', 'raid10']),
                drive=dict(type='str', default=None),
                encrypt=dict(type='str', default='no', choices=['yes', 'no']),
                mdiskgrp=dict(type='str', required=True)
            )
        )

        mutually_exclusive = []
        self.module = AnsibleModule(argument_spec=argument_spec,
                                    mutually_exclusive=mutually_exclusive,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Optional
        self.level = self.module.params.get('level', None)
        self.drive = self.module.params.get('drive', None)
        self.encrypt = self.module.params.get('encrypt', None)
        self.mdiskgrp = self.module.params.get('mdiskgrp', None)

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def mdisk_exists(self):
        return self.restapi.svc_obj_info(cmd='lsmdisk', cmdopts=None,
                                         cmdargs=[self.name])

    def mdisk_create(self):
        if self.module.check_mode:
            self.changed = True
            return

        # For now we create mdisk via mkarray which needs these options
        # level, drive, mdiskgrp
        if not self.level:
            self.module.fail_json(msg="You must pass in level to the module.")
        if not self.drive:
            self.module.fail_json(msg="You must pass in drive to the module.")
        if not self.mdiskgrp:
            self.module.fail_json(msg="You must pass in "
                                      "mdiskgrp to the module.")

        self.log("creating mdisk '%s'", self.name)

        # Make command
        cmd = 'mkarray'
        cmdopts = {}
        if self.level:
            cmdopts['level'] = self.level
        if self.drive:
            cmdopts['drive'] = self.drive
        if self.encrypt:
            cmdopts['encrypt'] = self.encrypt
        cmdopts['name'] = self.name
        cmdargs = [self.mdiskgrp]
        self.log("creating mdisk command=%s opts=%s args=%s",
                 cmd, cmdopts, cmdargs)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
        self.log("create mdisk result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("create mdisk result message %s", result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create mdisk [%s]" % self.name)

    def mdisk_delete(self):
        self.log("deleting mdisk '%s'", self.name)
        cmd = 'rmmdisk'
        cmdopts = {}
        cmdopts['mdisk'] = self.name
        cmdargs = [self.mdiskgrp]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmkdiskgrp does not output anything when successful.
        self.changed = True

    def mdisk_update(self, modify):
        # update the mdisk
        self.log("updating mdisk '%s'", self.name)

        # cmd = 'chmdisk'
        # cmdopts = {}
        # chmdisk does not like mdisk arrays.
        # cmdargs = [self.name]

        # TBD: Implement changed logic.
        # result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmkdiskgrp does not output anything when successful.
        self.changed = True

    # TBD: Implement a more generic way to check for properties to modify.
    def mdisk_probe(self, data):
        props = []

        if self.encrypt:
            if self.encrypt != data['encrypt']:
                props += ['encrypt']

        if props is []:
            props = None

        self.log("mdisk_probe props='%s'", data)
        return props

    def apply(self):
        changed = False
        msg = None
        modify = []

        mdisk_data = self.mdisk_exists()

        if mdisk_data:
            if self.state == 'absent':
                self.log("CHANGED: mdisk exists, but "
                         "requested state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chmdisk should be called.
                modify = self.mdisk_probe(mdisk_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: mdisk does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not mdisk_data:
                        self.mdisk_create()
                        msg = "Mdisk [%s] has been created." % self.name
                    else:
                        # This is where we would modify
                        self.mdisk_update(modify)
                        msg = "Mdisk [%s] has been modified." % self.name

                elif self.state == 'absent':
                    self.mdisk_delete()
                    msg = "Volume [%s] has been deleted." % self.name
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "Mdisk [%s] did not exist." % self.name
            else:
                msg = "Mdisk [%s] already exists." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCmdisk()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
