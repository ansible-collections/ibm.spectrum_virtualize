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
module: ibm_svc_manage_flashcopy
short_description: This module manages FlashCopy mappings on IBM Spectrum Virtualize
                   Family storage systems.
description:
  - Ansible interface to manage 'mkfcmap', 'rmfcmap' and 'chfcmap' volume commands.
version_added: "2.10.0"
options:
    name:
        description:
            - Specifies the name of the FlashCopy mapping.
        required: true
        type: str
    state:
        description:
            - Creates (C(present)) or removes (C(absent)) a FlashCopy
              mapping.
        choices: [ present, absent ]
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
    copytype:
        description:
            - Specifies the copy type when creating the FlashCopy mapping.
        choices: [ snapshot, clone]
        type: str
    source:
        description:
            - Specifies the name of the source volume.
        type: str
    target:
        description:
            - Specifies the name of the target volume.
        type: str
    mdiskgrp:
        description:
            - Specifies the name of the storage pool to use when
              creating a volume.
        type: str
    consistgrp:
        description:
            - Specifies the name of the consistency group.
        type: str
    noconsistgrp:
        description:
            - Removes the specified FlashCopy mappings from the consistency group.
        type: bool
    copyrate:
        description:
            - Specifies the copy rate. The rate varies between 0-150.
              If unspecified, the default copy rate is 50 for clone and 0 for snapshot.
        type: str
    grainsize:
        description:
            - Specifies the grain size for the mapping.
              The grainsize can be set to 64 or 256.
              If unspecified, the default value of 256 is set.
        type: str
    force:
        description:
            - Brings the target volume online. This parameter is
              required if the FlashCopy mapping is in the stopped state.
        type: bool
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
    log_path:
        description:
            - Path of debug log file.
        type: str
author:
    - Sreshtant Bohidar(@Sreshtant-Bohidar)
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to create a FlashCopy mapping for snapshot
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create FlashCopy mapping for snapshot
      ibm_svc_manage_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        state: present
        name: snapshot-name
        copytype: snapshot
        source: source-volume-name
        target: target-volume-name
        mdiskgrp: Pool0
        consistgrp: consistencygroup-name
        copyrate: 50
        grainsize: 64

- name: Using the IBM Spectrum Virtualize collection to create a FlashCopy mapping for clone
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create FlashCopy mapping for clone
      ibm_svc_manage_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        state: present
        name: snapshot-name
        copytype: clone
        source: source-volume-name
        target: target-volume-name
        mdiskgrp: Pool0
        consistgrp: consistencygroup-name
        copyrate: 50
        grainsize: 64

- name: Using the IBM Spectrum Virtualize collection to delete a FlashCopy mapping for snapshot
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete FlashCopy mapping for snapshot
      ibm_svc_manage_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: snapshot-name
        state: absent
        force: true

- name: Using the IBM Spectrum Virtualize collection to delete a FlashCopy mapping for clone
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete FlashCopy mapping for clone
      ibm_svc_manage_flashcopy:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: clone-name
        state: absent
        force: true
'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native
import time


class IBMSVCFlashcopy(object):
    def __init__(self):
        argument_spec = svc_argument_spec()
        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                copytype=dict(type='str', required=False, choices=['snapshot', 'clone']),
                source=dict(type='str', required=False),
                target=dict(type='str', required=False),
                mdiskgrp=dict(type='str', required=False),
                state=dict(type='str', required=True, choices=['present', 'absent']),
                consistgrp=dict(type='str', required=False),
                noconsistgrp=dict(type='bool', required=False),
                copyrate=dict(type='str', required=False),
                grainsize=dict(type='str', required=False),
                force=dict(type='bool', required=False)
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
        self.copytype = self.module.params.get('copytype', False)
        self.source = self.module.params.get('source', False)
        self.target = self.module.params.get('target', False)
        self.mdiskgrp = self.module.params.get('mdiskgrp', False)
        self.consistgrp = self.module.params.get('consistgrp', False)
        self.noconsistgrp = self.module.params.get('noconsistgrp', False)
        self.grainsize = self.module.params.get('grainsize', False)
        self.copyrate = self.module.params.get('copyrate', False)
        self.force = self.module.params.get('force', False)

        # Handline for mandatory parameter name
        if not self.name:
            self.module.fail_json(msg="Missing mandatory parameter: name")

        # Handline for mandatory parameter state
        if not self.state:
            self.module.fail_json(msg="Missing mandatory parameter: state")

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def run_command(self, cmd):
        return self.restapi.svc_obj_info(cmd=cmd[0], cmdopts=cmd[1], cmdargs=cmd[2])

    def gather_data(self):
        result = [None, None, None, []]
        commands = [["lsfcmap", None, [self.name]]]
        if self.state == "present" and self.source:
            commands.append(["lsvdisk", {'bytes': True, 'filtervalue': 'name=%s' % self.source}, None])
        if self.state == "present" and self.target:
            commands.append(["lsvdisk", {'bytes': True, 'filtervalue': 'name=%s' % self.target}, None])
            commands.append(["lsvdisk", {'bytes': True, 'filtervalue': 'name=%s' % self.target + "_temp_*"}, None])
        res = list(map(self.run_command, commands))
        if len(res) == 1:
            result[0] = res[0]
        elif len(res) == 2:
            result[0] = res[0]
            result[1] = res[1]
        elif len(res) == 4:
            result = res
        return result

    def target_create(self, temp_target_name, sdata):
        cmd = 'mkvdisk'
        cmdopts = {}
        cmdopts['name'] = temp_target_name
        if self.mdiskgrp:
            cmdopts['mdiskgrp'] = self.mdiskgrp
        else:
            cmdopts['mdiskgrp'] = sdata['mdisk_grp_name']
        cmdopts['size'] = sdata['capacity']
        cmdopts['unit'] = 'b'
        cmdopts['iogrp'] = sdata['IO_group_name']
        if self.copytype == 'snapshot':
            cmdopts['rsize'] = '0%'
            cmdopts['autoexpand'] = True
        self.log("Creating vdisk.. Command %s opts %s", cmd, cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("Create target volume result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("Create target volume result message %s",
                     result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create target volume [%s]" % self.target)

    def fcmap_create(self, temp_target_name):
        if self.copyrate:
            if self.copytype == 'clone':
                if int(self.copyrate) not in range(1, 151):
                    self.module.fail_json(msg="Copyrate for clone must be in range 1-150")
            if self.copytype == 'snapshot':
                if int(self.copyrate) not in range(0, 151):
                    self.module.fail_json(msg="Copyrate for snapshot must be in range 0-150")
        else:
            if self.copytype == 'clone':
                self.copyrate = 50
            elif self.copytype == 'snapshot':
                self.copyrate = 0

        cmd = 'mkfcmap'
        cmdopts = {}
        cmdopts['name'] = self.name
        cmdopts['source'] = self.source
        cmdopts['target'] = temp_target_name
        cmdopts['copyrate'] = self.copyrate
        if self.grainsize:
            cmdopts['grainsize'] = self.grainsize
        if self.consistgrp:
            cmdopts['consistgrp'] = self.consistgrp
        if self.copytype == 'clone':
            cmdopts['autodelete'] = True
        self.log("Creating fc mapping.. Command %s opts %s",
                 cmd, cmdopts)
        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("Create flash copy mapping relationship result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("Create flash copy mapping relationship result "
                     "message %s", result['message'])
        else:
            self.module.fail_json(msg="Failed to create FlashCopy mapping "
                                      "relationship [%s]" % self.name)

    def fcmap_delete(self):
        self.log("Deleting flash copy mapping relationship'%s'", self.name)
        cmd = 'rmfcmap'
        cmdopts = {}
        if self.force:
            cmdopts['force'] = self.force
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])

    def rename_temp_to_target(self, temp_name):
        cmd = 'chvdisk'
        cmdopts = {}
        cmdopts['name'] = self.target
        self.log("Rename %s to %s", cmd, cmdopts)
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[temp_name])

    def fcmap_probe(self, data):
        props = {}
        props_not_supported = []
        if self.source:
            if data["source_vdisk_name"] != self.source:
                props_not_supported.append("source")
        if self.target:
            if data["target_vdisk_name"] != self.target:
                props_not_supported.append("target")
        if self.copytype:
            if (self.copytype == "snapshot" and data['autodelete'] == "on") or (self.copytype == "clone" and data["autodelete"] != "on"):
                props_not_supported.append("copytype")
        if self.grainsize:
            if data['grain_size'] != self.grainsize:
                props_not_supported.append("grainsize")
        if props_not_supported:
            self.module.fail_json(msg="Update not supported for parameter: " + ", ".join(props_not_supported))
        self.log("Probe which properties need to be updated...")
        if data['group_name'] and self.noconsistgrp:
            props['consistgrp'] = 0
        if not self.noconsistgrp:
            if self.consistgrp:
                if self.consistgrp != data['group_name']:
                    props['consistgrp'] = self.consistgrp
        if self.copyrate:
            if self.copyrate != data['copy_rate']:
                props['copyrate'] = self.copyrate
        return props

    def fcmap_update(self, modify):
        if modify:
            self.log("updating fcmap with properties %s", modify)
            cmd = 'chfcmap'
            cmdopts = {}
            for prop in modify:
                cmdopts[prop] = modify[prop]
            cmdargs = [self.name]
            self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

    def apply(self):
        changed = False
        msg = None
        modify = []
        mdata, sdata, tdata, temp = self.gather_data()
        if mdata:
            if self.state == "present":
                modify = self.fcmap_probe(mdata)
                if modify:
                    changed = True
                else:
                    msg = "mapping [%s] already exists" % self.name
            elif self.state == "absent":
                changed = True
        else:
            if self.state == "present":
                changed = True
            elif self.state == "absent":
                msg = "mapping [%s] does not exist" % self.name
        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode.')
            else:
                if self.state == "present" and not modify:
                    if None in [self.source, self.target, self.copytype]:
                        self.module.fail_json(msg="Required while creating FlashCopy mapping: 'source', 'target' and 'copytype'")
                    if sdata:
                        if tdata:
                            if sdata[0]["capacity"] == tdata[0]["capacity"]:
                                self.module.fail_json(msg="target [%s] already exists" % self.target)
                            else:
                                self.module.fail_json(msg="source and target must be of same size")
                        temp_target = "%s_temp_%s" % (self.target, time.time())
                        if len(temp) == 0:
                            self.target_create(temp_target, sdata[0])
                            self.fcmap_create(temp_target)
                            self.rename_temp_to_target(temp_target)
                            msg = "mapping [%s] has been created" % self.name
                        elif len(temp) == 1:
                            self.fcmap_create(temp[0]["name"])
                            self.rename_temp_to_target(temp[0]["name"])
                            msg = "mapping [%s] has been created" % self.name
                        elif len(temp) > 1:
                            self.module.fail_json(msg="Multiple %s_temp_* volumes exists" % self.target)
                    else:
                        self.module.fail_json(msg="The source volume [%s] doesn't exist." % self.source)
                elif self.state == "present" and modify:
                    self.fcmap_update(modify)
                    msg = "mapping [%s] has been modified" % self.name
                elif self.state == "absent":
                    self.fcmap_delete()
                    msg = "mapping [%s] has been deleted" % self.name
        else:
            if self.state == "absent":
                msg = "mapping [%s] does not exist" % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCFlashcopy()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
