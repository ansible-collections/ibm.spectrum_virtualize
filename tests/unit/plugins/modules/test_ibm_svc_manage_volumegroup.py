# Copyright (C) 2020 IBM CORPORATION
# Author(s):
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_vdisk """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_volumegroup import IBMSVCVG


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


class TestIBMSVCvdisk(unittest.TestCase):
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
            IBMSVCVG()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_vg(self, mock_svc_authorize, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        vg.get_existing_vg()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_adding_ownershipgroup(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup_new',
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('ownershipgroup' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_updating_ownershipgroup(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup_new',
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "test_ownershipgroup_old",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('ownershipgroup' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_with_noownershipgroup(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'noownershipgroup': True
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "test_ownershipgroup",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('noownershipgroup' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_add_safeguardpolicyname(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name'
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "test_ownershipgroup",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('safeguardedpolicy' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_update_safeguardpolicyname(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'new_policy_name'
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "test_ownershipgroup",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "old_policy_name",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('safeguardedpolicy' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_mutual_exclusive_parameter_1(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup',
            'noownershipgroup': True
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        with pytest.raises(AnsibleFailJson) as exc:
            vg.vg_probe(data)
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_mutual_exclusive_parameter_2(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name',
            'nosafeguardpolicy': True
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        with pytest.raises(AnsibleFailJson) as exc:
            vg.vg_probe(data)
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_mutual_exclusive_parameter_3(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup',
            'safeguardpolicyname': 'policy_name'
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        vg = IBMSVCVG()
        with pytest.raises(AnsibleFailJson) as exc:
            vg.vg_probe(data)
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_create(self, mock_svc_authorize, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup',
        })
        svc_run_command_mock.return_value = {
            'id': '56',
            'message': 'success'
        }
        vg = IBMSVCVG()
        probe_data = vg.vg_create()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_noownershipgroup_nosafeguardpolicy(self,
                                                               mock_svc_authorize,
                                                               svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'noownershipgroup': True,
            'nosafeguardpolicy': True
        })
        probe_data = {
            'noownershipgroup': True,
            'nosafeguardpolicy': True
        }
        svc_run_command_mock.return_value = None
        vg = IBMSVCVG()
        probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_ownershipgroup_nosafeguardpolicy(self,
                                                             mock_svc_authorize,
                                                             svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'group_name',
            'nosafeguardpolicy': True
        })
        probe_data = {
            'ownershipgroup': 'group_name',
            'nosafeguardpolicy': True
        }
        svc_run_command_mock.return_value = None
        vg = IBMSVCVG()
        probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_safeguardpolicyname(self, mock_svc_authorize,
                                                svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name'
        })
        probe_data = {
            'safeguardedpolicy': 'policy_name'
        }
        svc_run_command_mock.return_value = None
        vg = IBMSVCVG()
        probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_policystarttime(self, mock_svc_authorize,
                                            svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name',
            'policystarttime': 'YYMMDDHHMM'
        })
        probe_data = {
            'safeguardedpolicy': 'policy_name',
            'policystarttime': 'YYMMDDHHMM'
        }
        svc_run_command_mock.return_value = None
        vg = IBMSVCVG()
        probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_only_noownershipgroup(self, mock_svc_authorize,
                                                  svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'noownershipgroup': True,
        })
        probe_data = {
            'noownershipgroup': True
        }
        svc_run_command_mock.return_value = None
        vg = IBMSVCVG()
        probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_only_nosafeguardpolicy(self, mock_svc_authorize,
                                                   svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'nosafeguardpolicy': True,
        })
        probe_data = {
            'nosafeguardpolicy': True,
        }
        svc_run_command_mock.return_value = None
        vg = IBMSVCVG()
        probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_delete(self, mock_svc_authorize, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'absent',
        })
        svc_run_command_mock.return_value = None
        vg = IBMSVCVG()
        vg.vg_delete()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_creation_of_new_volumegroup(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        svc_obj_info_mock.return_value = []
        svc_run_command_mock.return_value = {
            'id': 56,
            'message': 'success message'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_creation_when_volumegroup_aleady_existing(
            self,
            mock_svc_authorize,
            svc_obj_info_mock,
            svc_run_command_mock
    ):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_while_updating_ownersipgroup(self, mock_svc_authorize,
                                                 soim, srcm):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'present',
            'ownershipgroup': 'new_name'
        })
        soim.return_value = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "old_name",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        srcm.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_deleting_an_existing_volumegroup(self, mock_svc_authorize,
                                                         svc_obj_info_mock,
                                                         svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'absent',
        })
        svc_obj_info_mock.return_value = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_deleting_nonexisting_volumegroup(self, mock_svc_authorize,
                                                         svc_obj_info_mock,
                                                         svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'absent',
        })
        svc_obj_info_mock.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_snapshotpolicy(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy1',
            'replicationpolicy': 'rp0',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_snapshotpolicy_idempotency(self, mock_svc_authorize,
                                                                svc_obj_info_mock,
                                                                svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy1',
            'replicationpolicy': 'rp0',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "ss_policy1",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no",
            "replication_policy_name": "rp0"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_safeguarded_snapshotpolicy(self,
                                                                mock_svc_authorize,
                                                                svc_obj_info_mock,
                                                                svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy1',
            'safeguarded': True,
            'ignoreuserfcmaps': 'yes',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_snapshot_policy(self, mock_svc_authorize,
                                    svc_obj_info_mock,
                                    svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy2',
            'replicationpolicy': 'rp0',
            'state': 'present',
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "ss_policy1",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no",
            "replication_policy_name": ""
        }

        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('snapshotpolicy' in probe_data)
        self.assertTrue('replicationpolicy' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_safeguarded_snapshot_policy(self, mock_svc_authorize,
                                                svc_obj_info_mock,
                                                svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy2',
            'safeguarded': True,
            'ignoreuserfcmaps': 'yes',
            'state': 'present',
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "ss_policy1",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }

        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('safeguarded' in probe_data)
        self.assertTrue('snapshotpolicy' in probe_data)
        self.assertTrue('ignoreuserfcmaps' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_unmap_snapshot_policy(self, mock_svc_authorize,
                                          svc_obj_info_mock,
                                          svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'nosnapshotpolicy': True,
            'noreplicationpolicy': True,
            'state': 'present',
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "ss_policy2",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no",
            "replication_policy_name": "rp0"
        }

        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('nosnapshotpolicy' in probe_data)
        self.assertTrue('noreplicationpolicy' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_suspend_snapshot_policy_in_volumegroup(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicysuspended': 'yes',
            'state': 'present',
        })
        data = {
            "id": "8",
            "name": "test_volumegroup",
            "volume_count": "0",
            "backup_status": "empty",
            "last_backup_time": "",
            "owner_id": "",
            "owner_name": "",
            "safeguarded_policy_id": "",
            "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "",
            "snapshot_policy_name": "ss_policy2",
            "snapshot_policy_suspended": "no",
            "ignore_user_flash_copy_maps": "no",
            "snapshot_policy_safeguarded": "no"
        }

        vg = IBMSVCVG()
        probe_data = vg.vg_probe(data)
        self.assertTrue('snapshotpolicysuspended' in probe_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_from_VG_snapshot(self, mock_svc_authorize,
                                                 svc_obj_info_mock,
                                                 svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'type': 'thinclone',
            'snapshot': 'snapshot1',
            'fromsourcegroup': 'volgrp1',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            vg = IBMSVCVG()
            vg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.set_parentuid')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_from_orphan_snapshot(self, mock_svc_authorize,
                                                     svc_obj_info_mock,
                                                     set_parentuid_mock,
                                                     svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'type': 'thinclone',
            'snapshot': 'snapshot1',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {}
        vg = IBMSVCVG()
        vg.parentuid = 5
        with pytest.raises(AnsibleExitJson) as exc:
            vg.apply()
        self.assertTrue(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
