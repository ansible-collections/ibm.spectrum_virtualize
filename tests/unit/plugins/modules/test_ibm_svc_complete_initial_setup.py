# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_complete_intial_setup """

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
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_complete_initial_setup import IBMSVCCompleteSetup


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


class TestIBMSVCInitS(unittest.TestCase):

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
        })

    def test_ssh_connect_with_missing_username(self):
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({
                'clustername': 'clustername',
                'password': 'password',
            })
            IBMSVCCompleteSetup()
            print('Info: %s' % exc.value.args[0]['msg'])
            self.assertFalse(exc.value.args[0]['changed'])

    def test_ssh_connect_with_missing_password(self):
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({
                'clustername': 'clustername',
                'username': 'username',
            })
            IBMSVCCompleteSetup()
            print('Info: %s' % exc.value.args[0]['msg'])
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_complete_initial_setup.IBMSVCCompleteSetup.is_lmc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_disconnect')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_setup_with_lmc(self, connect_mock, disconnect_mock, lmc_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password'
        })
        lmc_mock.return_value = True
        patch.object(paramiko.SSHClient, 'exec_command')
        conn = IBMSVCCompleteSetup()
        with pytest.raises(Exception) as exc:
            conn.apply()
        print('Info: %s' % exc)
        self.assertTrue(exc)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_complete_initial_setup.IBMSVCCompleteSetup.is_lmc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_disconnect')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_setup_without_lmc(self, connect_mock, disconnect_mock, lmc_mock):
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password'
        })
        lmc_mock.return_value = False
        patch.object(paramiko.SSHClient, 'exec_command')
        conn = IBMSVCCompleteSetup()
        with pytest.raises(Exception) as exc:
            conn.apply()
        print('Info: %s' % exc)
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
