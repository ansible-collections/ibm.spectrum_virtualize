# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_sra """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_sra import IBMSVCSupportRemoteAssistance


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


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an
    exception """
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestIBMSVCSupportRemoteAssistance(unittest.TestCase):
    """
    Group of related Unit Tests
    """

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def setUp(self, connect):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)
        self.restapi = IBMSVCRestApi(self.mock_module_helper, '1.2.3.4',
                                     'domain.ibm.com', 'username', 'password',
                                     False, 'test.log', '')

    def test_module_required_if_functionality(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_required_together_functionality(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': []
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_with_empty_list(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': [],
            'sra_ip': [],
            'sra_port': []
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_with_blank_value_in_list(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': [''],
            'sra_ip': [''],
            'sra_port': ['']
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_without_state_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'support': 'onsite'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_onsite_with_unnecessary_args(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'support': 'onsite',
            'name': ['test_proxy']
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_with_unequal_proxy_arguments(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': ['dummy_proxy'],
            'sra_ip': ['9.9.9.9', '9.9.9.9'],
            'sra_port': []
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_enable_sra_onsite(self, svc_authorize_mock,
                               svc_run_command_mock,
                               sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'onsite',
        })

        sra_enabled_mock.return_value = False

        sra_inst = IBMSVCSupportRemoteAssistance()
        with pytest.raises(AnsibleExitJson) as exc:
            sra_inst.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.add_proxy_details')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_enable_sra_remote_with_proxy(self, svc_authorize_mock,
                                          svc_run_command_mock,
                                          add_proxy_mock,
                                          sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': ['customer_proxy'],
            'sra_ip': ['10.10.10.10'],
            'sra_port': [8888]
        })

        sra_enabled_mock.return_value = False

        sra_inst = IBMSVCSupportRemoteAssistance()
        with pytest.raises(AnsibleExitJson) as exc:
            sra_inst.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.remove_proxy_details')
    def test_disable_sra_remote_negative(self, remove_proxy_mock,
                                         svc_authorize_mock,
                                         svc_run_command_mock,
                                         sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'disabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': ['customer_proxy'],
            'sra_ip': ['10.10.10.10'],
            'sra_port': [8888]
        })

        sra_enabled_mock.return_value = True
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSupportRemoteAssistance()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.remove_proxy_details')
    def test_disable_sra_remote(self, remove_proxy_mock,
                                svc_authorize_mock,
                                svc_run_command_mock,
                                sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'disabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': ['customer_proxy']
        })

        sra_enabled_mock.return_value = True

        sra_inst = IBMSVCSupportRemoteAssistance()
        with pytest.raises(AnsibleExitJson) as exc:
            sra_inst.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_enable_sra_twice(self, svc_authorize_mock,
                              svc_run_command_mock,
                              svc_obj_info_mock,
                              sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'onsite',
        })

        svc_obj_info_mock.return_value = {'remote_support_enabled': 'yes'}
        sra_enabled_mock.return_value = True

        sra_inst = IBMSVCSupportRemoteAssistance()
        with pytest.raises(AnsibleExitJson) as exc:
            sra_inst.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_remote_support_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.add_proxy_details')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_sra(self, svc_authorize_mock,
                        add_proxy_mock,
                        remote_enabled_mock,
                        sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'enabled',
            'username': 'username',
            'password': 'password',
            'support': 'remote',
            'name': ['customer_proxy'],
            'sra_ip': ['10.10.10.10'],
            'sra_port': [8888]
        })

        sra_enabled_mock.return_value = True
        remote_enabled_mock.return_value = False
        add_proxy_mock.return_value = []

        sra_inst = IBMSVCSupportRemoteAssistance()
        with pytest.raises(AnsibleExitJson) as exc:
            sra_inst.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_disable_sra(self, svc_authorize_mock,
                         svc_run_command_mock,
                         sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'disabled',
            'username': 'username',
            'password': 'password',
            'support': 'onsite',
        })

        sra_enabled_mock.return_value = True

        sra_inst = IBMSVCSupportRemoteAssistance()
        with pytest.raises(AnsibleExitJson) as exc:
            sra_inst.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_sra.IBMSVCSupportRemoteAssistance.is_sra_enabled')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_disable_sra_twice(self, svc_authorize_mock,
                               svc_run_command_mock,
                               sra_enabled_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'disabled',
            'username': 'username',
            'password': 'password',
            'support': 'onsite',
        })

        sra_enabled_mock.return_value = False

        sra_inst = IBMSVCSupportRemoteAssistance()
        with pytest.raises(AnsibleExitJson) as exc:
            sra_inst.apply()
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
