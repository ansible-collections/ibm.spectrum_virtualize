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
module: ibm_svc_vol_map
short_description: This module manages volume mapping on IBM Spectrum
                   Virtualize Family storage systems.
description:
  - Ansible interface to manage volume mapping commands
    'mkvdiskhostmap' and 'rmvdiskhostmap' commands.
version_added: "2.10"
options:
  volname:
    description:
      - Specifies the volume name for host mapping
    required: true
    type: str
  host:
    description:
      - Specifies the host name for host mapping
    required: true
    type: str
  state:
    description:
      - Creates (C(present)) or removes (C(absent)) a volume mapping
    choices: [ absent, present ]
    required: true
    type: str
  clustername:
    description:
      - The hostname or management IP of the
        Spectrum Virtualize storage system
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
  log_path:
    description:
    - Path of debug log file
    type: str
  validate_certs:
    description:
    - Validates certification
    type: bool
author:
    - Peng Wang(@wangpww)
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to map a volume to a host
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: map volume to host
      ibm_svc_vol_map:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        volname: volume0
        host: host4test
        state: present

- name: Using the IBM Spectrum Virtualize collection to unmap a volume from a host
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: unmap volume from host
      ibm_svc_vol_map:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/playbook.debug
        volname: volume0
        host: host4test
        state: absent
'''
RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCvdiskhostmap(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                volname=dict(type='str', required=True),
                host=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.volname = self.module.params['volname']
        self.host = self.module.params['host']
        self.state = self.module.params['state']

        # Optional

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def get_existing_vdiskhostmap(self):
        merged_result = []

        data = self.restapi.svc_obj_info(cmd='lsvdiskhostmap', cmdopts=None,
                                         cmdargs=[self.volname])

        if isinstance(data, list):
            for d in data:
                merged_result.append(d)
        elif data:
            merged_result = [data]

        return merged_result

    # TBD: Implement a more generic way to check for properties to modify.
    def vdiskhostmap_probe(self, mdata):
        props = []
        self.log("vdiskhostmap_probe props='%s'", mdata)
        # TBD: The parameter is easytier but the view has easy_tier label.
        mapping_exist = False
        for data in mdata:
            if (self.host == data['host_name']) and (self.volname == data['name']):
                mapping_exist = True

        if not mapping_exist:
            props += ["map"]

        if props is []:
            props = None

        self.log("vdiskhostmap_probe props='%s'", props)
        return props

    def vdiskhostmap_create(self):
        if self.module.check_mode:
            self.changed = True
            return

        if not self.volname:
            self.module.fail_json(msg="You must pass in "
                                      "volname to the module.")
        if not self.host:
            self.module.fail_json(msg="You must pass in host "
                                      "name to the module.")

        self.log("creating vdiskhostmap '%s' '%s'", self.volname, self.host)

        # Make command
        cmd = 'mkvdiskhostmap'
        cmdopts = {'force': True}
        cmdopts['host'] = self.host
        cmdargs = [self.volname]

        self.log("creating vdiskhostmap command %s opts %s args %s",
                 cmd, cmdopts, cmdargs)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
        self.log("create vdiskhostmap result %s", result)

        if 'message' in result:
            self.changed = True
            self.log("create vdiskhostmap result message %s",
                     result['message'])
        else:
            self.module.fail_json(msg="Failed to create vdiskhostmap.")

    def vdiskhostmap_update(self, modify):
        # vdiskhostmap_update() doesn't actually update anything as of now, it is here just as a placeholder.
        # update the vdiskhostmap
        self.log("updating vdiskhostmap")

        if 'host_name' in modify:
            self.log("host name is changed.")

        if 'volname' in modify:
            self.log("vol name is changed.")

        self.changed = True

    def vdiskhostmap_delete(self):
        self.log("deleting vdiskhostmap '%s'", self.volname)

        cmd = 'rmvdiskhostmap'
        cmdopts = {}
        cmdopts['host'] = self.host
        cmdargs = [self.volname]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmvdisk does not output anything when successful.
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = []

        vdiskhostmap_data = self.get_existing_vdiskhostmap()
        self.log("volume mapping data is : '%s'", vdiskhostmap_data)

        if vdiskhostmap_data:
            if self.state == 'absent':
                self.log("vdiskhostmap exists, "
                         "and requested state is 'absent'")
                changed = True
            elif self.state == 'present':
                probe_data = self.vdiskhostmap_probe(vdiskhostmap_data)
                if probe_data:
                    self.log("vdiskhostmap does not exist, but requested state is 'present'")
                    changed = True
        else:
            if self.state == 'present':
                self.log("vdiskhostmap does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.module.check_mode:
                self.log('skipping changes due to check mode')
                msg = 'skipping changes due to check mode'
            else:
                if self.state == 'present':
                    self.vdiskhostmap_create()
                    msg = "vdiskhostmap %s %s has been created." % (
                        self.volname, self.host)
                elif self.state == 'absent':
                    self.vdiskhostmap_delete()
                    msg = "vdiskhostmap [%s] has been deleted." % self.volname
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "vdiskhostmap [%s] did not exist." % self.volname
            else:
                msg = "vdiskhostmap [%s] already exists." % self.volname

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCvdiskhostmap()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
