# Copyright (C) 2020 IBM CORPORATION
# Author(s):
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_replication """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_cv import IBMSVCchangevolume


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation """
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


class TestIBMSVCchangevolume(unittest.TestCase):
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
            IBMSVCchangevolume()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_rc(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        svc_obj_info_mock.return_value = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        obj = IBMSVCchangevolume()
        return_data = obj.get_existing_rc()
        self.assertEqual('test_cvname', return_data['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_vdisk(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        svc_obj_info_mock.return_value = [
            {
                "id": "101", "name": "test_cvname", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
                "capacity": "536870912", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "many", "FC_name": "many", "RC_id": "101",
                "RC_name": "rcopy20", "vdisk_UID": "60050768108101C7C0000000000005D9", "preferred_node_id": "1",
                "fast_write_state": "empty", "cache": "readwrite", "udid": "", "fc_map_count": "2",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "201123133855", "parent_mdisk_grp_id": "1",
                "parent_mdisk_grp_name": "AnsibleMaster", "owner_type": "none", "owner_id": "", "owner_name": "",
                "encrypt": "no", "volume_id": "101", "volume_name": "test_cvname", "function": "master", "throttle_id": "",
                "throttle_name": "", "IOPs_limit": "", "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "", "backup_status": "off",
                "last_backup_time": "", "restore_status": "none", "backup_grain_size": "", "deduplicated_copy_count": "0",
                "protocol": "scsi"
            }, {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes", "mdisk_grp_id": "1",
                "mdisk_grp_name": "AnsibleMaster", "type": "striped", "mdisk_id": "", "mdisk_name": "",
                "fast_write_state": "empty", "used_capacity": "536870912", "real_capacity": "536870912", "free_capacity": "0",
                "overallocation": "100", "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "536870912"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ],
                "compressed_copy": "no", "uncompressed_used_capacity": "536870912", "parent_mdisk_grp_id": "1",
                "parent_mdisk_grp_name": "AnsibleMaster", "encrypt": "no", "deduplicated_copy": "no", "used_capacity_before_reduction": ""
            }
        ]
        obj = IBMSVCchangevolume()
        return_data = obj.get_existing_vdisk('test_cvname')
        self.assertEqual('test_cvname', return_data['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_attach_ismaster_true(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        arg_data = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "global", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        svc_run_command_mock.return_value = None
        obj = IBMSVCchangevolume()
        return_data = obj.change_volume_attach(arg_data)
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_attach_ismaster_false(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'false'
        })
        arg_data = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "global", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        svc_run_command_mock.return_value = None
        obj = IBMSVCchangevolume()
        return_data = obj.change_volume_attach(arg_data)
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_detach_ismaster_true(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        arg_data = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "mcvn", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        svc_run_command_mock.return_value = None
        obj = IBMSVCchangevolume()
        return_data = obj.change_volume_detach(arg_data)
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_detach_ismaster_false(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'false'
        })
        arg_data = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "acvn", "previous_primary": "", "channel": "none"
        }
        svc_run_command_mock.return_value = None
        obj = IBMSVCchangevolume()
        return_data = obj.change_volume_detach(arg_data)
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_probe_with_no_rcreldata(self, svc_authorize_mock, get_existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        get_existing_rc_mock.return_value = None
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCchangevolume()
            obj.change_volume_probe()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_probe_with_rcreldata(self, svc_authorize_mock, get_existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        get_existing_rc_mock.return_value = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        obj = IBMSVCchangevolume()
        return_data = obj.change_volume_probe()
        self.assertTrue(return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_delete(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCchangevolume()
        return_data = obj.change_volume_delete()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_create_no_basevolume(self, svc_authorize_mock, get_existing_vdisk_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        get_existing_vdisk_mock.return_value = []
        svc_run_command_mock.return_value = None
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCchangevolume()
            obj.change_volume_create()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_create_with_vdiskdata(self, svc_authorize_mock, get_existing_vdisk_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        get_existing_vdisk_mock.return_value = {
            'id': '101', 'name': 'test_rname', 'IO_group_id': '0', 'IO_group_name': 'io_grp0', 'status': 'online',
            'mdisk_grp_id': '1', 'mdisk_grp_name': 'AnsibleMaster', 'capacity': '536870912', 'type': 'striped',
            'formatted': 'yes', 'formatting': 'no', 'mdisk_id': '', 'mdisk_name': '', 'FC_id': 'many',
            'FC_name': 'many', 'RC_id': '101', 'RC_name': 'rcopy20', 'vdisk_UID': '60050768108101C7C0000000000005D9',
            'preferred_node_id': '1', 'fast_write_state': 'empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2',
            'sync_rate': '50', 'copy_count': '1', 'se_copy_count': '0', 'filesystem': '', 'mirror_write_priority': 'latency',
            'RC_change': 'no', 'compressed_copy_count': '0', 'access_IO_group_count': '1', 'last_access_time': '201123133855',
            'parent_mdisk_grp_id': '1', 'parent_mdisk_grp_name': 'AnsibleMaster', 'owner_type': 'none', 'owner_id': '',
            'owner_name': '', 'encrypt': 'no', 'volume_id': '101', 'volume_name': 'test_cvname', 'function': 'master',
            'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '', 'volume_group_id': '',
            'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '', 'cloud_account_name': '',
            'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none', 'backup_grain_size': '',
            'deduplicated_copy_count': '0', 'protocol': 'scsi', 'copy_id': '0', 'sync': 'yes', 'auto_delete': 'no',
            'primary': 'yes', 'used_capacity': '536870912', 'real_capacity': '536870912', 'free_capacity': '0',
            'overallocation': '100', 'autoexpand': '', 'warning': '', 'grainsize': '', 'se_copy': 'no', 'easy_tier': 'on',
            'easy_tier_status': 'balanced', 'tiers': [
                {'tier': 'tier_scm', 'tier_capacity': '0'},
                {'tier': 'tier0_flash', 'tier_capacity': '536870912'},
                {'tier': 'tier1_flash', 'tier_capacity': '0'},
                {'tier': 'tier_enterprise', 'tier_capacity': '0'},
                {'tier': 'tier_nearline', 'tier_capacity': '0'}
            ],
            'compressed_copy': 'no', 'uncompressed_used_capacity': '536870912',
            'deduplicated_copy': 'no', 'used_capacity_before_reduction': ''
        }
        svc_run_command_mock.return_value = {
            'message': {
                'name': 'test_cvname', 'mdiskgrp': 'SRA-DR-POOL', 'size': '536870912', 'unit': 'b',
                'rsize': '0%', 'autoexpand': True, 'iogrp': 'io_grp0'
            }
        }
        obj = IBMSVCchangevolume()
        return_data = obj.change_volume_create()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_detach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_change_volume(self, sam, gevm, germ, cv_detach_mock, cv_delete_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'absent',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        gevm.return_value = {
            'id': '101', 'name': 'test_cvname', 'IO_group_id': '0', 'IO_group_name': 'io_grp0', 'status': 'online',
            'mdisk_grp_id': '1', 'mdisk_grp_name': 'AnsibleMaster', 'capacity': '536870912', 'type': 'striped',
            'formatted': 'yes', 'formatting': 'no', 'mdisk_id': '', 'mdisk_name': '', 'FC_id': 'many',
            'FC_name': 'many', 'RC_id': '101', 'RC_name': 'rcopy20', 'vdisk_UID': '60050768108101C7C0000000000005D9',
            'preferred_node_id': '1', 'fast_write_state': 'empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2',
            'sync_rate': '50', 'copy_count': '1', 'se_copy_count': '0', 'filesystem': '', 'mirror_write_priority': 'latency',
            'RC_change': 'no', 'compressed_copy_count': '0', 'access_IO_group_count': '1', 'last_access_time': '201123133855',
            'parent_mdisk_grp_id': '1', 'parent_mdisk_grp_name': 'AnsibleMaster', 'owner_type': 'none', 'owner_id': '',
            'owner_name': '', 'encrypt': 'no', 'volume_id': '101', 'volume_name': 'test_cvname', 'function': 'master',
            'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '', 'volume_group_id': '',
            'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '', 'cloud_account_name': '',
            'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none', 'backup_grain_size': '',
            'deduplicated_copy_count': '0', 'protocol': 'scsi', 'copy_id': '0', 'sync': 'yes', 'auto_delete': 'no',
            'primary': 'yes', 'used_capacity': '536870912', 'real_capacity': '536870912', 'free_capacity': '0',
            'overallocation': '100', 'autoexpand': '', 'warning': '', 'grainsize': '', 'se_copy': 'no', 'easy_tier': 'on',
            'easy_tier_status': 'balanced', 'tiers': [
                {'tier': 'tier_scm', 'tier_capacity': '0'},
                {'tier': 'tier0_flash', 'tier_capacity': '536870912'},
                {'tier': 'tier1_flash', 'tier_capacity': '0'},
                {'tier': 'tier_enterprise', 'tier_capacity': '0'},
                {'tier': 'tier_nearline', 'tier_capacity': '0'}
            ],
            'compressed_copy': 'no', 'uncompressed_used_capacity': '536870912', 'deduplicated_copy': 'no',
            'used_capacity_before_reduction': ''
        }
        germ.return_value = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        cv_detach_mock.return_value = None
        cv_delete_mock.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCchangevolume()
            obj.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_detach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_non_existing_change_volume(self, sam, gevm, gerc, cv_detach_mock, cv_delete_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'absent',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        gevm.return_value = {}
        gerc.return_value = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        cv_detach_mock.return_value = None
        cv_delete_mock.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCchangevolume()
            obj.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_attach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_change_volume(self, sam, gevm, germ, cv_create_mock, cv_attach_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        gevm.return_value = {}
        germ.return_value = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        cv_create_mock.return_value = None
        cv_attach_mock.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCchangevolume()
            obj.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_attach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_change_volume_when_rel_absent(self, sam, gevm, germ, cv_create_mock, cv_attach_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        gevm.return_value = {}
        germ.return_value = {}
        cv_create_mock.return_value = None
        cv_attach_mock.return_value = None
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCchangevolume()
            obj.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_attach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_when_change_volume_absent(self, sam, gevm, germ, cv_create_mock, cv_attach_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'absent',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        gevm.return_value = {}
        germ.return_value = {}
        cv_create_mock.return_value = None
        cv_attach_mock.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCchangevolume()
            obj.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_detach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_for_failure_when_copytype_not_global(self, sam, cvpm, gevm, germ, cv_detach_mock, cv_delete_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        gevm.return_value = {
            'id': '101', 'name': 'test_cvname', 'IO_group_id': '0', 'IO_group_name': 'io_grp0', 'status': 'online',
            'mdisk_grp_id': '1', 'mdisk_grp_name': 'AnsibleMaster', 'capacity': '536870912', 'type': 'striped',
            'formatted': 'yes', 'formatting': 'no', 'mdisk_id': '', 'mdisk_name': '', 'FC_id': 'many',
            'FC_name': 'many', 'RC_id': '101', 'RC_name': 'rcopy20', 'vdisk_UID': '60050768108101C7C0000000000005D9',
            'preferred_node_id': '1', 'fast_write_state': 'empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2',
            'sync_rate': '50', 'copy_count': '1', 'se_copy_count': '0', 'filesystem': '', 'mirror_write_priority': 'latency',
            'RC_change': 'no', 'compressed_copy_count': '0', 'access_IO_group_count': '1', 'last_access_time': '201123133855',
            'parent_mdisk_grp_id': '1', 'parent_mdisk_grp_name': 'AnsibleMaster', 'owner_type': 'none', 'owner_id': '',
            'owner_name': '', 'encrypt': 'no', 'volume_id': '101', 'volume_name': 'test_cvname', 'function': 'master',
            'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '', 'volume_group_id': '',
            'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '', 'cloud_account_name': '',
            'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none', 'backup_grain_size': '',
            'deduplicated_copy_count': '0', 'protocol': 'scsi', 'copy_id': '0', 'sync': 'yes', 'auto_delete': 'no',
            'primary': 'yes', 'used_capacity': '536870912', 'real_capacity': '536870912', 'free_capacity': '0',
            'overallocation': '100', 'autoexpand': '', 'warning': '', 'grainsize': '', 'se_copy': 'no', 'easy_tier': 'on',
            'easy_tier_status': 'balanced', 'tiers': [
                {'tier': 'tier_scm', 'tier_capacity': '0'},
                {'tier': 'tier0_flash', 'tier_capacity': '536870912'},
                {'tier': 'tier1_flash', 'tier_capacity': '0'},
                {'tier': 'tier_enterprise', 'tier_capacity': '0'},
                {'tier': 'tier_nearline', 'tier_capacity': '0'}
            ],
            'compressed_copy': 'no', 'uncompressed_used_capacity': '536870912', 'deduplicated_copy': 'no',
            'used_capacity_before_reduction': ''
        }
        germ.return_value = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "metro", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        cv_detach_mock.return_value = None
        cv_delete_mock.return_value = None
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCchangevolume()
            obj.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_attach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_detach')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.change_volume_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_cv.IBMSVCchangevolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_volume_update(self, sam, cvpm, gevm, germ, cv_detach_mock, cv_delete_mock, cva):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cvname': 'test_cvname',
            'basevolume': 'test_base_volume',
            'state': 'present',
            'rname': 'test_rname',
            'ismaster': 'true'
        })
        gevm.return_value = {
            'id': '101', 'name': 'test_cvname', 'IO_group_id': '0', 'IO_group_name': 'io_grp0', 'status': 'online',
            'mdisk_grp_id': '1', 'mdisk_grp_name': 'AnsibleMaster', 'capacity': '536870912', 'type': 'striped',
            'formatted': 'yes', 'formatting': 'no', 'mdisk_id': '', 'mdisk_name': '', 'FC_id': 'many',
            'FC_name': 'many', 'RC_id': '101', 'RC_name': 'rcopy20', 'vdisk_UID': '60050768108101C7C0000000000005D9',
            'preferred_node_id': '1', 'fast_write_state': 'empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2',
            'sync_rate': '50', 'copy_count': '1', 'se_copy_count': '0', 'filesystem': '', 'mirror_write_priority': 'latency',
            'RC_change': 'no', 'compressed_copy_count': '0', 'access_IO_group_count': '1', 'last_access_time': '201123133855',
            'parent_mdisk_grp_id': '1', 'parent_mdisk_grp_name': 'AnsibleMaster', 'owner_type': 'none', 'owner_id': '',
            'owner_name': '', 'encrypt': 'no', 'volume_id': '101', 'volume_name': 'test_cvname', 'function': 'master',
            'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '', 'volume_group_id': '',
            'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '', 'cloud_account_name': '',
            'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none', 'backup_grain_size': '',
            'deduplicated_copy_count': '0', 'protocol': 'scsi', 'copy_id': '0', 'sync': 'yes', 'auto_delete': 'no',
            'primary': 'yes', 'used_capacity': '536870912', 'real_capacity': '536870912', 'free_capacity': '0',
            'overallocation': '100', 'autoexpand': '', 'warning': '', 'grainsize': '', 'se_copy': 'no', 'easy_tier': 'on',
            'easy_tier_status': 'balanced', 'tiers': [
                {'tier': 'tier_scm', 'tier_capacity': '0'},
                {'tier': 'tier0_flash', 'tier_capacity': '536870912'},
                {'tier': 'tier1_flash', 'tier_capacity': '0'},
                {'tier': 'tier_enterprise', 'tier_capacity': '0'},
                {'tier': 'tier_nearline', 'tier_capacity': '0'}
            ],
            'compressed_copy': 'no', 'uncompressed_used_capacity': '536870912', 'deduplicated_copy': 'no',
            'used_capacity_before_reduction': ''
        }
        germ.return_value = {
            "id": "305", "name": "test_cvname", "master_cluster_id": "00000204204071F0",
            "master_cluster_name": "Cluster_altran-stand5", "master_vdisk_id": "305",
            "master_vdisk_name": "master34", "aux_cluster_id": "00000204202071BC",
            "aux_cluster_name": "aux_cluster_name", "aux_vdisk_id": "197",
            "aux_vdisk_name": "aux34", "primary": "master", "consistency_group_id": "19 ",
            "consistency_group_name": "test_name", "state": "consistent_synchronized",
            "bg_copy_priority": "50", "progress": "", "freeze_time": "", "status": "online",
            "sync": "", "copy_type": "global", "cycling_mode": "", "cycle_period_seconds": "300",
            "master_change_vdisk_id": "", "master_change_vdisk_name": "", "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "", "previous_primary": "", "channel": "none"
        }
        cv_detach_mock.return_value = None
        cv_delete_mock.return_value = None
        cva.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCchangevolume()
            obj.apply()
        self.assertTrue(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
