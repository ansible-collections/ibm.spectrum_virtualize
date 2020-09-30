# Copyright (C) 2020 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module_utils: ibm_svc_ssh """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import json
import paramiko
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_ssh import IBMSVCssh


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


class TestIBMSVModuleUtilsSsh(unittest.TestCase):
    """ a group of related Unit Tests"""

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def setUp(self, mock_connect):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)
        self.sshclient = IBMSVCssh(self.mock_module_helper, '1.2.3.4',
                                   'username', 'password',
                                   False, '', 'test.log')

    def set_default_args(self):
        return dict({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'look_for_keys': False,
        })

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_svc_ssh_connect(self, mock_connect):
        if paramiko is None:
            print("paramiko is not installed")

        ret = self.sshclient.is_connected()
        self.assertTrue(ret)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_svc_ssh_disconnect_successfully(self, mock_disconnect):
        if paramiko is None:
            print("paramiko is not installed")

        patch.object(paramiko.SSHClient, 'close')
        ret = self.sshclient._svc_disconnect()
        self.assertTrue(ret)


if __name__ == '__main__':
    unittest.main()
