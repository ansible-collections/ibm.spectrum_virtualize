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
module: ibm_svc_mdiskgrp
short_description: This module manages pools on IBM Spectrum Virtualize
                   Family storage systems.
description:
  - Ansible interface to manage 'mkmdiskgrp' and 'rmmdiskgrp' pool commands.
version_added: "2.10"
options:
  name:
    description:
      - Specifies a name to assign to the new pool
    required: true
    type: str
  state:
    description:
      - Creates (C(present)) or removes (C(absent)) an MDisk group
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
  datareduction:
    description:
    - Defines use of data reduction pools (DRPs) on the MDisk group
    type: str
    default: 'no'
    choices: ['yes', 'no']
  easytier:
    description:
    - Defines use of easytier with the MDisk group
    type: str
    default: 'off'
    choices: ['on', 'off', 'auto']
  encrypt:
    description:
    - Defines use of encryption with the MDisk group
    type: str
    default: 'no'
    choices: ['yes', 'no']
  ext:
    description:
    - Specifies the size of the extents for this group in MB
    type: int
  log_path:
    description:
    - Debugs log for this file
    type: str
  validate_certs:
    description:
      - Validate certification
    type: bool
  parentmdiskgrp:
    description:
      - parentmdiskgrp for subpool
    type: str
  unit:
    description:
      - Unit for subpool
    type: str
  size:
    description:
      - Specifies the child pool capacity. The value must be
        a numeric value (and an integer multiple of the extent size)
    type: int
author:
    - Peng Wang(@wangpww)
'''
EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to create a pool
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: make mdisk group
      ibm_svc_mdiskgrp:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        name: pool1
        state: present
        datareduction: no
        easytier: auto
        encrypt: no
        ext: 1024

- name: Using the IBM Spectrum Virtualize collection to delete a pool
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: delete mdisk group
      ibm_svc_mdiskgrp:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        name: pool1
        state: absent

'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger


class IBMSVCmdiskgrp(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                datareduction=dict(type='str', default='no', choices=['yes',
                                                                      'no']),
                easytier=dict(type='str', default='off', choices=['on', 'off',
                                                                  'auto']),
                encrypt=dict(type='str', default='no', choices=['yes', 'no']),
                ext=dict(type='int'),
                parentmdiskgrp=dict(type='str'),
                size=dict(type='int'),
                unit=dict(type='str')
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
        self.datareduction = self.module.params.get('datareduction', None)
        self.easytier = self.module.params.get('easytier', None)
        self.encrypt = self.module.params.get('encrypt', None)
        self.ext = self.module.params.get('ext', None)

        self.parentmdiskgrp = self.module.params.get('parentmdiskgrp', None)
        self.size = self.module.params.get('size', None)
        self.unit = self.module.params.get('unit', None)

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def mdiskgrp_exists(self):
        return self.restapi.svc_obj_info(cmd='lsmdiskgrp', cmdopts=None,
                                         cmdargs=[self.name])

    def mdiskgrp_create(self):
        if self.module.check_mode:
            self.changed = True
            return

        # So ext is optional to mkmdiskgrp but make required in ansible
        # until all options for create are implemented.
        # if not self.ext:
        #    self.module.fail_json(msg="You must pass in ext to the module.")

        self.log("creating mdisk group '%s'", self.name)

        # Make command
        cmd = 'mkmdiskgrp'
        cmdopts = {}

        if not self.ext:
            self.module.fail_json(msg="You must pass the ext to the module.")
        if self.parentmdiskgrp:
            cmdopts['parentmdiskgrp'] = self.parentmdiskgrp
            if self.size:
                cmdopts['size'] = self.size
            if self.unit:
                cmdopts['unit'] = self.unit
        else:
            if self.datareduction:
                cmdopts['datareduction'] = self.datareduction
            if self.easytier:
                cmdopts['easytier'] = self.easytier
            if self.encrypt:
                cmdopts['encrypt'] = self.encrypt
            if self.ext:
                cmdopts['ext'] = str(self.ext)
        cmdopts['name'] = self.name
        self.log("creating mdisk group command %s opts %s", cmd, cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("creating mdisk group result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("creating mdisk group command result message %s",
                     result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create mdisk group [%s]" % (self.name))

    def mdiskgrp_delete(self):
        self.log("deleting mdiskgrp '%s'", self.name)

        cmd = 'rmmdiskgrp'
        cmdopts = None
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmkdiskgrp does not output anything when successful.
        self.changed = True

    def mdiskgrp_update(self, modify):
        # updte the mdisk group
        self.log("updating mdiskgrp '%s'", self.name)

        # cmd = 'chmdiskgrp'
        # cmdopts = {}
        # TBD: Be smarter handling many properties.
        # if 'easytier' in modify:
        #    cmdopts['easytier'] = self.easytier
        # cmdargs = [self.name]

        # result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmkdiskgrp does not output anything when successful.
        self.changed = True

    # TBD: Implement a more generic way to check for properties to modify.
    def mdiskgrp_probe(self, data):
        props = []

        # TBD: The parameter is easytier but the view has easy_tier label.
        # if self.easytier:
        #    if self.easytier != data['easy_tier']:
        #        props += ['easytier']

        if props is []:
            props = None

        self.log("mdiskgrp_probe props='%s'", data)
        return props

    def apply(self):
        changed = False
        msg = None
        modify = []

        mdiskgrp_data = self.mdiskgrp_exists()

        if mdiskgrp_data:
            if self.state == 'absent':
                self.log("CHANGED: mdisk group exists, "
                         "but requested state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chmdiskgrp should be called.
                modify = self.mdiskgrp_probe(mdiskgrp_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: mdisk group does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not mdiskgrp_data:
                        self.mdiskgrp_create()
                        msg = "Mdisk group [%s] has been created." % self.name
                    else:
                        # This is where we would modify
                        self.mdiskgrp_update(modify)
                        msg = "Mdisk group [%s] has been modified." % self.name

                elif self.state == 'absent':
                    self.mdiskgrp_delete()
                    msg = "Volume [%s] has been deleted." % self.name
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "Mdisk group [%s] did not exist." % self.name
            else:
                msg = "Mdisk group [%s] already exists." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCmdiskgrp()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
