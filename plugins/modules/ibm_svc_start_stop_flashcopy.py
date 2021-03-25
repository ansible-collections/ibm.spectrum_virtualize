#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
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
module: ibm_svc_start_stop_flashcopy
short_description: This module starts or stops FlashCopy mapping and consistency groups
                   on IBM Spectrum Virtualize Family storage systems.
description:
  - Ansible interface to manage 'startfcmap', 'stopfcmap', 'startfcconsistgrp' and 'stopfcconsistgrp' commands.
version_added: "2.10.0"
options:
    name:
        description:
            - Specifies the name of the FlashCopy mapping or FlashCopy consistency group.
        required: true
        type: str
    state:
        description:
            - Specifies the state of the FlashCopy mapping or FlashCopy consistency group.
        choices: [ started, stopped ]
        required: true
        type: str
    clustername:
        description:
            - The hostname or management IP of the Spectrum Virtualize storage system.
        type: str
        required: true
    domain:
        description:
            - Domain for the Spectrum Virtualize storage system.
        type: str
    username:
        description:
            - REST API username for the Spectrum Virtualize storage system.
        required: true
        type: str
    password:
        description:
            - REST API password for the Spectrum Virtualize storage system.
        required: true
        type: str
    isgroup:
        description:
            - Specifies that a consistency group has to be started or stopped.
        required: false
        type: bool
    force:
        description:
            - Specifies that all processing associated with the FlashCopy mapping
              of a consistency group be immediately stopped.
        required: false
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
    - Sreshtant Bohidar(@Sreshtant-Bohidar)
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to start a FlashCopy mapping
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Start a FlashCopy mapping
      ibm_svc_start_stop_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: mapping-name
        state: started

- name: Using the IBM Spectrum Virtualize collection to stop a FlashCopy mapping
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Stop a FlashCopy mapping
      ibm_svc_start_stop_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: mapping-name
        state: stopped

- name: Using the IBM Spectrum Virtualize collection to start a FlashCopy consistency group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Start a FlashCopy consistenecy group
      ibm_svc_start_stop_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: fcconsistgrp-name
        isgroup: true
        state: started

- name: Using the IBM Spectrum Virtualize collection to stop a FlashCopy consistency group
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Stop a FlashCopy consistency group
      ibm_svc_start_stop_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: fcconsistgrp-name
        isgroup: true
        state: stopped

'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCFlashcopyStartStop(object):
    def __init__(self):
        argument_spec = svc_argument_spec()
        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['started', 'stopped']),
                isgroup=dict(type='bool', required=False),
                force=dict(type='bool', required=False),
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Optional
        self.isgroup = self.module.params.get('isgroup', False)
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

    def get_existing_fcmapping(self):
        merged_result = {}
        data = {}
        if self.isgroup:
            data = self.restapi.svc_obj_info(cmd='lsfcconsistgrp', cmdopts=None, cmdargs=[self.name])
        else:
            data = self.restapi.svc_obj_info(cmd='lsfcmap', cmdopts=None, cmdargs=[self.name])
        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data
        return merged_result

    def start_fc(self):
        cmd = ''
        if self.isgroup:
            cmd = 'startfcconsistgrp'
        else:
            cmd = 'startfcmap'
        cmdopts = {}
        cmdopts['prep'] = True
        if self.force:
            cmdopts["force"] = self.force
        self.log("Starting fc mapping.. Command %s opts %s", cmd, cmdopts)
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])

    def stop_fc(self):
        cmd = ''
        if self.isgroup:
            cmd = 'stopfcconsistgrp'
        else:
            cmd = 'stopfcmap'
        cmdopts = {}
        if self.force:
            cmdopts["force"] = self.force
        self.log("Stopping fc mapping.. Command %s opts %s", cmd, cmdopts)
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])

    def apply(self):
        changed = False
        msg = None
        modify = []
        fcdata = self.get_existing_fcmapping()
        if fcdata:
            if self.state == "started" and fcdata["start_time"] == "":
                self.log("[%s] exists, but requested state is 'started'", self.name)
                changed = True
            elif self.state == "stopped" and fcdata["start_time"] != "":
                self.log("[%s] exists, but requested state is 'stopped'", self.name)
                changed = True
        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode.')
            else:
                if self.state == "started":
                    self.start_fc()
                    msg = "fc [%s] has been started" % self.name
                elif self.state == "stopped":
                    self.stop_fc()
                    msg = "fc [%s] has been stopped" % self.name
        else:
            if fcdata:
                if self.state == "started" or self.state == "stopped":
                    self.log("[%s] exists, but currently in [%s] state", self.name, fcdata["status"])
                    if self.isgroup:
                        msg = "FlashCopy Consistency Group [%s] is in [%s] state." % (self.name, fcdata["status"])
                    else:
                        msg = "FlashCopy Mapping [%s] is in [%s] state." % (self.name, fcdata["status"])
            else:
                if self.state == "started" or self.state == "stopped":
                    if self.isgroup:
                        msg = "FlashCopy Consistency Group [%s] does not exist." % self.name
                    else:
                        msg = "FlashCopy Mapping [%s] does not exist." % self.name
        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCFlashcopyStartStop()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
