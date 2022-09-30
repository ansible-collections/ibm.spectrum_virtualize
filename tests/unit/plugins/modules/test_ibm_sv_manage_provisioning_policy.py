# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_manage_provisioning_policy """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_manage_provisioning_policy import IBMSVProvisioningPolicy


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


class TestIBMSVProvisioningPolicy(unittest.TestCase):
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

    def test_module_with_blank_values(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': ''
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVProvisioningPolicy()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_without_state_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp0',
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVProvisioningPolicy()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_provisioning_policy.IBMSVProvisioningPolicy.is_pp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_without_mandatory_parameter(self,
                                                svc_authorize_mock,
                                                svc_run_command_mock,
                                                pp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp0',
            'state': 'present'
        })

        pp_exists_mock.return_value = {}
        pp = IBMSVProvisioningPolicy()

        with pytest.raises(AnsibleFailJson) as exc:
            pp.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_provisioning_policy.IBMSVProvisioningPolicy.is_pp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_provisioning_policy(self,
                                        svc_authorize_mock,
                                        svc_run_command_mock,
                                        pp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp0',
            'capacitysaving': 'drivebased',
            'state': 'present'
        })

        pp_exists_mock.return_value = {}
        pp = IBMSVProvisioningPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            pp.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_provisioning_policy_idempotency(self,
                                                    svc_authorize_mock,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp0',
            'capacitysaving': 'drivebased',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {'id': 0, 'name': 'pp0', 'capacity_saving': 'none'}
        pp = IBMSVProvisioningPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            pp.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_provisioning_policy.IBMSVProvisioningPolicy.is_pp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_provisioning_policy(self,
                                        svc_authorize_mock,
                                        svc_run_command_mock,
                                        pp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp_new',
            'old_name': 'pp0',
            'state': 'present'
        })

        pp_exists_mock.side_effect = iter([
            {'id': 0, 'name': 'pp0'},
            {},
            {'id': 0, 'name': 'pp0'}
        ])
        pp = IBMSVProvisioningPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            pp.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_provisioning_policy.IBMSVProvisioningPolicy.is_pp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_provisioning_policy_idempotency(self,
                                                    svc_authorize_mock,
                                                    svc_run_command_mock,
                                                    pp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp_new',
            'old_name': 'pp0',
            'state': 'present'
        })

        pp_exists_mock.side_effect = iter([{}, {'id': 0, 'name': 'pp0'}, {}])
        pp = IBMSVProvisioningPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            pp.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_with_capacitysaving(self,
                                        svc_authorize_mock,
                                        svc_run_command_mock,
                                        svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp_new',
            'old_name': 'pp0',
            'capacitysaving': 'drivebased',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {'id': 0, 'name': 'pp0', 'capacity_saving': 'none'}
        pp = IBMSVProvisioningPolicy()
        with pytest.raises(AnsibleFailJson) as exc:
            pp.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_with_deduplicated(self,
                                      svc_authorize_mock,
                                      svc_run_command_mock,
                                      svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp_new',
            'old_name': 'pp0',
            'deduplicated': True,
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {'id': 0, 'name': 'pp0', 'deduplicated': 'no'}
        pp = IBMSVProvisioningPolicy()
        with pytest.raises(AnsibleFailJson) as exc:
            pp.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_provisioning_policy.IBMSVProvisioningPolicy.is_pp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_provisioning_policy(self,
                                        svc_authorize_mock,
                                        svc_run_command_mock,
                                        pp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp0',
            'state': 'absent'
        })

        pp_exists_mock.return_value = {'id': 0, 'name': 'pp0'}
        pp = IBMSVProvisioningPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            pp.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_provisioning_policy.IBMSVProvisioningPolicy.is_pp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_provisioning_policy_idempotency(self,
                                                    svc_authorize_mock,
                                                    svc_run_command_mock,
                                                    pp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp0',
            'state': 'absent'
        })

        pp_exists_mock.return_value = {}
        pp = IBMSVProvisioningPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            pp.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_provisioning_policy.IBMSVProvisioningPolicy.is_pp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_provisioning_policy_validation(self,
                                                   svc_authorize_mock,
                                                   svc_run_command_mock,
                                                   pp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'pp0',
            'capacitysaving': 'drivebased',
            'state': 'absent'
        })

        pp_exists_mock.return_value = {}

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVProvisioningPolicy()
        self.assertTrue(exc.value.args[0]['failed'])


if __name__ == '__main__':
    unittest.main()
