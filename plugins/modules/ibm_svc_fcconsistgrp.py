#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
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
module: ibm_svc_fcconsistgrp
short_description: This module manages FlashCopy consistency group on
                   IBM Spectrum Virtualize Family storage systems.
version_added: "2.10"

description:
  - Ansible interface to manage 'mkfcconsistgrp', 'lsfcconsistgrp',
    'startfcconsistgrp', 'stopfcconsistgrp', 'prestartfcconsistgrp', and
    'rmfcconsistgrp' flashcopy consistency group commands.

options:
    name:
        description:
            - Specifies a name for the consistency group
        required: true
        type: str
    state:
        description:
            - Creates (C(present)) or removes (C(absent)) a FlashCopy
              consistency group; or prestart, start or stop a FlashCopy
              consistency group
        choices: [ absent, present, prestart, start, stop ]
        required: true
        type: str
    clustername:
        description:
            - The hostname or management IP of
              Spectrum Virtualize storage
        type: str
        required: true
    domain:
        description:
            - Domain for IBM Spectrum Virtualize storage system
        type: str
    username:
        description:
            - REST API username for IBM Spectrum Virtualize storage system
        required: true
        type: str
    password:
        description:
            - REST API password for IBM Spectrum Virtualize storage system
        required: true
        type: str
    autodelete:
        description:
            - Deletes the consistency group when the last mapping that it
              contains is deleted or removed from the consistency group
        choices: [ 'on', 'off' ]
        default: 'off'
        type: str
    prep:
        description:
            - Specifies that the designated FlashCopy consistency group be
              prepared prior to starting the FlashCopy consistency group
        default: false
        type: bool
    restore:
        description:
            - Specifies the restore flag
        default: false
        type: bool
    split:
        description:
            - Breaks the dependency on the source volumes of any
              mappings that are also dependent on the target volume
        default: false
        type: bool
    force:
        description:
            - Specifies the force flag
        default: false
        type: bool
    log_path:
        description:
            - Debugs log for this file
        type: str
    validate_certs:
        description:
            - Validate certification
        type: bool
author:
    - Peng Wang (@wangpww)
'''

EXAMPLES = '''
- name: Using IBM Spectrum Virtualize collection to create fc consistency group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Define a new fc consistency group
      ibm_svc_fcconsistgrp:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: fccg4test
        state: present
        autodelete: on

- name: Using IBM Spectrum Virtualize collection to start a fc cg
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: start a fc consistency group
      ibm_svc_fcconsistgrp:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: fccg4test
        state: start
        prep: true
        restore: true

- name: Using IBM Spectrum Virtualize collection to stop a fc consistency group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: stop a fc consistency group
      ibm_svc_fcconsistgrp:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: fccg4test
        state: stop
        force: true

- name: Using IBM Spectrum Virtualize collection to delete fc consistency group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete fc consistency group
      ibm_svc_fcconsistgrp:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: fccg4test
        state: absent
        force: true
'''

RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCFCCG(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present',
                                                               'prestart',
                                                               'start',
                                                               'stop']),
                restore=dict(type='bool', required=False),
                prep=dict(type='bool', required=False),
                force=dict(type='bool', required=False),
                split=dict(type='bool', required=False),
                autodelete=dict(type='str', required=False,
                                choices=['on', 'off'], default='off')
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
        self.prep = self.module.params.get('prep', False)
        self.autodelete = self.module.params.get('autodelete', 'off')
        self.restore = self.module.params.get('restore', False)
        self.split = self.module.params.get('split', False)
        self.force = self.module.params.get('force', False)

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def get_existing_fccg(self):
        merged_result = {}

        data = self.restapi.svc_obj_info(cmd='lsfcconsistgrp', cmdopts=None,
                                         cmdargs=[self.name])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    # TBD: Implement a more generic way to check for properties to modify.
    def fccg_probe(self, data):
        props = {}
        self.log("Probe which properties need to be updated...")
        if self.autodelete != data['autodelete']:
            props['autodelete'] = self.autodelete
        return props

    def fccg_create(self):
        self.log("creating fc consistgrp '%s'", self.name)

        # Make command
        cmd = 'mkfcconsistgrp'
        cmdopts = {'name': self.name}
        if self.autodelete == 'on':
            cmdopts['autodelete'] = True

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("create fc consistgrp result '%s'", result)

        if 'message' in result:
            self.changed = True
            self.log("create fc consistgrp result message '%s'",
                     result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create fc consistgrp [%s]" % self.name)

    def fccg_prestart(self):
        self.log("prestart fc consistgrp '%s'", self.name)
        # Make command
        cmd = 'prestartfcconsistgrp'
        cmdopts = {'restore': self.restore}
        result = self.restapi.svc_run_command(cmd, cmdopts,
                                              cmdargs=[self.name])
        self.log("prestart fc consistgrp result '%s'", result)

        self.changed = True
        self.log("prestart fc consistgrp successfully")

    def fccg_start(self):
        self.log("start fc consistgrp '%s'", self.name)
        # Make command
        cmd = 'startfcconsistgrp'
        cmdopts = {'restore': self.restore, 'prep': self.prep}
        result = self.restapi.svc_run_command(cmd, cmdopts,
                                              cmdargs=[self.name])
        self.changed = True
        self.log("start fc consistgrp successfully")

    def fccg_stop(self):
        self.log("stop fc consistgrp '%s'", self.name)
        # Make command
        cmd = 'stopfcconsistgrp'
        cmdopts = {'force': self.force, 'split': self.split}
        result = self.restapi.svc_run_command(cmd, cmdopts,
                                              cmdargs=[self.name])
        self.log("stop fc consistgrp result '%s'", result)

        self.changed = True
        self.log("stop fc consistgrp successfully")

    def fccg_update(self, modify):
        if modify:
            self.log("updating fc consistgrp '%s'", self.name)

            cmd = 'chfcconsistgrp'
            cmdopts = {}
            for prop in modify:
                cmdopts[prop] = modify[prop]
            cmdargs = [self.name]

            self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

            # Any error will have been raised in svc_run_command
            # chfcconsistgrp does not output anything when successful.
            self.changed = True
        else:
            self.log("No property need to be update for fccg: %s", self.name)
            self.changed = False

    def fccg_delete(self):
        self.log("deleting fc consistgrp '%s'", self.name)

        cmd = 'rmfcconsistgrp'
        cmdopts = {}
        if self.force:
            cmdopts['force'] = True
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # rmfcconsistgrp does not output anything when successful.
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = []

        fccg_data = self.get_existing_fccg()

        if fccg_data:
            if self.state == 'absent':
                self.log("CHANGED: fc consistgrp exists, and requested "
                         "state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chfcconsistgrp should be called
                modify = self.fccg_probe(fccg_data)
                if modify:
                    changed = True
            elif self.state in ['prestart', 'start', 'stop']:
                changed = True
                self.log('The operation for the fc'
                         'consistgrp is %s', self.state)
        else:
            if self.state == 'present':
                self.log("CHANGED: fc consistgrp does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not fccg_data:
                        self.fccg_create()
                        msg = "fc consistgrp %s has been created." % (
                            self.name)
                    else:
                        # This is where we would modify
                        self.fccg_update(modify)
                        msg = "fc consistgrp [%s] has been modified." % (
                            self.name)
                elif self.state == 'absent':
                    self.fccg_delete()
                    msg = "fc consistgrp [%s] has been deleted." % self.name
                elif self.state == 'prestart':
                    self.fccg_prestart()
                    msg = "fc consistgrp [%s] has been prestarted." % self.name
                elif self.state == 'start':
                    self.fccg_start()
                    msg = "fc consistgrp [%s] has been started." % self.name
                elif self.state == 'stop':
                    self.fccg_stop()
                    msg = "fc consistgrp [%s] has been stopped." % self.name
        else:
            self.log("exiting with no changes")
            if self.state in ['absent', 'prestart', 'start', 'stop']:
                msg = ('fc consistgrp %s did not exist and the'
                       'operations is %s', self.name, self.state)
                self.log(msg)
            else:
                msg = "fc consistgrp [%s] already exists." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCFCCG()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
