#!/usr/bin/python
# Copyright (C) 2020 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
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
module: ibm_svcinfo_command
short_description: This module implements SSH Client which helps to run
                   svcinfo CLI command on IBM Spectrum Virtualize Family storage systems.
version_added: "2.10"
description:
- Runs single svcinfo CLI command on IBM Spectrum Virtualize Family storage systems.
  Filter options like filtervalue or pipe '|' with grep, awk, and others are
  not supported in the command in this module.
  Paramiko must be installed to use this module.
author:
    - Shilpi Jain (@Shilpi-Jain1)
options:
  command:
    description:
    - Single svcinfo CLI command to be executed on Spectrum Virtualize storage system.
      Each command must start with svcinfo keyword.
    type: str
  usesshkey:
    description:
    - For key-pair based SSH connection, set this field as "yes".
      Provide full path of keyfile in key_filename field.
      If not provided, default path of SSH key is used.
    type: str
    choices: [ 'yes', 'no']
    default: 'no'
  key_filename:
    description:
    - SSH client private key filename. By default, ~/.ssh/id_rsa is used.
    required: false
    type: str
  clustername:
    description:
    - The hostname or management IP of the
      Spectrum Virtualize storage system
    type: str
    required: true
  username:
    description:
    - Username for the Spectrum Virtualize storage system
    required: true
    type: str
  password:
    description:
    - Password for the Spectrum Virtualize storage system
    required: true
    type: str
  log_path:
    description:
    - Path of debug log file
    type: str
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to run svcinfo CLI command
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  vars:
    - user: user1
  tasks:
    - name: Run CLI command using SSH client with password.
      ibm_svcinfo_command:
        command: "svcinfo lsuser {{user}}"
        clustername: "{{clustername}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/ansible.log

- name: Using the IBM Spectrum Virtualize collection to run svcinfo CLI command using password-less SSH connection
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Run CLI command using password-less SSH Client
      ibm_svcinfo_command:
        command: "svcinfo lsuser"
        usesshkey: "yes"
        clustername: "{{clustername}}"
        username: "{{username}}"
        password:
        log_path: /tmp/ansible.log
'''

RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import svc_ssh_argument_spec, get_logger
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_ssh import IBMSVCssh
from ansible.module_utils._text import to_native


class IBMSVCsshClient(object):
    def __init__(
            self,
            timeout=30,
            cmd_timeout=30.0):
        """
        Constructor for SSH client class.
        """

        argument_spec = svc_ssh_argument_spec()

        argument_spec.update(
            dict(
                command=dict(type='str', required=False),
                usesshkey=dict(type='str', required=False, default='no', choices=['yes', 'no']),
                key_filename=dict(type='str', required=False)
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required parameters for module
        self.command = self.module.params['command']

        # local SSH keys will be used in case of password less SSH connection
        self.usesshkey = self.module.params['usesshkey']
        self.key_filename = self.module.params['key_filename']

        # Required
        self.clustername = self.module.params['clustername']
        self.username = self.module.params['username']
        self.password = self.module.params['password']
        self.log_path = log_path

        if self.password is None:
            if self.usesshkey == 'yes':
                self.log("password is none and use ssh private key. Check for its path")
                if self.key_filename:
                    self.look_for_keys = True
                else:
                    self.log("key file_name is not provided, use default one, ~/.ssh/id_rsa.pub")
                    self.look_for_keys = True
            else:
                self.module.fail_json(msg="You must pass in either password or key for ssh")
        else:
            self.look_for_keys = False

        # Connect to the storage
        self.ssh_client = IBMSVCssh(
            module=self.module,
            clustername=self.module.params['clustername'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            look_for_keys=self.look_for_keys,
            key_filename=self.key_filename,
            log_path=log_path
        )

    def modify_command(self, argument):
        return ' '.join([c.strip() if not c.startswith('ls') else c + " -json" for c in argument.strip().split()])

    def send_svcinfo_command(self):
        info_output = ""
        message = ""
        failed = False

        if self.ssh_client.is_client_connected:
            if not self.command.startswith('svcinfo'):
                failed = True
                message = "The command must start with svcinfo"
            if (self.command.find('|') != -1):
                failed = True
                message = "Pipe(|) is not supported in command."
            if (self.command.find('-filtervalue') != -1):
                failed = True
                message = "'filtervalue' is not supported in command."
            if not failed:
                new_command = self.modify_command(self.command)
                self.log("Executing CLI command: %s", new_command)
                stdin, stdout, stderr = self.ssh_client.client.exec_command(new_command)
                for line in stdout.readlines():
                    info_output += line
                self.log(info_output)
                rc = stdout.channel.recv_exit_status()
                if rc > 0:
                    message = stderr.read()
                    if len(message) > 0:
                        message = message.decode('utf-8')
                        self.log("Error in executing CLI command: %s", new_command)
                        self.log("%s", message)
                    else:
                        message = "Unknown error"
                    self.ssh_client._svc_disconnect()
                    self.module.fail_json(msg=message, rc=rc, stdout=info_output)
                self.ssh_client._svc_disconnect()
                self.module.exit_json(msg=message, rc=rc, stdout=info_output)
        else:
            message = "SSH client is not connected"
        self.ssh_client._svc_disconnect()
        self.module.fail_json(msg=message)


def main():
    v = IBMSVCsshClient()
    try:
        if not v.ssh_client.is_client_connected:
            v.log("SSH Connection failed, retry")
            v.module.exit_json(msg="SSH connection failed, retry", changed=False)
        else:
            v.send_svcinfo_command()
    except Exception as e:
        v.ssh_client._svc_disconnect()
        v.log("Exception in executing CLI command(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
