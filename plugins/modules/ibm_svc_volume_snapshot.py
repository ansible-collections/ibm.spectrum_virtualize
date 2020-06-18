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
module: ibm_svc_volume_snapshot
short_description: This module manages snapshots on IBM Spectrum Virtualize
                   Family storage systems.
description:
  - Ansible interface to manage 'mkfcmap', 'prestartfcmap', 'startfcmap',
    'stopfcmap' and 'rmfcmap' volume commands.
version_added: "2.10"
options:
  state:
    description:
      - Creates (C(present)) or removes (C(absent)) a snapshot;
        prestart, start or stop a FlashCopy mapping
    choices: [ absent, present, prestart, start, stop ]
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
  name:
    description:
      - Specifies the name to assign to the new mapping
    type: str
    required: true
  volume:
    description:
    - Name of the volume on which the snapshot is to be created
    required: true
    type: str
  snapshot:
    description:
    - Name of the snapshot to be managed
    required: true
    type: str
  mdiskgrp:
    description:
    - Specifies one storage pool name to use when you are
      creating this snapshot
    type: str
  consistgrp:
    description:
    - Specifies the consistency group to add the new mapping to
    type: str
  grainsize:
    description:
    - Specifies the grain size for the mapping
    choices: [ '64', '256' ]
    type: str
  iogrp:
    description:
    - Specifies the I/O group for the FlashCopy bitmap
    type: str
  copyrate:
    description:
    - Specifies the copy rate
    type: str
    default: '0'
  cleanrate:
    description:
    - Sets the cleaning rate for the mapping
    type: str
    default: '0'
  autodelete:
    description:
    - Specifies that a mapping is to be deleted when the
      background copy completes
    choices: [ 'on', 'off' ]
    default: 'off'
    type: str
  keeptarget:
    description:
    - Specifies that the target volume and source volume
      availability should be kept the same
    type: bool
  restore:
    description:
    - Specifies the restore flag
    type: bool
  prep:
    description:
    - Specifies that the designated mapping be prepared prior to
      starting the mapping
    type: bool
  force:
    description:
    - Specifies that all processing that is associated with the
      designated mapping be stopped immediately
    type: bool
  split:
    description:
    - Breaks the dependency on the source volume of any mappings
      that are also dependent on the target disk
    type: bool
  validate_certs:
    description:
    - Validate certification
    type: bool
  log_path:
    description:
    - Debugs log for this file
    type: str
author:
    - Peng Wang(@wangpww)
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to create a Flash Copy Mapping
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create Flash Copy Mapping for snapshot
      ibm_svc_volume_snapshot:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        state: present
        name: volume-snapshot
        volume: vol4testcreatesnapshot
        snapshot: snapshotofvol4
        mdiskgrp: Pool0

- name: Using the IBM Spectrum Virtualize collection to prestart a Flash Copy Mapping
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: prestart a Flash Copy Mapping
      ibm_svc_volume_snapshot:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        state: prestart
        name: volume-snapshot
        volume: vol4testcreatesnapshot
        snapshot: snapshotofvol4
        restore: true

- name: Using the IBM Spectrum Virtualize collection to start a Flash Copy Mapping
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: start a Flash Copy Mapping
      ibm_svc_volume_snapshot:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        state: start
        name: volume-snapshot
        volume: vol4testcreatesnapshot
        snapshot: snapshotofvol4
        restore: true

- name: Using the IBM Spectrum Virtualize collection to stop a Flash Copy Mapping
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: stop a Flash Copy Mapping
      ibm_svc_volume_snapshot:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        state: stop
        name: volume-snapshot
        volume: vol4testcreatesnapshot
        snapshot: snapshotofvol4
        force: true

- name: Using the IBM Spectrum Virtualize collection to delete a Flash Copy Mapping
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete a Flash Copy Mapping for snapshot
      ibm_svc_volume_snapshot:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: volume-snapshot
        volume: vol4testcreatesnapshot
        snapshot: snapshotofvol4
        state: absent
        force: true
'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCSnapshot(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True,
                           choices=['absent', 'present', 'prestart', 'start',
                                    'stop']),
                mdiskgrp=dict(type='str', required=False),
                volume=dict(type='str', required=True),
                snapshot=dict(type='str', required=True),
                consistgrp=dict(type='str', required=False),
                grainsize=dict(type='str', required=False,
                               choices=['64', '256']),
                iogrp=dict(type='str', required=False),
                copyrate=dict(type='str', required=False, default='0'),
                cleanrate=dict(type='str', required=False, default='0'),
                keeptarget=dict(type='bool', required=False),
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
        self.volume = self.module.params['volume']
        self.snapshot = self.module.params['snapshot']

        # Optional
        self.mdiskgrp = self.module.params.get('mdiskgrp', None)
        self.consistgrp = self.module.params.get('consistgrp', None)
        self.grainsize = self.module.params.get('grainsize', None)
        self.iogrp = self.module.params.get('iogrp', None)
        self.copyrate = self.module.params.get('copyrate', '0')
        self.cleanrate = self.module.params.get('cleanrate', '0')
        self.keeptarget = self.module.params.get('keeptarget', False)
        self.restore = self.module.params.get('restore', False)
        self.prep = self.module.params.get('prep', False)
        self.force = self.module.params.get('force', False)
        self.split = self.module.params.get('split', False)
        self.autodelete = self.module.params.get('autodelete', 'off')

        # Store source vol info
        self.source_vol_info = {}

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def get_existing_snapshot(self):
        merged_result = {}
        self.log('Trying to get the snapshot %s', self.snapshot)
        data = self.restapi.svc_obj_info(cmd='lsvdisk', cmdopts=None,
                                         cmdargs=[self.snapshot])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    def get_fc_mapping(self):
        merged_result = {}
        self.log('Trying to get the fc mapping: %s', self.name)
        data = self.restapi.svc_obj_info(cmd='lsfcmap', cmdopts=None,
                                         cmdargs=[self.name])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    def get_info_from_source_volume(self):
        self.log("Getting info from source volume %s", self.volume)
        data = self.restapi.svc_obj_info(cmd='lsvdisk',
                                         cmdopts={'bytes': True},
                                         cmdargs=[self.volume])

        if not data:
            self.module.fail_json(msg="You must specify an "
                                      "existing source volume.")

        if isinstance(data, list):
            for d in data:
                self.source_vol_info.update(d)
        else:
            self.source_vol_info = data

    def target_volume_create(self):
        self.log("Creating target volume '%s'", self.snapshot)
        self.get_info_from_source_volume()

        # Make command
        cmd = 'mkvdisk'
        cmdopts = {}
        cmdopts['name'] = self.snapshot
        if self.mdiskgrp:
            cmdopts['mdiskgrp'] = self.mdiskgrp
        else:
            cmdopts['mdiskgrp'] = self.source_vol_info['mdisk_grp_name']
        cmdopts['size'] = self.source_vol_info['capacity']
        cmdopts['unit'] = 'b'
        cmdopts['rsize'] = '0%'
        cmdopts['autoexpand'] = True
        cmdopts['iogrp'] = self.source_vol_info['IO_group_name']

        self.log("Creating vdisk command %s opts %s", cmd, cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("Create target volume result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("Create target volume result message %s",
                     result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create target volume [%s]" % self.snapshot)

    def prestartfcmap(self):
        self.log("Prestart fc map for %s", self.name)
        cmd = 'prestartfcmap'
        cmdopts = {}
        if self.restore:
            cmdopts = {'restore': True}
        self.log("Prestartfcmap fc map %s opts %s", cmd, cmdopts)

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])
        self.log("Prestartfcmap fc map finished")

    def startfcmap(self):
        self.log("Start fc map for %s", self.name)
        cmd = 'startfcmap'
        cmdopts = {}
        if self.prep:
            cmdopts['prep'] = True
        if self.restore:
            cmdopts['restore'] = True
        self.log("Starting fc map %s opts %s", cmd, cmdopts)

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])
        self.log("Start fc map finished")

    def stopfcmap(self):
        self.log("Stop fc map for %s", self.name)
        cmd = 'stopfcmap'
        cmdopts = {}
        if self.force:
            cmdopts['force'] = True
        if self.split:
            cmdopts['split'] = True
        self.log("Stopping fc map %s opts %s", cmd, cmdopts)

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])
        self.log("Stop fc map finished")

    def rmfcmap(self):
        self.log("Delete fc map for %s", self.name)
        cmd = 'rmfcmap'
        cmdopts = {}
        if self.force:
            cmdopts['force'] = True
        self.log("Delete fc map %s opts %s", cmd, cmdopts)

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])
        self.log("Delete fc map finished")

    # TBD: Implement a more generic way to check for properties to modify.
    def flashcopymap_probe(self, data):
        props = {}
        self.log("Probe which properties need to be updated...")
        if self.consistgrp is not None and self.consistgrp != data['group_name']:
            props['consistgrp'] = self.consistgrp
        if self.copyrate != data['copy_rate']:
            props['copyrate'] = self.copyrate
        if self.cleanrate != data['clean_rate']:
            props['cleanrate'] = self.cleanrate
        if self.autodelete != data['autodelete']:
            props['autodelete'] = self.autodelete
        return props

    def flashcopymap_create(self):
        self.log("Checking the target volume...")
        data = self.get_existing_snapshot()
        if not data:
            self.target_volume_create()
        self.log("Creating flash copy mapping relationship'%s'", self.name)

        # Make command
        cmd = 'mkfcmap'
        cmdopts = {'name': self.name, 'source': self.volume,
                   'target': self.snapshot}
        if self.grainsize:
            cmdopts['grainsize'] = self.grainsize
        if self.keeptarget:
            cmdopts['keeptarget'] = True
        if self.consistgrp:
            cmdopts['consistgrp'] = self.consistgrp
        if self.iogrp:
            cmdopts['iogrp'] = self.iogrp
        cmdopts['copyrate'] = self.copyrate
        cmdopts['cleanrate'] = self.cleanrate
        if self.autodelete == 'on':
            cmdopts['autodelete'] = True
        self.log("Creating snapshot relationship command %s opts %s",
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

    def flashcopymap_update(self, modify):
        if modify:
            self.log("updating fcmap with properties %s", modify)
            cmd = 'chfcmap'
            cmdopts = {}
            for prop in modify:
                cmdopts[prop] = modify[prop]
            cmdargs = [self.name]

            self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

            # Any error will have been raised in svc_run_command
            # chfcmap does not output anything when successful.
            self.changed = True
        else:
            self.log("There is no property need to be updated")
            self.changed = False

    def flashcopymap_delete(self):
        self.log("Delete flash copy mapping '%s'", self.name)

        cmd = 'rmfcmap'
        cmdopts = {}
        if self.force:
            cmdopts['force'] = True
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # rmfcmap does not output anything when successful.
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = {}

        fcmap_data = self.get_fc_mapping()

        if fcmap_data:
            if self.state == 'absent':
                self.log("CHANGED: FlashCopy mapping exists,"
                         "requested state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chfcmap should be called
                modify = self.flashcopymap_probe(fcmap_data)
                if modify:
                    changed = True
            elif self.state in ['prestart', 'start', 'stop']:
                self.log("The state is %s", self.state)
                changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: FlashCopy mapping does not exist, "
                         "a new FlashCopy mapping will be created.")
                changed = True

        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not fcmap_data:
                        self.flashcopymap_create()
                        msg = ("FlashCopy mapping %s has been "
                               "created." % self.name)
                    else:
                        # This is where we would modify
                        self.flashcopymap_update(modify)
                        msg = ("FlashCopy mapping [%s] has "
                               "been modified." % self.name)
                elif self.state == 'absent':
                    self.flashcopymap_delete()
                    msg = ("FlashCopy mapping [%s] has been "
                           "deleted." % self.name)
                elif self.state == 'prestart':
                    self.prestartfcmap()
                    msg = ("FlashCopy mapping [%s] has been "
                           "prestarted." % self.name)
                elif self.state == 'start':
                    self.startfcmap()
                    msg = ("FlashCopy mapping [%s] has been "
                           "started." % self.name)
                elif self.state == 'stop':
                    self.stopfcmap()
                    msg = ("FlashCopy mapping [%s] has been "
                           "stopped." % self.name)
        else:
            self.log("Exiting with no changes")
            if self.state in ['absent', 'prestart', 'start', 'stop']:
                msg = "FlashCopy mapping [%s] did not exist." % self.name
            else:
                msg = "FlashCopy mapping [%s] already exists." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCSnapshot()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
