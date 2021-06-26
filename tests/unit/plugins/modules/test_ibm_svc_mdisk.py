# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_mdisk """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_mdisk import IBMSVCmdisk


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


class TestIBMSVCmdisk(unittest.TestCase):
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
            IBMSVCmdisk()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_mdisk(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_get_existing_mdisk',
            'mdiskgrp': 'Ansible-Pool'
        })
        mdisk_ret = [{"id": "0", "name": "mdisk_Ansible_collections",
                      "status": "online", "mode": "array", "mdisk_grp_id": "0",
                      "mdisk_grp_name": "Pool_Ansible_collections",
                      "capacity": "5.2TB", "ctrl_LUN_#": "",
                      "controller_name": "", "UID": "", "tier": "tier0_flash",
                      "encrypt": "no", "site_id": "", "site_name": "",
                      "distributed": "no", "dedupe": "no",
                      "over_provisioned": "no", "supports_unmap": "yes"}]
        svc_obj_info_mock.return_value = mdisk_ret
        mdisk = IBMSVCmdisk().mdisk_exists()
        self.assertEqual('mdisk_Ansible_collections', mdisk[0]['name'])
        self.assertEqual('0', mdisk[0]['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_mdisk_create_get_existing_mdisk_called(self, svc_authorize_mock,
                                                    get_existing_mdisk_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_mdisk_create_get_existing_mdisk_called',
            'mdiskgrp': 'Pool'
        })
        mdisk_created = IBMSVCmdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            mdisk_created.apply()
        get_existing_mdisk_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_mdisk_failed_since_missed_required_param(
            self, svc_authorize_mock, get_existing_mdisk_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_mdisk_failed_since_missed_required_param',
            'mdiskgrp': 'Pool'
        })
        get_existing_mdisk_mock.return_value = []
        mdisk_created = IBMSVCmdisk()
        with pytest.raises(AnsibleFailJson) as exc:
            mdisk_created.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        get_existing_mdisk_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_mdisk_but_mdisk_existed(self, svc_authorize_mock,
                                            mdisk_probe_mock,
                                            get_existing_mdisk_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_mdisk_but_mdisk_existed',
            'mdiskgrp': 'Pool'
        })
        mdisk_ret = [{"id": "0", "name": "mdisk_Ansible_collections",
                      "status": "online", "mode": "array", "mdisk_grp_id": "0",
                      "mdisk_grp_name": "Pool_Ansible_collections",
                      "capacity": "5.2TB", "ctrl_LUN_#": "",
                      "controller_name": "", "UID": "", "tier": "tier0_flash",
                      "encrypt": "no", "site_id": "", "site_name": "",
                      "distributed": "no", "dedupe": "no",
                      "over_provisioned": "no", "supports_unmap": "yes"}]
        get_existing_mdisk_mock.return_value = mdisk_ret
        mdisk_probe_mock.return_value = []
        mdisk_created = IBMSVCmdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            mdisk_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_mdisk_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_mdisk_successfully(self, svc_authorize_mock,
                                       mdisk_create_mock,
                                       get_existing_mdisk_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_mdisk_successfully',
            'level': 'raid0',
            'drive': '5:6',
            'encrypt': 'no',
            'mdiskgrp': 'Pool'
        })
        mdisk = {u'message': u'Mdisk, id [0],'
                             u'successfully created', u'id': u'0'}
        mdisk_create_mock.return_value = mdisk
        get_existing_mdisk_mock.return_value = []
        mdisk_created = IBMSVCmdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            mdisk_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_mdisk_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_mdisk_failed_since_no_message_in_result(
            self, svc_authorize_mock, svc_run_command_mock,
            get_existing_mdisk_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_mdisk_successfully',
            'level': 'raid0',
            'drive': '5:6',
            'encrypt': 'no',
            'mdiskgrp': 'Pool'
        })
        mdisk = {u'id': u'0'}
        svc_run_command_mock.return_value = mdisk
        get_existing_mdisk_mock.return_value = []
        mdisk_created = IBMSVCmdisk()
        with pytest.raises(AnsibleFailJson) as exc:
            mdisk_created.apply()
        get_existing_mdisk_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_mdisk_but_mdisk_not_existed(self, svc_authorize_mock,
                                                get_existing_mdisk_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_delete_mdisk_but_mdisk_not_existed',
            'mdiskgrp': 'Pool'
        })
        get_existing_mdisk_mock.return_value = []
        mdisk_deleted = IBMSVCmdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            mdisk_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_mdisk_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdisk.IBMSVCmdisk.mdisk_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_mdisk_successfully(self, svc_authorize_mock,
                                       mdisk_delete_mock,
                                       get_existing_mdisk_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_delete_mdisk_successfully',
            'mdiskgrp': 'Pool'
        })
        mdisk_ret = [{"id": "0", "name": "mdisk_Ansible_collections",
                      "status": "online", "mode": "array", "mdisk_grp_id": "0",
                      "mdisk_grp_name": "Pool_Ansible_collections",
                      "capacity": "5.2TB", "ctrl_LUN_#": "",
                      "controller_name": "", "UID": "", "tier": "tier0_flash",
                      "encrypt": "no", "site_id": "", "site_name": "",
                      "distributed": "no", "dedupe": "no",
                      "over_provisioned": "no", "supports_unmap": "yes"}]
        get_existing_mdisk_mock.return_value = mdisk_ret
        mdisk_deleted = IBMSVCmdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            mdisk_deleted.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_mdisk_mock.assert_called_with()


if __name__ == '__main__':
    unittest.main()
