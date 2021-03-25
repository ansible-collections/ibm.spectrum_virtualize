#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 IBM CORPORATION
# Author(s): Rohit Kumar <rohit.kumar6@ibm.com>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: ibm_svc_manage_mirrored_volume
short_description: This module manages mirrored volumes on IBM Spectrum Virtualize
                   Family storage systems.
description:
  - Ansible interface to manage 'mkvolume', 'addvolumecopy', 'rmvolumecopy' and 'rmvolume' volume commands.
version_added: "2.10.0"
options:
  name:
    description:
      - Specifies the name to assign to the new volume.
    required: true
    type: str
  state:
    description:
      - Creates (C(present)) or removes (C(absent)) a mirrored volume.
    choices: [ absent, present ]
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
  poolA:
    description:
    - Specifies the name of first storage pool to be used when
      creating a mirrored volume.
    type: str
  poolB:
    description:
    - Specifies the name of second storage pool to be used when
      creating a mirrored volume.
    type: str
  type:
    description:
    - Specifies the desired volume type. When the type is "local hyperswap",
      a HyperSwap volume gets created. When the type is "standard" and
      values for "PoolA" and "PoolB" are also specified,
      a "standard mirror" volume gets created.
      If a "standard" mirrored volume exists and either "PoolA" or "PoolB"
      is specified, the mirrored volume gets converted to a standard volume.
    choices: [ local hyperswap, standard ]
    required: false
    type: str
  thin:
    description:
    - Specifies if the volume to be created is thin-provisioned.
    type: bool
  compressed:
    description:
    - Specifies if the volume to be created is compressed.
    type: bool
  deduplicated:
    description:
    - Specifies if the volume to be created is deduplicated.
    type: bool
  grainsize:
    description:
    - Specifies the grain size (in KB) to use when
      creating the HyperSwap volume.
    type: str
  rsize:
    description:
    - Specifies the rsize in %. Defines how much physical space
      is initially allocated to the thin-provisioned or compressed volume.
    type: str
  size:
    description:
    - Specifies the size of mirrored volume in MB.
    type: str
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
    - Rohit Kumar(@rohitk-github)
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to create a HyperSwap volume
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create a HyperSwap volume
      ibm_svc_manage_mirrored_volume:
        clustername: "{{clustername}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        type: "local hyperswap"
        name: "{{vol_name}}"
        state: present
        poolA: "{{pool_name1}}"
        poolB: "{{pool_name2}}"
        size: "1024"

- name: Using the IBM Spectrum Virtualize collection to create a thin-provisioned HyperSwap volume
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create a thin-provisioned HyperSwap volume
      ibm_svc_manage_mirrored_volume:
        clustername: "{{clustername}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        type: "local hyperswap"
        name: "{{vol_name}}"
        state: present
        poolA: "{{pool_name1}}"
        poolB: "{{pool_name2}}"
        size: "1024"
        thin: true

- name: Using the IBM Spectrum Virtualize collection to delete a mirrored volume
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Delete a mirrored volume
      ibm_svc_manage_mirrored_volume:
        clustername: "{{clustername}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        name: "{{vol_name}}"
        state: absent

- name: Using the IBM Spectrum Virtualize collection to create standard mirror volume
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Create a standard mirror volume
      block:
        - name: Create Volume
          ibm_svc_manage_mirrored_vol:
            clustername: "{{clustername}}"
            username: "superuser"
            password: "passw0rd"
            log_path: /tmp/playbook.debug
            name: "{{vol_name}}"
            state: present
            type: "standard"
            poolA: "{{pool_name1}}"
            poolB: "{{pool_name2}}"
'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCvolume(object):
    def __init__(self):
        argument_spec = svc_argument_spec()
        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                poolA=dict(type='str', required=False),
                poolB=dict(type='str', required=False),
                size=dict(type='str', required=False),
                thin=dict(type='bool', required=False),
                type=dict(type='str', required=False, choices=['local hyperswap', 'standard']),
                grainsize=dict(type='str', required=False),
                rsize=dict(type='str', required=False),
                compressed=dict(type='bool', required=False),
                deduplicated=dict(type='bool', required=False)

            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)
        self.vdisk_type = ""
        self.discovered_poolA = ""
        self.discovered_poolB = ""
        self.discovered_standard_vol_pool = ""
        self.rmvolumecopy_flag = ""
        self.addvolumecopy_flag = ""
        self.addvdiskcopy_flag = ""
        self.discovered_poolA_site = ""
        self.discovered_poolB_site = ""
        self.removefrompool_site = ""
        self.changed = ""
        self.poolA_data = ""
        self.poolB_data = ""

        # logging setup
        log_path = self.module.params.get('log_path')
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.name = self.module.params.get('name')
        self.state = self.module.params.get('state')

        if not self.name:
            self.module.fail_json(msg="Missing mandatory parameter: name")
        if not self.state:
            self.module.fail_json(msg="Missing mandatory parameter: state")

        # Optional
        self.poolA = self.module.params.get('poolA')
        self.poolB = self.module.params.get('poolB')
        self.size = self.module.params.get('size')
        self.type = self.module.params.get('type')
        self.compressed = self.module.params.get('compressed')
        self.thin = self.module.params.get('thin')
        self.deduplicated = self.module.params.get('deduplicated')
        self.rsize = self.module.params.get('rsize')
        self.grainsize = self.module.params.get('grainsize')

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params.get('clustername'),
            domain=self.module.params.get('domain'),
            username=self.module.params.get('username'),
            password=self.module.params.get('password'),
            validate_certs=self.module.params.get('validate_certs'),
            log_path=log_path
        )

    def get_existing_vdisk(self):
        self.log("Entering function get_existing_vdisk")
        cmd = 'lsvdisk'
        cmdargs = {}
        cmdopts = {'bytes': True}
        cmdargs = [self.name]
        existing_vdisk_data = self.restapi.svc_obj_info(cmd, cmdopts, cmdargs)
        return existing_vdisk_data

    def basic_checks(self):
        self.log("Entering function basic_checks")
        if self.poolA:
            self.poolA_data = self.restapi.svc_obj_info(cmd='lsmdiskgrp', cmdopts=None, cmdargs=[self.poolA])
            if not self.poolA_data:
                self.module.fail_json(msg="PoolA does not exist")
        if self.poolB:
            self.poolB_data = self.restapi.svc_obj_info(cmd='lsmdiskgrp', cmdopts=None, cmdargs=[self.poolB])
            if not self.poolB_data:
                self.module.fail_json(msg="PoolB does not exist")
        if self.state == "present" and not self.type:
            self.module.fail_json(msg="missing required argument: type")
        if self.poolA and self.poolB:
            if self.poolA == self.poolB:
                self.module.fail_json(msg="poolA and poolB cannot be same")
            siteA, siteB = self.discover_site_from_pools()
            if siteA != siteB and self.type == "standard":
                self.module.fail_json(msg="To create Standard Mirrored volume, provide pools belonging to same site.")
        if not self.poolA and not self.poolB and self.state == "present":
            self.module.fail_json(msg="Both poolA and poolB cannot be empty")

    def discover_pools(self, data):
        # Discover pool(s) where the volume resides, this function is called if the volume already exists
        self.log("Entering function discover_pools")
        is_std_mirrored_vol = False
        is_hs_vol = False
        if data[0]['type'] == "many":
            is_std_mirrored_vol = True
            self.discovered_poolA = data[1]['mdisk_grp_name']
            self.discovered_poolB = data[2]['mdisk_grp_name']
            self.log("The discovered standard mirrored volume \"%s\" belongs to \
                pools \"%s\" and \"%s\"", self.name, self.discovered_poolA, self.discovered_poolB)

        relationship_name = data[0]['RC_name']
        if relationship_name:
            rel_data = self.restapi.svc_obj_info(cmd='lsrcrelationship', cmdopts=None, cmdargs=[relationship_name])
            if rel_data['copy_type'] == "activeactive":
                is_hs_vol = True
            if is_hs_vol:
                master_vdisk = rel_data['master_vdisk_name']
                aux_vdisk = rel_data['aux_vdisk_name']
                master_vdisk_data = self.restapi.svc_obj_info(cmd='lsvdisk', cmdopts=None, cmdargs=[master_vdisk])
                aux_vdisk_data = self.restapi.svc_obj_info(cmd='lsvdisk', cmdopts=None, cmdargs=[aux_vdisk])
                if is_std_mirrored_vol:
                    self.discovered_poolA = master_vdisk_data[1]['mdisk_grp_name']
                    self.discovered_poolB = aux_vdisk_data[1]['mdisk_grp_name']
                    self.log("The discovered mixed volume \"%s\" belongs to pools \"%s\" and \"%s\"", self.name, self.discovered_poolA, self.discovered_poolB)
                else:
                    self.discovered_poolA = master_vdisk_data[0]['mdisk_grp_name']
                    self.discovered_poolB = aux_vdisk_data[0]['mdisk_grp_name']
                    self.log("The discovered HyperSwap volume \"%s\" belongs to pools\
                     \"%s\" and \"%s\"", self.name, self.discovered_poolA, self.discovered_poolB)

        if is_std_mirrored_vol and is_hs_vol:
            self.module.fail_json(msg="Unsupported Configuration: Both HyperSwap and Standard Mirror \
are configured on this volume")
        elif is_hs_vol:
            self.vdisk_type = "local hyperswap"
        elif is_std_mirrored_vol:
            self.vdisk_type = "standard mirror"
        if not is_std_mirrored_vol and not is_hs_vol:
            mdisk_grp_name = data[0]['mdisk_grp_name']
            self.discovered_standard_vol_pool = mdisk_grp_name
            self.vdisk_type = "standard"
            self.log("The standard volume %s belongs to pool \"%s\"", self.name, self.discovered_standard_vol_pool)

    def discover_site_from_pools(self):
        self.log("Entering function discover_site_from_pools")
        poolA_site = self.poolA_data['site_name']
        poolB_site = self.poolB_data['site_name']
        return poolA_site, poolB_site

    def verify_mirror_vol_pool(self):
        self.log("Entering function verify_mirror_vol_pool")
        if self.type == "local hyperswap" and self.vdisk_type == "standard mirror":
            self.module.fail_json(msg="You cannot "
                                      "update the topolgy from standard mirror to HyperSwap")

        if self.poolA and self.poolB:
            if self.vdisk_type == "local hyperswap" and self.type == "standard":
                self.module.fail_json(msg="HyperSwap Volume cannot be converted to standard mirror")
            if self.vdisk_type == "standard mirror" or self.vdisk_type == "local hyperswap":
                if (self.poolA == self.discovered_poolA or self.poolA == self.discovered_poolB)\
                   and (self.poolB == self.discovered_poolA or self.poolB == self.discovered_poolB):
                    self.changed = False
                    return
                else:
                    self.module.fail_json(msg="Pools for Standard Mirror or HyperSwap volume cannot be updated")
            elif self.vdisk_type == "standard" and self.type == "local hyperswap":
                # input poolA or poolB must belong to given Volume
                if self.poolA == self.discovered_standard_vol_pool or self.poolB == self.discovered_standard_vol_pool:
                    self.addvolumecopy_flag = True
                    self.changed = True
                else:
                    self.module.fail_json(msg="One of the input pools must belong to the Volume")
            elif self.vdisk_type == "standard" and self.type == "standard":
                if self.poolA == self.discovered_standard_vol_pool or self.poolB == self.discovered_standard_vol_pool:
                    self.addvdiskcopy_flag = True
                    self.changed = True
                else:
                    self.module.fail_json(msg="One of the input pools must belong to the Volume")

        elif not self.poolA or not self.poolB:
            if self.vdisk_type == "standard":
                if self.poolA == self.discovered_standard_vol_pool or self.poolB == self.discovered_standard_vol_pool:
                    self.log("Standard Volume already exists, no modifications done")
                    return
            if self.poolA:
                if self.poolA == self.discovered_poolA or self.poolA == self.discovered_poolB:
                    self.rmvolumecopy_flag = True
                    self.changed = True
                else:
                    self.module.fail_json(msg="One of the input pools must belong to the Volume")
            elif self.poolB:
                if self.poolB == self.discovered_poolA or self.poolB == self.discovered_poolB:
                    self.rmvolumecopy_flag = True
                    self.changed = True
                else:
                    self.module.fail_json(msg="One of the input pools must belong to the Volume")
        if not self.poolA or not self.poolB:
            if (self.system_topology == "hyperswap" and self.type == "local hyperswap"):
                self.module.fail_json(msg="Type must be standard if either PoolA or PoolB is not specified.")

    def vdisk_probe(self, data):
        self.log("Entering function vdisk_probe")
        if self.size:
            size_in_bytes = int(self.size) * 1024 * 1024
            if str(size_in_bytes) != data[0]['capacity']:
                self.module.fail_json(msg="You cannot update the parameter: size")

    def volume_create(self):
        self.log("Entering function volume_create")
        if self.module.check_mode:
            self.changed = True
            return
        if not self.size:
            self.module.fail_json(msg="You must pass in size to the module.")
        if not self.type:
            self.module.fail_json(msg="You must pass type to the module.")
        self.log("creating Volume '%s'", self.name)
        # Make command
        cmd = 'mkvolume'
        cmdopts = {}
        if self.poolA and self.poolB:
            cmdopts['pool'] = self.poolA + ":" + self.poolB
        if self.size:
            cmdopts['size'] = self.size
            cmdopts['unit'] = "mb"
        if self.grainsize:
            cmdopts['grainsize'] = self.grainsize
        if self.thin and self.rsize:
            cmdopts['thin'] = self.thin
            cmdopts['buffersize'] = self.rsize
        elif self.thin:
            cmdopts['thin'] = self.thin
        elif self.rsize and not self.thin:
            self.module.fail_json(msg="To configure 'rsize', parameter 'thin' should be passed and the value should be 'true'.")
        if self.compressed:
            cmdopts['compressed'] = self.compressed
        if self.thin:
            cmdopts['thin'] = self.thin
        if self.deduplicated:
            cmdopts['deduplicated'] = self.deduplicated
        cmdopts['name'] = self.name
        self.log("creating volume command %s opts %s", cmd, cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("create volume result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("create volume result message %s", result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create volume [%s]" % self.name)

    def vdisk_create(self):
        self.log("Entering function vdisk_create")
        if self.module.check_mode:
            self.changed = True
            return
        if not self.size:
            self.module.fail_json(msg="You must pass in size to the module.")
        if not self.type:
            self.module.fail_json(msg="You must pass type to the module.")
        self.log("creating Volume '%s'", self.name)
        # Make command
        cmd = 'mkvdisk'
        cmdopts = {}
        if self.poolA and self.poolB:
            cmdopts['mdiskgrp'] = self.poolA + ":" + self.poolB
        if self.size:
            cmdopts['size'] = self.size
            cmdopts['unit'] = "mb"
        if self.compressed:
            cmdopts['compressed'] = self.compressed
        if self.thin and self.rsize:
            cmdopts['rsize'] = self.rsize
        elif self.thin:
            cmdopts['rsize'] = "2%"
        elif self.rsize and not self.thin:
            self.module.fail_json(msg="To configure 'rsize', parameter 'thin' should be passed and the value should be 'true.'")
        if self.grainsize:
            cmdopts['grainsize'] = self.grainsize
        if self.deduplicated:
            cmdopts['deduplicated'] = self.deduplicated
        cmdopts['name'] = self.name
        cmdopts['copies'] = 2
        self.log("creating volume command %s opts %s", cmd, cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("create volume result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("create volume result message %s", result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create Volume [%s]" % self.name)

    def addvolumecopy(self):
        self.log("Entering function addvolumecopy")
        cmd = 'addvolumecopy'
        cmdopts = {}
        if self.compressed:
            cmdopts['compressed'] = self.compressed
        if self.grainsize:
            cmdopts['grainsize'] = self.grainsize
        if self.thin and self.rsize:
            cmdopts['thin'] = self.thin
            cmdopts['buffersize'] = self.rsize
        elif self.thin:
            cmdopts['thin'] = self.thin
        elif self.rsize and not self.thin:
            self.module.fail_json(msg="To configure 'rsize', parameter 'thin' should be passed and the value should be 'true'.")
        if self.deduplicated:
            cmdopts['deduplicated'] = self.deduplicated
        if self.size:
            self.module.fail_json(msg="Invalid Parameter: size")
        if self.poolA and (self.poolB == self.discovered_standard_vol_pool and self.poolA != self.discovered_standard_vol_pool):
            cmdopts['pool'] = self.poolA
        elif self.poolB and (self.poolA == self.discovered_standard_vol_pool and self.poolB != self.discovered_standard_vol_pool):
            cmdopts['pool'] = self.poolB

        cmdargs = [self.name]
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
        self.changed = True

    def addvdiskcopy(self):
        self.log("Entering function addvdiskcopy")
        cmd = 'addvdiskcopy'
        cmdopts = {}
        if self.size:
            self.module.fail_json(msg="Invalid Parameter: size")
        siteA, siteB = self.discover_site_from_pools()
        if siteA != siteB:
            self.module.fail_json(msg="To create Standard Mirrored volume, provide pools belonging to same site.")
        if self.poolA and (self.poolB == self.discovered_standard_vol_pool and self.poolA != self.discovered_standard_vol_pool):
            cmdopts['mdiskgrp'] = self.poolA
        elif self.poolB and (self.poolA == self.discovered_standard_vol_pool and self.poolB != self.discovered_standard_vol_pool):
            cmdopts['mdiskgrp'] = self.poolB
        else:
            self.module.fail_json(msg="One of the input pools must belong to the volume")
        if self.compressed:
            cmdopts['compressed'] = self.compressed
        if self.grainsize:
            cmdopts['grainsize'] = self.grainsize
        if self.thin and self.rsize:
            cmdopts['rsize'] = self.rsize
        elif self.thin:
            cmdopts['rsize'] = "2%"
        elif self.rsize and not self.thin:
            self.module.fail_json(msg="To configure 'rsize', parameter 'thin' should be passed and the value should be 'true'.")

        if self.deduplicated:
            cmdopts['deduplicated'] = self.deduplicated

        cmdargs = [self.name]
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
        self.changed = True

    def rmvolumecopy(self):
        self.log("Entering function rmvolumecopy")
        cmd = 'rmvolumecopy'
        if self.size:
            self.module.fail_json(msg="Invalid Parameter: size")
        if self.rsize:
            self.module.fail_json(msg="Invalid Parameter: rsize")
        if self.thin:
            self.module.fail_json(msg="Invalid Parameter: thin")
        if self.deduplicated:
            self.module.fail_json(msg="Invalid Parameter: deduplicated")
        if self.compressed:
            self.module.fail_json(msg="Invalid Parameter: compressed")
        cmdopts = {}
        if not self.poolA:
            if (self.poolB != self.discovered_poolA):
                cmdopts['pool'] = self.discovered_poolA
            else:
                cmdopts['pool'] = self.discovered_poolB
        elif not self.poolB:
            if (self.poolA != self.discovered_poolB):
                cmdopts['pool'] = self.discovered_poolB
            else:
                cmdopts['pool'] = self.discovered_poolA
        cmdargs = [self.name]
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
        self.changed = True

    def vdisk_update(self):
        self.log("Entering function vdisk_update")
        if self.addvolumecopy_flag:
            self.addvolumecopy()
        elif self.addvdiskcopy_flag:
            self.addvdiskcopy()
        elif self.rmvolumecopy_flag:
            self.rmvolumecopy()

    def volume_delete(self):
        self.log("Entering function volume_delete")
        self.log("deleting volume '%s'", self.name)

        cmd = 'rmvolume'
        cmdopts = None
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmvdisk does not output anything when successful.
        self.changed = True

    def discover_system_topology(self):
        self.log("Entering function discover_system_topology")
        system_data = self.restapi.svc_obj_info(cmd='lssystem', cmdopts=None, cmdargs=None)
        sys_topology = system_data['topology']
        return sys_topology

    def apply(self):
        self.log("Entering function apply")
        changed = False
        msg = None
        self.basic_checks()
        self.system_topology = self.discover_system_topology()
        if self.system_topology == "standard" and self.type == "local hyperswap":
            self.module.fail_json(msg="The system topology is Standard, HyperSwap actions are not supported.")
        vdisk_data = self.get_existing_vdisk()
        if vdisk_data:
            # Discover the pool(s) belonging to the Volume
            self.discover_pools(vdisk_data)
            if self.state == 'absent':
                self.log("CHANGED: volume exists, but requested "
                         "state is 'absent'")
                changed = True
            elif self.state == 'present':
                self.verify_mirror_vol_pool()
            if not self.changed or not changed:
                self.vdisk_probe(vdisk_data)
        else:
            if self.state == 'present':
                if self.poolA and self.poolB:
                    self.log("CHANGED: volume does not exist, but requested state is 'present'")
                    changed = True
                else:
                    self.module.fail_json(msg="Volume does not exist, To create a Mirrored volume (standard mirror or HyperSwap), \
You must pass in poolA and poolB to the module.")

        if changed or self.changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not vdisk_data:
                        # create_vdisk_flag = self.discover_site_from_pools()
                        if self.type == "standard":
                            self.vdisk_create()
                            msg = "Standard Mirrored Volume %s has been created." % self.name
                        elif self.type == "local hyperswap":
                            # if not create_vdisk_flag:
                            self.volume_create()
                            msg = "HyperSwap Volume %s has been created." % self.name
                    else:
                        # This is where we would modify if required
                        self.vdisk_update()
                        msg = "Volume [%s] has been modified." % self.name
                elif self.state == 'absent':
                    self.volume_delete()
                    msg = "Volume [%s] has been deleted." % self.name
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "Volume %s did not exist." % self.name
            else:
                msg = self.vdisk_type + " Volume [%s] already exists, no modifications done" % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCvolume()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
