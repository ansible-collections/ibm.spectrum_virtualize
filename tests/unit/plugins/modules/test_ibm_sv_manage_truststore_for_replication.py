# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_manage_truststore_for_replication """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch, Mock
from ansible.module_utils.compat.paramiko import paramiko
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_ssh import IBMSVCssh
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_manage_truststore_for_replication import (
    IBMSVTrustStore
)


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


class TestIBMSVTrustStore(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_mandatory_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVTrustStore()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_create_truststore_with_name(self, svc_connect_mock, ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'ansi_store',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()

        self.assertTrue(exc.value.args[0]['changed'])
        self.assertTrue('ansi_store' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_create_truststore_with_name_idempotency(self,
                                                            svc_connect_mock,
                                                            ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'ansi_store',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{"name":"ansi_store"}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()

        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_create_truststore_without_name(self, svc_connect_mock,
                                                   ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()

        self.assertTrue(exc.value.args[0]['changed'])
        self.assertTrue('store_x.x.x.x' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_create_truststore_without_name_idempotency(self, svc_connect_mock,
                                                               ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{"name": "store_x.x.x.x"}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()

        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_delete_truststore_with_name(self, svc_connect_mock,
                                                ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'ansi_store',
            'remote_clustername': 'x.x.x.x',
            'state': 'absent'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{"name": "ansi_store"}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_delete_truststore_with_name_idempotency(self, svc_connect_mock,
                                                            ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'x.x.x.x',
            'state': 'absent'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_delete_truststore_without_name(self, svc_connect_mock,
                                                   ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'x.x.x.x',
            'state': 'absent'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{"name": "store_x.x.x.x"}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()

        self.assertTrue(exc.value.args[0]['changed'])
        self.assertTrue('store_x.x.x.x' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_module_delete_truststore_without_name_idempotency(self, svc_connect_mock,
                                                               ssh_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'x.x.x.x',
            'state': 'absent'
        })
        con_mock = Mock()
        svc_connect_mock.return_value = True
        ssh_mock.return_value = con_mock
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        con_mock.exec_command.return_value = (stdin, stdout, stderr)
        stdout.read.side_effect = iter([br'{}', b'', b''])
        stdout.channel.recv_exit_status.return_value = 0

        ts = IBMSVTrustStore()

        with pytest.raises(AnsibleExitJson) as exc:
            ts.apply()

        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
