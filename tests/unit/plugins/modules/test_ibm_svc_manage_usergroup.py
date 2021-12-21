# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_usergroup """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_usergroup import IBMSVCUsergroup


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


class TestIBMSVCUsergroup(unittest.TestCase):
    """ a group of related Unit Tests"""

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

    def set_default_args(self):
        return dict({
            'name': 'test',
            'state': 'present'
        })

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVCUsergroup()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Monitor',
            'ownershipgroup': 'ownershipgroupx'
        })
        ug = IBMSVCUsergroup()
        data = ug.basic_checks()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_usergroup(self, mock_svc_authorize, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Monitor',
            'ownershipgroup': 'ownershipgroupx'
        })
        svc_obj_info_mock.return_value = {
            "id": "8",
            "name": "test_usergrp",
            "role": "Monitor",
            "remote": "no",
            "owner_id": "1",
            "owner_name": "ownershipgroupx"
        }
        ug = IBMSVCUsergroup()
        data = ug.get_existing_usergroup()
        self.assertEqual(data["name"], "test_usergrp")

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_user_group(self, mock_svc_authorize, svc_run_command):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Monitor',
            'ownershipgroup': 'ownershipgroupx'
        })
        svc_run_command.return_value = {
            "message": "User Group, id [6], successfully created",
            "id": 6
        }
        ug = IBMSVCUsergroup()
        data = ug.create_user_group()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_probe_user_group(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Monitor',
            'ownershipgroup': 'ownershipgroupx'
        })
        data = {
            "id": "8",
            "name": "test_usergrp",
            "role": "Service",
            "remote": "no",
            "owner_id": "1",
            "owner_name": "ownershipgroupy"
        }
        ug = IBMSVCUsergroup()
        data = ug.probe_user_group(data)
        self.assertTrue('role' in data)
        self.assertTrue('ownershipgroup' in data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_user_group(self, mock_svc_authorize, svc_run_command):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Monitor',
            'ownershipgroup': 'ownershipgroupx'
        })
        data = {
            "role": "Service",
            "ownershipgroup": "ownershipgroupy"
        }
        ug = IBMSVCUsergroup()
        data = ug.update_user_group(data)
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_user_group(self, mock_svc_authorize, svc_run_command):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'absent',
        })
        svc_run_command.return_value = None
        ug = IBMSVCUsergroup()
        data = ug.remove_user_group()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_new_ownershipgroup(self, mock_svc_authorize, soi, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Monitor',
            'ownershipgroup': 'ownershipgroupx'
        })
        soi.return_value = {}
        src.return_value = {
            "message": "User Group, id [6], successfully created",
            "id": 6
        }
        ug = IBMSVCUsergroup()
        with pytest.raises(AnsibleExitJson) as exc:
            ug.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_existing_ownershipgroup(self, mock_svc_authorize, soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Monitor',
            'ownershipgroup': 'ownershipgroupx'
        })
        soi.return_value = {
            "id": "8",
            "name": "test_usergrp",
            "role": "Monitor",
            "remote": "no",
            "owner_id": "1",
            "owner_name": "ownershipgroupx"
        }
        ug = IBMSVCUsergroup()
        with pytest.raises(AnsibleExitJson) as exc:
            ug.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_existing_ownershipgroup(self, mock_svc_authorize, soi, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Service',
            'ownershipgroup': 'ownershipgroupy'
        })
        soi.return_value = {
            "id": "8",
            "name": "test_usergrp",
            "role": "Monitor",
            "remote": "no",
            "owner_id": "1",
            "owner_name": "ownershipgroupx"
        }
        src.return_value = None
        ug = IBMSVCUsergroup()
        with pytest.raises(AnsibleExitJson) as exc:
            ug.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_noownershipgroup(self, mock_svc_authorize, soi, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'role': 'Service',
            'noownershipgroup': True
        })
        soi.return_value = {
            "id": "8",
            "name": "test_usergrp",
            "role": "Monitor",
            "remote": "no",
            "owner_id": "1",
            "owner_name": "ownershipgroupx"
        }
        src.return_value = None
        ug = IBMSVCUsergroup()
        with pytest.raises(AnsibleExitJson) as exc:
            ug.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_existing_ownershipgroup(self, mock_svc_authorize, soi, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'absent',
        })
        soi.return_value = {
            "id": "8",
            "name": "test_usergrp",
            "role": "Monitor",
            "remote": "no",
            "owner_id": "1",
            "owner_name": "ownershipgroupx"
        }
        src.return_value = None
        ug = IBMSVCUsergroup()
        with pytest.raises(AnsibleExitJson) as exc:
            ug.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_non_existing_ownershipgroup(self, mock_svc_authorize, soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'absent',
        })
        soi.return_value = {}
        ug = IBMSVCUsergroup()
        with pytest.raises(AnsibleExitJson) as exc:
            ug.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_missing_name_parameter(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUsergroup()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_missing_state_parameter(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_usergrp'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUsergroup()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_missing_role_parameter_during_creation(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_usergrp',
            'state': 'present'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUsergroup()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_mutually_exclusive_noownershipgroup(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_usergrp',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup-name',
            'noownershipgroup': True
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUsergroup()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])


if __name__ == '__main__':
    unittest.main()
