# Copyright (C) 2020 IBM CORPORATION
# Author(s):
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_mirrored_volume """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_mirrored_volume import IBMSVCvolume


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


class TestIBMSVCvolume(unittest.TestCase):
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
            IBMSVCvolume()
        print('Info: %s' % exc.value.args[0]['msg'])

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
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': '1024'
        })
        svc_obj_info_mock.return_value = [
            {
                'id': '86', 'name': 'test_vol', 'IO_group_id': '0', 'IO_group_name': 'io_grp0',
                'status': 'online', 'mdisk_grp_id': '2', 'mdisk_grp_name': 'Pool1', 'capacity': '1.00GB',
                'type': 'striped', 'formatted': 'no', 'formatting': 'yes', 'mdisk_id': '', 'mdisk_name': '',
                'FC_id': 'many', 'FC_name': 'many', 'RC_id': '86', 'RC_name': 'rcrel14',
                'vdisk_UID': '60050764008581864800000000000675', 'preferred_node_id': '1',
                'fast_write_state': 'not_empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2',
                'sync_rate': '50', 'copy_count': '1', 'se_copy_count': '0', 'filesystem': '',
                'mirror_write_priority': 'latency', 'RC_change': 'no', 'compressed_copy_count': '0',
                'access_IO_group_count': '2', 'last_access_time': '', 'parent_mdisk_grp_id': '2',
                'parent_mdisk_grp_name': 'Pool1', 'owner_type': 'none', 'owner_id': '', 'owner_name': '',
                'encrypt': 'no', 'volume_id': '86', 'volume_name': 'test_vol', 'function': 'master',
                'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '',
                'volume_group_id': '', 'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '',
                'cloud_account_name': '', 'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none',
                'backup_grain_size': '', 'deduplicated_copy_count': '0', 'protocol': ''
            },
            {
                'copy_id': '0', 'status': 'online', 'sync': 'yes', 'auto_delete': 'no', 'primary': 'yes',
                'mdisk_grp_id': '2', 'mdisk_grp_name': 'Pool1', 'type': 'striped', 'mdisk_id': '', 'mdisk_name': '',
                'fast_write_state': 'not_empty', 'used_capacity': '1.00GB', 'real_capacity': '1.00GB',
                'free_capacity': '0.00MB', 'overallocation': '100', 'autoexpand': '', 'warning': '', 'grainsize': '',
                'se_copy': 'no', 'easy_tier': 'on', 'easy_tier_status': 'balanced',
                'tiers': [
                    {'tier': 'tier_scm', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier0_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier1_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier_enterprise', 'tier_capacity': '1.00GB'},
                    {'tier': 'tier_nearline', 'tier_capacity': '0.00MB'}
                ],
                'compressed_copy': 'no', 'uncompressed_used_capacity': '1.00GB', 'parent_mdisk_grp_id': '2',
                'parent_mdisk_grp_name': 'Pool1', 'encrypt': 'no', 'deduplicated_copy': 'no', 'used_capacity_before_reduction': ''
            }
        ]
        obj = IBMSVCvolume()
        data = obj.get_existing_vdisk()
        self.assertEqual('test_vol', data[0]["name"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, svc_authorize_mock, svc_obj_info_mock1, svc_obj_info_mock2):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': '1024'
        })
        vdisk_data = [
            {
                'id': '86', 'name': 'test_vol', 'IO_group_id': '0', 'IO_group_name': 'io_grp0',
                'status': 'online', 'mdisk_grp_id': '2', 'mdisk_grp_name': 'Pool1', 'capacity': '1.00GB',
                'type': 'striped', 'formatted': 'no', 'formatting': 'yes', 'mdisk_id': '', 'mdisk_name': '',
                'FC_id': 'many', 'FC_name': 'many', 'RC_id': '86', 'RC_name': 'rcrel14',
                'vdisk_UID': '60050764008581864800000000000675', 'preferred_node_id': '1',
                'fast_write_state': 'not_empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2',
                'sync_rate': '50', 'copy_count': '1', 'se_copy_count': '0', 'filesystem': '',
                'mirror_write_priority': 'latency', 'RC_change': 'no', 'compressed_copy_count': '0',
                'access_IO_group_count': '2', 'last_access_time': '', 'parent_mdisk_grp_id': '2',
                'parent_mdisk_grp_name': 'Pool1', 'owner_type': 'none', 'owner_id': '', 'owner_name': '',
                'encrypt': 'no', 'volume_id': '86', 'volume_name': 'test_vol', 'function': 'master',
                'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '',
                'volume_group_id': '', 'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '',
                'cloud_account_name': '', 'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none',
                'backup_grain_size': '', 'deduplicated_copy_count': '0', 'protocol': ''
            },
            {
                'copy_id': '0', 'status': 'online', 'sync': 'yes', 'auto_delete': 'no', 'primary': 'yes',
                'mdisk_grp_id': '2', 'mdisk_grp_name': 'Pool1', 'type': 'striped', 'mdisk_id': '', 'mdisk_name': '',
                'fast_write_state': 'not_empty', 'used_capacity': '1.00GB', 'real_capacity': '1.00GB',
                'free_capacity': '0.00MB', 'overallocation': '100', 'autoexpand': '', 'warning': '', 'grainsize': '',
                'se_copy': 'no', 'easy_tier': 'on', 'easy_tier_status': 'balanced',
                'tiers': [
                    {'tier': 'tier_scm', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier0_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier1_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier_enterprise', 'tier_capacity': '1.00GB'},
                    {'tier': 'tier_nearline', 'tier_capacity': '0.00MB'}
                ],
                'compressed_copy': 'no', 'uncompressed_used_capacity': '1.00GB', 'parent_mdisk_grp_id': '2',
                'parent_mdisk_grp_name': 'Pool1', 'encrypt': 'no', 'deduplicated_copy': 'no', 'used_capacity_before_reduction': ''
            }
        ]
        svc_obj_info_mock1.return_value = {
            'id': '2', 'name': 'Pool1', 'status': 'online', 'mdisk_count': '1', 'vdisk_count': '30',
            'capacity': '553.00GB', 'extent_size': '1024', 'free_capacity': '474.00GB', 'virtual_capacity': '6.73GB',
            'used_capacity': '1.08GB', 'real_capacity': '51.47GB', 'overallocation': '1', 'warning': '80',
            'easy_tier': 'auto', 'easy_tier_status': 'balanced',
            'tiers': [
                {
                    'tier': 'tier_scm', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                },
                {
                    'tier': 'tier0_flash', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                },
                {
                    'tier': 'tier1_flash', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                },
                {
                    'tier': 'tier_enterprise', 'tier_mdisk_count': '1', 'tier_capacity': '553.00GB', 'tier_free_capacity': '474.00GB'
                },
                {
                    'tier': 'tier_nearline', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                }
            ],
            'compression_active': 'yes', 'compression_virtual_capacity': '200.00MB', 'compression_compressed_capacity': '0.31MB',
            'compression_uncompressed_capacity': '0.00MB', 'site_id': '1', 'site_name': 'site1', 'parent_mdisk_grp_id': '2',
            'parent_mdisk_grp_name': 'Pool1', 'child_mdisk_grp_count': '0', 'child_mdisk_grp_capacity': '0.00MB',
            'type': 'parent', 'encrypt': 'no', 'owner_type': 'none', 'owner_id': '', 'owner_name': '', 'data_reduction': 'no',
            'used_capacity_before_reduction': '0.00MB', 'used_capacity_after_reduction': '0.00MB', 'overhead_capacity': '0.00MB',
            'deduplication_capacity_saving': '0.00MB', 'reclaimable_capacity': '0.00MB', 'physical_capacity': '553.00GB',
            'physical_free_capacity': '474.00GB', 'shared_resources': 'no', 'vdisk_protection_enabled': 'yes',
            'vdisk_protection_status': 'inactive', 'easy_tier_fcm_over_allocation_max': '', 'auto_expand': 'no',
            'auto_expand_max_capacity': '0.00MB'
        }
        svc_obj_info_mock2.return_value = {
            'id': '3', 'name': 'Pool2', 'status': 'online', 'mdisk_count': '1', 'vdisk_count': '27', 'capacity': '2.72TB',
            'extent_size': '1024', 'free_capacity': '2.65TB', 'virtual_capacity': '6.44GB', 'used_capacity': '910.38MB',
            'real_capacity': '51.25GB', 'overallocation': '0', 'warning': '80', 'easy_tier': 'auto', 'easy_tier_status': 'balanced',
            'tiers': [
                {
                    'tier': 'tier_scm', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                },
                {
                    'tier': 'tier0_flash', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                },
                {
                    'tier': 'tier1_flash', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                },
                {
                    'tier': 'tier_enterprise', 'tier_mdisk_count': '0', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'
                },
                {
                    'tier': 'tier_nearline', 'tier_mdisk_count': '1', 'tier_capacity': '2.72TB', 'tier_free_capacity': '2.65TB'
                }
            ], 'compression_active': 'no', 'compression_virtual_capacity': '0.00MB', 'compression_compressed_capacity': '0.00MB',
            'compression_uncompressed_capacity': '0.00MB', 'site_id': '2', 'site_name': 'site2',
            'parent_mdisk_grp_id': '3', 'parent_mdisk_grp_name': 'Pool2', 'child_mdisk_grp_count': '0',
            'child_mdisk_grp_capacity': '0.00MB', 'type': 'parent', 'encrypt': 'no', 'owner_type': 'none',
            'owner_id': '', 'owner_name': '', 'data_reduction': 'no', 'used_capacity_before_reduction': '0.00MB',
            'used_capacity_after_reduction': '0.00MB', 'overhead_capacity': '0.00MB', 'deduplication_capacity_saving': '0.00MB',
            'reclaimable_capacity': '0.00MB', 'physical_capacity': '2.72TB', 'physical_free_capacity': '2.65TB',
            'shared_resources': 'no', 'vdisk_protection_enabled': 'yes', 'vdisk_protection_status': 'inactive',
            'easy_tier_fcm_over_allocation_max': '', 'auto_expand': 'no', 'auto_expand_max_capacity': '0.00MB'
        }
        obj = IBMSVCvolume()
        data = obj.basic_checks(vdisk_data)
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_discover_site_from_pools(self, svc_authorize_mock, soi1, soi2):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': '1024'
        })
        soi1.return_value = {
            "id": "2", "name": "Pool1", "status": "online", "mdisk_count": "1", "vdisk_count": "32",
            "capacity": "553.00GB", "extent_size": "1024", "free_capacity": "472.00GB",
            "virtual_capacity": "8.73GB", "used_capacity": "2.08GB", "real_capacity": "52.48GB", "overallocation": "1",
            "warning": "80", "easy_tier": "auto", "easy_tier_status": "balanced",
            "tiers": [
                {"tier": "tier_scm", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"},
                {"tier": "tier0_flash", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"},
                {"tier": "tier1_flash", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"},
                {"tier": "tier_enterprise", "tier_mdisk_count": "1", "tier_capacity": "553.00GB", "tier_free_capacity": "472.00GB"},
                {"tier": "tier_nearline", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"}
            ],
            "compression_active": "yes", "compression_virtual_capacity": "200.00MB",
            "compression_compressed_capacity": "0.31MB", "compression_uncompressed_capacity": "0.00MB", "site_id": "1",
            "site_name": "site1", "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "Pool1", "child_mdisk_grp_count": "0",
            "child_mdisk_grp_capacity": "0.00MB", "type": "parent", "encrypt": "no", "owner_type": "none", "owner_id": "",
            "owner_name": "", "data_reduction": "no", "used_capacity_before_reduction": "0.00MB", "used_capacity_after_reduction": "0.00MB",
            "overhead_capacity": "0.00MB", "deduplication_capacity_saving": "0.00MB", "reclaimable_capacity": "0.00MB",
            "physical_capacity": "553.00GB", "physical_free_capacity": "472.00GB", "shared_resources": "no", "vdisk_protection_enabled": "yes",
            "vdisk_protection_status": "inactive", "easy_tier_fcm_over_allocation_max": "", "auto_expand": "no", "auto_expand_max_capacity": "0.00MB"
        }
        soi2.return_value = {
            "id": "3", "name": "Pool2", "status": "online", "mdisk_count": "1", "vdisk_count": "29", "capacity": "2.72TB", "extent_size": "1024",
            "free_capacity": "2.64TB", "virtual_capacity": "8.44GB", "used_capacity": "1.89GB", "real_capacity": "52.27GB", "overallocation": "0",
            "warning": "80", "easy_tier": "auto", "easy_tier_status": "balanced",
            "tiers": [
                {"tier": "tier_scm", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"},
                {"tier": "tier0_flash", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"},
                {"tier": "tier1_flash", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"},
                {"tier": "tier_enterprise", "tier_mdisk_count": "0", "tier_capacity": "0.00MB", "tier_free_capacity": "0.00MB"},
                {"tier": "tier_nearline", "tier_mdisk_count": "1", "tier_capacity": "2.72TB", "tier_free_capacity": "2.64TB"}
            ],
            "compression_active": "no", "compression_virtual_capacity": "0.00MB", "compression_compressed_capacity": "0.00MB",
            "compression_uncompressed_capacity": "0.00MB", "site_id": "2", "site_name": "site2", "parent_mdisk_grp_id": "3",
            "parent_mdisk_grp_name": "Pool2", "child_mdisk_grp_count": "0", "child_mdisk_grp_capacity": "0.00MB", "type": "parent",
            "encrypt": "no", "owner_type": "none", "owner_id": "", "owner_name": "", "data_reduction": "no", "used_capacity_before_reduction": "0.00MB",
            "used_capacity_after_reduction": "0.00MB", "overhead_capacity": "0.00MB", "deduplication_capacity_saving": "0.00MB",
            "reclaimable_capacity": "0.00MB", "physical_capacity": "2.72TB", "physical_free_capacity": "2.64TB", "shared_resources": "no",
            "vdisk_protection_enabled": "yes", "vdisk_protection_status": "inactive", "easy_tier_fcm_over_allocation_max": "", "auto_expand": "no",
            "auto_expand_max_capacity": "0.00MB"
        }
        obj = IBMSVCvolume()
        obj.poolA_data = {
            "site_name": "site2"
        }
        obj.poolB_data = {
            "site_name": "site2"
        }
        data = obj.discover_site_from_pools()
        self.assertEqual('site2', data[0])
        self.assertEqual('site2', data[1])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vdisk_probe(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': '1024'
        })
        arg_data = [
            {
                'id': '86', 'name': 'test_vol', 'IO_group_id': '0', 'IO_group_name': 'io_grp0',
                'status': 'online', 'mdisk_grp_id': '2', 'mdisk_grp_name': 'Pool1', 'capacity': '1.00GB',
                'type': 'striped', 'formatted': 'no', 'formatting': 'yes', 'mdisk_id': '', 'mdisk_name': '',
                'FC_id': 'many', 'FC_name': 'many', 'RC_id': '86', 'RC_name': 'rcrel14',
                'vdisk_UID': '60050764008581864800000000000675', 'preferred_node_id': '1',
                'fast_write_state': 'not_empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2',
                'sync_rate': '50', 'copy_count': '1', 'se_copy_count': '0', 'filesystem': '',
                'mirror_write_priority': 'latency', 'RC_change': 'no', 'compressed_copy_count': '0',
                'access_IO_group_count': '2', 'last_access_time': '', 'parent_mdisk_grp_id': '2',
                'parent_mdisk_grp_name': 'Pool1', 'owner_type': 'none', 'owner_id': '', 'owner_name': '',
                'encrypt': 'no', 'volume_id': '86', 'volume_name': 'test_vol', 'function': 'master',
                'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '',
                'volume_group_id': '', 'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '',
                'cloud_account_name': '', 'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none',
                'backup_grain_size': '', 'deduplicated_copy_count': '0', 'protocol': ''
            },
            {
                'copy_id': '0', 'status': 'online', 'sync': 'yes', 'auto_delete': 'no', 'primary': 'yes',
                'mdisk_grp_id': '2', 'mdisk_grp_name': 'Pool1', 'type': 'striped', 'mdisk_id': '', 'mdisk_name': '',
                'fast_write_state': 'not_empty', 'used_capacity': '1.00GB', 'real_capacity': '1.00GB',
                'free_capacity': '0.00MB', 'overallocation': '100', 'autoexpand': '', 'warning': '', 'grainsize': '',
                'se_copy': 'no', 'easy_tier': 'on', 'easy_tier_status': 'balanced',
                'tiers': [
                    {'tier': 'tier_scm', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier0_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier1_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier_enterprise', 'tier_capacity': '1.00GB'},
                    {'tier': 'tier_nearline', 'tier_capacity': '0.00MB'}
                ],
                'compressed_copy': 'no', 'uncompressed_used_capacity': '1.00GB', 'parent_mdisk_grp_id': '2',
                'parent_mdisk_grp_name': 'Pool1', 'encrypt': 'no', 'deduplicated_copy': 'no', 'used_capacity_before_reduction': ''
            }
        ]
        obj = IBMSVCvolume()
        data = obj.vdisk_probe(arg_data)
        self.assertEqual([], data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_volume_create(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': '1024'
        })
        svc_run_command_mock.return_value = {
            'id': '86',
            'message': 'Volume, id [86], successfully created'
        }
        obj = IBMSVCvolume()
        data = obj.volume_create()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vdisk_create(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': '1024'
        })
        svc_run_command_mock.return_value = {
            'id': '86',
            'message': 'Volume, id [86], successfully created'
        }
        obj = IBMSVCvolume()
        data = obj.vdisk_create()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_addvolumecopy(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2'
        })
        obj = IBMSVCvolume()
        data = obj.addvolumecopy()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.discover_site_from_pools')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_addvdiskcopy(self, svc_authorize_mock, svc_run_command_mock, dsfp):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2'
        })
        dsfp.return_value = ('site1', 'site1')
        svc_run_command_mock.return_value = None
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCvolume()
            data = obj.addvdiskcopy()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rmvolumecopy(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2'
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCvolume()
        data = obj.rmvolumecopy()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vdisk_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2'
        })
        obj = IBMSVCvolume()
        data = obj.vdisk_update([])
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_volume_delete(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2'
        })
        obj = IBMSVCvolume()
        data = obj.volume_delete()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_discover_system_topology(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_vol',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2'
        })
        svc_run_command_mock.return_value = {
            'id': '0000010021606192', 'name': 'altran-v7khs', 'location': 'local', 'partnership': '',
            'total_mdisk_capacity': '5.8TB', 'space_in_mdisk_grps': '5.8TB', 'space_allocated_to_vdisks': '134.76GB',
            'total_free_space': '5.6TB', 'total_vdiskcopy_capacity': '13.76GB', 'total_used_capacity': '30.11GB',
            'total_overallocation': '0', 'total_vdisk_capacity': '13.66GB', 'total_allocated_extent_capacity': '189.00GB',
            'statistics_status': 'on', 'statistics_frequency': '15', 'cluster_locale': 'en_US', 'time_zone': '522 UTC',
            'code_level': '8.4.0.0 (build 152.16.2009091545000)', 'console_IP': '9.71.42.198:443', 'id_alias': '0000010021606192',
            'gm_link_tolerance': '300', 'gm_inter_cluster_delay_simulation': '0', 'gm_intra_cluster_delay_simulation': '0',
            'gm_max_host_delay': '5', 'email_reply': '', 'email_contact': '', 'email_contact_primary': '',
            'email_contact_alternate': '', 'email_contact_location': '', 'email_contact2': '', 'email_contact2_primary': '',
            'email_contact2_alternate': '', 'email_state': 'stopped', 'inventory_mail_interval': '0', 'cluster_ntp_IP_address': '',
            'cluster_isns_IP_address': '', 'iscsi_auth_method': 'none', 'iscsi_chap_secret': '', 'auth_service_configured': 'no',
            'auth_service_enabled': 'no', 'auth_service_url': '', 'auth_service_user_name': '', 'auth_service_pwd_set': 'no',
            'auth_service_cert_set': 'no', 'auth_service_type': 'ldap', 'relationship_bandwidth_limit': '25',
            'tiers': [
                {'tier': 'tier_scm', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'},
                {'tier': 'tier0_flash', 'tier_capacity': '2.51TB', 'tier_free_capacity': '2.47TB'},
                {'tier': 'tier1_flash', 'tier_capacity': '0.00MB', 'tier_free_capacity': '0.00MB'},
                {'tier': 'tier_enterprise', 'tier_capacity': '553.00GB', 'tier_free_capacity': '474.00GB'},
                {'tier': 'tier_nearline', 'tier_capacity': '2.72TB', 'tier_free_capacity': '2.65TB'}
            ],
            'easy_tier_acceleration': 'off', 'has_nas_key': 'no', 'layer': 'storage', 'rc_buffer_size': '48',
            'compression_active': 'yes', 'compression_virtual_capacity': '200.00MB', 'compression_compressed_capacity': '0.31MB',
            'compression_uncompressed_capacity': '0.00MB', 'cache_prefetch': 'on', 'email_organization': '',
            'email_machine_address': '', 'email_machine_city': '', 'email_machine_state': 'XX', 'email_machine_zip': '',
            'email_machine_country': '', 'total_drive_raw_capacity': '10.10TB', 'compression_destage_mode': 'off',
            'local_fc_port_mask': '1111111111111111111111111111111111111111111111111111111111111111',
            'partner_fc_port_mask': '1111111111111111111111111111111111111111111111111111111111111111', 'high_temp_mode': 'off',
            'topology': 'hyperswap', 'topology_status': 'dual_site', 'rc_auth_method': 'none', 'vdisk_protection_time': '15',
            'vdisk_protection_enabled': 'no', 'product_name': 'IBM Storwize V7000', 'odx': 'off', 'max_replication_delay': '0',
            'partnership_exclusion_threshold': '315', 'gen1_compatibility_mode_enabled': 'no', 'ibm_customer': '',
            'ibm_component': '', 'ibm_country': '', 'tier_scm_compressed_data_used': '0.00MB',
            'tier0_flash_compressed_data_used': '0.00MB', 'tier1_flash_compressed_data_used': '0.00MB',
            'tier_enterprise_compressed_data_used': '36.00MB', 'tier_nearline_compressed_data_used': '0.00MB',
            'total_reclaimable_capacity': '0.00MB', 'physical_capacity': '5.77TB', 'physical_free_capacity': '5.58TB',
            'used_capacity_before_reduction': '0.00MB', 'used_capacity_after_reduction': '2.04GB', 'overhead_capacity': '26.00GB',
            'deduplication_capacity_saving': '0.00MB', 'enhanced_callhome': 'on', 'censor_callhome': 'off', 'host_unmap': 'off',
            'backend_unmap': 'on', 'quorum_mode': 'standard', 'quorum_site_id': '', 'quorum_site_name': '', 'quorum_lease': 'short',
            'parent_seq_no': '', 'automatic_vdisk_analysis_enabled': 'on'
        }
        obj = IBMSVCvolume()
        data = obj.discover_system_topology()
        self.assertEqual('hyperswap', data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.discover_system_topology')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.basic_checks')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hs_volume(self, svc_authorize_mock, bc, dst, gev, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_volume',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': 1024
        })
        gev.return_value = None
        src.return_value = {
            'id': '86',
            'message': 'Volume, id [86], successfully created'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCvolume()
            data = obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.discover_system_topology')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.basic_checks')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hs_volume_thin(self, svc_authorize_mock, bc, dst, gev, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_volume',
            'state': 'present',
            'poolA': 'Pool1',
            'poolB': 'Pool2',
            'size': 1024,
            'thin': True
        })
        gev.return_value = None
        src.return_value = {
            'id': '86',
            'message': 'Volume, id [86], successfully created'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCvolume()
            data = obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.discover_system_topology')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_mirrored_volume.IBMSVCvolume.basic_checks')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_hs_volume(self, svc_authorize_mock, bc, dst, gev, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'type': 'local hyperswap',
            'name': 'test_volume',
            'state': 'absent'
        })
        gev.return_value = [
            {
                'id': '130', 'name': 'test_volume', 'IO_group_id': '0', 'IO_group_name': 'io_grp0', 'status': 'online',
                'mdisk_grp_id': '2', 'mdisk_grp_name': 'Pool1', 'capacity': '1.00GB', 'type': 'striped', 'formatted': 'yes',
                'formatting': 'no', 'mdisk_id': '', 'mdisk_name': '', 'FC_id': 'many', 'FC_name': 'many', 'RC_id': '130',
                'RC_name': 'rcrel25', 'vdisk_UID': '600507640085818648000000000006A1', 'preferred_node_id': '2',
                'fast_write_state': 'empty', 'cache': 'readwrite', 'udid': '', 'fc_map_count': '2', 'sync_rate': '50',
                'copy_count': '1', 'se_copy_count': '0', 'filesystem': '', 'mirror_write_priority': 'latency',
                'RC_change': 'no', 'compressed_copy_count': '0', 'access_IO_group_count': '2', 'last_access_time': '',
                'parent_mdisk_grp_id': '2', 'parent_mdisk_grp_name': 'Pool1', 'owner_type': 'none', 'owner_id': '',
                'owner_name': '', 'encrypt': 'no', 'volume_id': '130', 'volume_name': 'test_volume', 'function': 'master',
                'throttle_id': '', 'throttle_name': '', 'IOPs_limit': '', 'bandwidth_limit_MB': '', 'volume_group_id': '',
                'volume_group_name': '', 'cloud_backup_enabled': 'no', 'cloud_account_id': '', 'cloud_account_name': '',
                'backup_status': 'off', 'last_backup_time': '', 'restore_status': 'none', 'backup_grain_size': '',
                'deduplicated_copy_count': '0', 'protocol': ''
            },
            {
                'copy_id': '0', 'status': 'online', 'sync': 'yes', 'auto_delete': 'no', 'primary': 'yes', 'mdisk_grp_id': '2',
                'mdisk_grp_name': 'Pool1', 'type': 'striped', 'mdisk_id': '', 'mdisk_name': '', 'fast_write_state': 'empty',
                'used_capacity': '1.00GB', 'real_capacity': '1.00GB', 'free_capacity': '0.00MB', 'overallocation': '100',
                'autoexpand': '', 'warning': '', 'grainsize': '', 'se_copy': 'no', 'easy_tier': 'on',
                'easy_tier_status': 'balanced', 'tiers': [
                    {'tier': 'tier_scm', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier0_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier1_flash', 'tier_capacity': '0.00MB'},
                    {'tier': 'tier_enterprise', 'tier_capacity': '1.00GB'},
                    {'tier': 'tier_nearline', 'tier_capacity': '0.00MB'}
                ],
                'compressed_copy': 'no', 'uncompressed_used_capacity': '1.00GB', 'parent_mdisk_grp_id': '2',
                'parent_mdisk_grp_name': 'Pool1', 'encrypt': 'no', 'deduplicated_copy': 'no', 'used_capacity_before_reduction': ''
            }
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCvolume()
            data = obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
