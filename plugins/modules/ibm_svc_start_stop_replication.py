#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 IBM CORPORATION
# Author(s): Rohit Kumar <rohit.kumar6@ibm.com>
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
module: ibm_svc_start_stop_replication
short_description: This module starts or stops remote copies on
                   IBM Spectrum Virtualize Family storage systems.
version_added: "2.10.0"

description:
  - Ansible interface to manage remote copy related commands.

options:
  name:
    description:
      - Specifies a name to assign to the new remote copy relationship or group,
        or to operate on the existing remote copy.
    required: false
    type: str
  state:
    description:
      - Starts (C(started)), stops (C(stopped)) a
        remote copy relationship.
    choices: [started, stopped]
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
  primary:
    description:
    - Specifies the copy direction by defining which disk
      becomes the primary (source).
      Applies when state is 'started'.
    type: str
    choices: [ 'master', 'aux' ]
  isgroup:
    description:
    - Specifies that a consistency group has to be started or stopped.
    default: false
    type: bool
  clean:
    description:
    - Specifies that the volume that is to become a secondary is clean.
      Applies when state is 'started'.
    default: false
    type: bool
  access:
    description:
    - Instructs the system to allow write access to a consistent secondary volume.
      Applies when state is 'stopped'.
    default: false
    type: bool
  force:
    description:
    - Specifies that the system must process the copy operation even if it
      causes a temporary loss of consistency during synchronization.
      Applies when state is 'started'.
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
    - rohit(@rohitk-github)
'''

EXAMPLES = '''
- name: Using Spectrum Virtualize collection for data replication
  hosts: localhost
  gather_facts: no
  vars:
    clustername: x.x.x.x
    username: username
    password: password
  collections:
    - ibm.spectrum_virtualize
  connection: local
  tasks:
    - name: Start remote copy
      ibm_svc_start_stop_replication:
        name: sample_rcopy
        clustername: "{{clustername}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/ansible.log
        state: started
        clean: true

    - name: Stop remote copy
      ibm_svc_start_stop_replication:
        name: sample_rcopy
        clustername: "{{clustername}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/ansible.log
        state: stopped

'''
RETURN = '''
'''


from ansible.module_utils._text import to_native
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils.basic import AnsibleModule
from traceback import format_exc


class IBMSVCStartStopReplication(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str'),
                state=dict(type='str',
                           required=True,
                           choices=['started', 'stopped']),
                force=dict(type='bool', required=False),
                primary=dict(type='str', choices=['master', 'aux']),
                clean=dict(type='bool', default=False),
                access=dict(type='bool', default=False),
                isgroup=dict(type='bool', default=False),
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
        self.primary = self.module.params.get('primary', None)
        self.clean = self.module.params.get('clean', False)
        self.access = self.module.params.get('access', False)
        self.force = self.module.params.get('force', False)
        self.isgroup = self.module.params.get('isgroup', False)

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def existing_rc(self):
        """
        find the remote copy relationships such as Metro Mirror, Global Mirror
        relationships visible to the system.

        Returns:
            None if no matching instances or a list including all the matching
            instances
        """
        self.log('Trying to get the remote copy relationship %s', self.name)
        data = self.restapi.svc_obj_info(cmd='lsrcrelationship',
                                             cmdopts=None, cmdargs=[self.name])

        return data

    def existing_rccg(self):
        """
        find the remote copy consistency group visible to the system.

        Returns:
            None if no matching instances or a list including all the matching
            instances
        """
        data_cg = {}
        self.log('Trying to get the remote copy cg %s', self.name)
        data = self.restapi.svc_obj_info(cmd='lsrcconsistgrp',
                                             cmdopts=None, cmdargs=[self.name])
        if isinstance(data, list):
            data_cg = data[0]
        elif isinstance(data, dict):
            data_cg = data
        return data_cg

    def start(self):
        """
        Starts the Metro Mirror or Global Mirror relationship copy process, set
        the direction of copy if undefined, and (optionally) mark the secondary
        volume of the relationship as clean. The relationship must be a
        stand-alone relationship.
        """
        cmdopts = {}
        self.log("self.primary is %s", self.primary)
        if self.primary:
            cmdopts['primary'] = self.primary
        if self.clean:
            cmdopts['clean'] = self.clean
        if self.force:
            cmdopts['force'] = self.force
        if self.isgroup:
            result = self.restapi.svc_run_command(cmd='startrcconsistgrp',
                                                  cmdopts=cmdopts,
                                                  cmdargs=[self.name])
            if result == '':
                self.changed = True
                self.log("succeeded to start the remote copy group %s", self.name)
            elif 'message' in result:
                self.changed = True
                self.log("start the remote copy group %s with result message %s", self.name, result['message'])
            else:
                msg = "Failed to start the remote copy group [%s]" % self.name
                self.module.fail_json(msg=msg)
        else:
            result = self.restapi.svc_run_command(cmd='startrcrelationship',
                                                  cmdopts=cmdopts,
                                                  cmdargs=[self.name])
            self.log("start the rcrelationship %s with result %s", self.name, result)
            if result == '':
                self.changed = True
                self.log("succeeded to start the remote copy %s", self.name)
            elif 'message' in result:
                self.changed = True
                self.log("start the rcrelationship %s with result message %s", self.name, result['message'])
            else:
                msg = "Failed to start the rcrelationship [%s]" % self.name
                self.module.fail_json(msg=msg)

    def stop(self):
        """
        Stops the copy process for a Metro Mirror or Global Mirror stand-alone
        relationship.
        """
        cmdopts = {}
        if self.access:
            cmdopts['access'] = self.access
        if self.isgroup:
            result = self.restapi.svc_run_command(cmd='stoprcconsistgrp',
                                                  cmdopts=cmdopts,
                                                  cmdargs=[self.name])
            self.log("stop the remote copy group %s with result %s", self.name, result)
            if result == '':
                self.changed = True
                self.log("succeeded to stop the remote copy group %s", self.name)
            elif 'message' in result:
                self.changed = True
                self.log("stop the remote copy group %s with result message %s", self.name, result['message'])
            else:
                msg = "Failed to stop the rcrelationship [%s]" % self.name
                self.module.fail_json(msg=msg)
        else:
            result = self.restapi.svc_run_command(cmd='stoprcrelationship', cmdopts=cmdopts, cmdargs=[self.name])
            self.log("stop the rcrelationship %s with result %s", self.name, result)
            if result == '':
                self.changed = True
                self.log("succeeded to stop the remote copy %s", self.name)
            elif 'message' in result:
                self.changed = True
                self.log("stop the rcrelationship %s with result message %s", self.name, result['message'])
            else:
                msg = "Failed to stop the rcrelationship [%s]" % self.name
                self.module.fail_json(msg=msg)

    def apply(self):
        changed = False
        msg = None
        self.log("self state is %s", self.state)
        if not self.isgroup:
            rcrelationship_data = self.existing_rc()
        else:
            rcrelationship_data = self.existing_rccg()
        if self.module.check_mode:
            self.log('skipping changes due to check mode.')
            msg = 'skipping changes due to check mode.'
        else:
            if self.state == 'started':
                self.start()
                changed = True
                if not self.isgroup:
                    msg = "remote copy [%s] has been started." % self.name
                else:
                    msg = "remote copy group [%s] has been started." % self.name
            elif self.state == 'stopped':
                self.stop()
                changed = True
                if not self.isgroup:
                    msg = "remote copy [%s] has been stopped." % self.name
                else:
                    msg = "remote copy group [%s] has been stopped." % self.name
            else:
                msg = "Invalid %s state. Supported states are 'started' and 'stopped'" % self.state

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCStartStopReplication()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
