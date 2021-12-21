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
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_user import IBMSVCUser


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


class TestIBMSVCUser(unittest.TestCase):
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
            IBMSVCUser()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_user(self, mock_svc_authorize, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'auth_type': 'usergrp',
            'usergroup': 'Service',
        })
        svc_obj_info_mock.return_value = {
            "id": "3",
            "name": "userx",
            "password": "yes",
            "ssh_key": "no",
            "remote": "no",
            "usergrp_id": "3",
            "usergrp_name": "Service",
            "owner_id": "",
            "owner_name": "",
            "locked": "no",
            "locked_until": "",
            "password_expiry_time": "",
            "password_change_required": "no"
        }
        ug = IBMSVCUser()
        data = ug.get_existing_user()
        self.assertEqual(data["name"], "userx")

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'auth_type': 'usergrp',
            'usergroup': 'Service',
        })
        ug = IBMSVCUser()
        data = ug.basic_checks()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_user(self, mock_svc_authorize, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'auth_type': 'usergrp',
            'usergroup': 'Service',
        })
        svc_obj_info_mock.return_value = {
            "id": "3",
            "name": "userx",
            "password": "yes",
            "ssh_key": "no",
            "remote": "no",
            "usergrp_id": "3",
            "usergrp_name": "Service",
            "owner_id": "",
            "owner_name": "",
            "locked": "no",
            "locked_until": "",
            "password_expiry_time": "",
            "password_change_required": "no"
        }
        ug = IBMSVCUser()
        data = ug.get_existing_user()
        self.assertEqual(data["name"], "userx")

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_user(self, mock_svc_authorize, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'auth_type': 'usergrp',
            'usergroup': 'Service',
        })
        svc_run_command_mock.return_value = {
            'id': '3',
            'message': 'User, id [3], successfully created'
        }
        ug = IBMSVCUser()
        data = ug.create_user()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_probe_user(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'auth_type': 'usergrp',
            'usergroup': 'Monitor',
        })
        data = {
            "id": "3",
            "name": "userx",
            "password": "yes",
            "ssh_key": "no",
            "remote": "no",
            "usergrp_id": "3",
            "usergrp_name": "Service",
            "owner_id": "",
            "owner_name": "",
            "locked": "no",
            "locked_until": "",
            "password_expiry_time": "",
            "password_change_required": "no"
        }
        ug = IBMSVCUser()
        result = ug.probe_user(data)
        self.assertEqual(result['usergrp'], 'Monitor')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_user(self, mock_svc_authorize, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'auth_type': 'usergrp',
            'usergroup': 'Monitor',
        })
        data = {
            'usergrp': 'Monitor',
            'password': 'Test@123'
        }
        svc_run_command_mock.return_value = None
        ug = IBMSVCUser()
        result = ug.update_user(data)
        self.assertEqual(result, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_user(self, mock_svc_authorize, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'name': 'userx',
        })
        svc_run_command_mock.return_value = None
        ug = IBMSVCUser()
        result = ug.remove_user()
        self.assertEqual(result, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_creating_new_user(self, mock_svc_authorize, mock_soi, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'name': 'userx',
            'user_password': 'userx@123',
            'usergroup': 'Monitor'
        })
        mock_soi.return_value = {}
        mock_src.return_value = {
            'id': '3',
            'message': 'User, id [3], successfully created'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_creating_existing_user(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'usergroup': 'Service'
        })
        mock_soi.return_value = {
            "id": "3",
            "name": "userx",
            "password": "yes",
            "ssh_key": "no",
            "remote": "no",
            "usergrp_id": "3",
            "usergrp_name": "Service",
            "owner_id": "",
            "owner_name": "",
            "locked": "no",
            "locked_until": "",
            "password_expiry_time": "",
            "password_change_required": "no"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_updating_user(self, mock_svc_authorize, mock_soi, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'usergroup': 'Monitor',
            'lock': True,
            'forcepasswordchange': True
        })
        mock_soi.return_value = {
            "id": "3",
            "name": "userx",
            "password": "yes",
            "ssh_key": "no",
            "remote": "no",
            "usergrp_id": "3",
            "usergrp_name": "Service",
            "owner_id": "",
            "owner_name": "",
            "locked": "no",
            "locked_until": "",
            "password_expiry_time": "",
            "password_change_required": "no"
        }
        mock_src.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_removing_existing_user(self, mock_svc_authorize, mock_soi, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'name': 'userx',
        })
        mock_soi.return_value = {
            "id": "3",
            "name": "userx",
            "password": "yes",
            "ssh_key": "no",
            "remote": "no",
            "usergrp_id": "3",
            "usergrp_name": "Service",
            "owner_id": "",
            "owner_name": "",
            "locked": "no",
            "locked_until": "",
            "password_expiry_time": "",
            "password_change_required": "no"
        }
        mock_src.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_removing_non_existing_user(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'name': 'userx',
        })
        mock_soi.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_missing_mandatory_parameters(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_missing_parameter_during_creation(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'userx',
            'state': 'present',
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_mutually_exclusive_nopassword(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'nopassword': True,
            'auth_type': 'usergrp',
            'usergroup': 'Service',
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_mutually_exclusive_nokey(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'keyfile': 'keyfile-path',
            'nokey': True,
            'auth_type': 'usergrp',
            'usergroup': 'Service',
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_mutually_exclusive_nokey(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'userx',
            'user_password': 'Test@123',
            'keyfile': 'keyfile-path',
            'auth_type': 'usergrp',
            'usergroup': 'Service',
            'lock': True,
            'unlock': True
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ug = IBMSVCUser()
            ug.apply()
            self.assertTrue(exc.value.args[0]['failed'])


if __name__ == '__main__':
    unittest.main()
