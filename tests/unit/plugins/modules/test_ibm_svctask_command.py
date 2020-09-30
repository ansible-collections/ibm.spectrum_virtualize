# Copyright (C) 2020 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svctask_command """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils.compat.paramiko import paramiko
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_ssh import IBMSVCssh
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svctask_command import IBMSVCsshClient


def set_module_args(args):
    """prepare arguments so that they will be picked up during module
    creation """
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the
    test case """
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the
    test case """
    pass


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over exit_json; package return data into an
    exception """
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over fail_json; package return data into an
    exception """
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestIBMSVCsshClient_svctask(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def set_default_args(self):
        return dict({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svctask cli_command',
        })

    def test_ssh_connect_with_missing_username(self):
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({
                'clustername': 'clustername',
                'password': 'password',
                'command': 'svctask cli_command',
            })
            IBMSVCsshClient()
            print('Info: %s' % exc.value.args[0]['msg'])
            self.assertFalse(exc.value.args[0]['changed'])

    def test_ssh_connect_with_missing_password(self):
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({
                'clustername': 'clustername',
                'username': 'username',
                'command': 'svctask cli_command',
            })
            IBMSVCsshClient()
            print('Info: %s' % exc.value.args[0]['msg'])
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_connect_with_password(self, connect_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svctask cli_command',
        })
        if paramiko is None:
            print("paramiko is not installed")

        patch.object(paramiko.SSHClient, 'exec_command')
        conn = IBMSVCsshClient()
        with pytest.raises(Exception) as exc:
            conn.send_svctask_command()
        print('Info: %s' % exc.value.args[0])
        self.assertTrue(conn.ssh_client.is_client_connected)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_connect_with_key(self, connect_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': '',
            'usesshkey': 'yes',
            'command': 'svctask cli_command',
        })
        if paramiko is None:
            print("paramiko is not installed")

        patch.object(paramiko.SSHClient, 'exec_command')
        conn = IBMSVCsshClient()
        with pytest.raises(Exception) as exc:
            conn.send_svctask_command()
        print('Info: %s' % exc.value.args[0])
        self.assertTrue(conn.ssh_client.is_client_connected)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_disconnect')
    def test_ssh_disconnect(self, connect_mock, disconnect_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svctask cli_command',
        })
        conn = IBMSVCsshClient()
        conn.is_client_connected = True
        conn.ssh_client._svc_disconnect()
        self.assertTrue(conn.ssh_client.is_client_connected)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_disconnect_failed(self, connect_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svctask cli_command',
        })
        conn = IBMSVCsshClient()
        conn.ssh_client._svc_disconnect()
        self.assertFalse(conn.ssh_client.is_client_connected)


if __name__ == '__main__':
    unittest.main()
