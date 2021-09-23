# Copyright (C) 2020 IBM CORPORATION
# Author(s):
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_migration """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_migration import IBMSVCMigrate


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


class TestIBMSVCMigrate(unittest.TestCase):
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
            IBMSVCMigrate()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_discover_partner_system(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = {
            "id": "0000010022206192", "name": "Cluster_9.71.42.198", "location": "remote",
            "partnership": "fully_configured", "code_level": "8.4.2.0 (build 154.19.2106231326000)",
            "console_IP": "9.71.42.198:443", "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0", "gm_intra_cluster_delay_simulation": "0",
            "relationship_bandwidth_limit": "25", "gm_max_host_delay": "5", "type": "fc",
            "cluster_ip": "", "chap_secret": "", "event_log_sequence": "", "link_bandwidth_mbits": "100",
            "background_copy_rate": "50", "max_replication_delay": "0", "compressed": "no", "link1": "",
            "link2": "", "link1_ip_id": "", "link2_ip_id": ""
        }
        m = IBMSVCMigrate()
        data = m.discover_partner_system()
        self.assertEqual(data, '9.71.42.198')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_when_partner_local(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = {
            "id": "0000010022206192", "name": "Cluster_9.71.42.198", "location": "local",
            "partnership": "fully_configured", "code_level": "8.4.2.0 (build 154.19.2106231326000)",
            "console_IP": "9.71.42.198:443", "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0", "gm_intra_cluster_delay_simulation": "0",
            "relationship_bandwidth_limit": "25", "gm_max_host_delay": "5", "type": "fc",
            "cluster_ip": "", "chap_secret": "", "event_log_sequence": "", "link_bandwidth_mbits": "100",
            "background_copy_rate": "50", "max_replication_delay": "0", "compressed": "no", "link1": "",
            "link2": "", "link1_ip_id": "", "link2_ip_id": ""
        }
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            data = m.discover_partner_system()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_when_partner_absent(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = None
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            data = m.discover_partner_system()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.discover_partner_system')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_construct_remote_rest(self, auth, dps):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        dps.return_value = "9.71.42.198"
        m = IBMSVCMigrate()
        data = m.construct_remote_rest()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.construct_remote_rest')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_vdisk(self, auth, cmd1, crr, cmd2):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        cmd2.return_value = None
        m = IBMSVCMigrate()
        m.get_existing_vdisk()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, auth):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        m = IBMSVCMigrate()
        m.basic_checks()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_missing_token_parameter(self, auth):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            # "username": "superuser",
            # "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.basic_checks()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_missing_initiate_parameters(self, auth):
        set_module_args({
            # "source_volume": "tesla",
            # "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            # "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            # "remote_username": "superuser",
            # "remote_password": "passw0rd",
            # "relationship_name": "migrate_tesla",
            # "remote_pool": "site2pool1"
        })
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.basic_checks()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_missing_switch_parameters(self, auth):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            # "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.basic_checks()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_missing_cleanup_parameters(self, auth):
        set_module_args({
            # "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.basic_checks()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_source_hosts(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = [
            {
                "id": "69",
                "name": "tesla",
                "SCSI_id": "3",
                "host_id": "0",
                "host_name": "altran-esxi-06-iscsi",
                "vdisk_UID": "60050768108180ED7000000000000388",
                "IO_group_id": "0",
                "IO_group_name": "io_grp0",
                "mapping_type": "private",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi"
            },
            {
                "id": "69",
                "name": "tesla",
                "SCSI_id": "0",
                "host_id": "86",
                "host_name": "host_x",
                "vdisk_UID": "60050768108180ED7000000000000388",
                "IO_group_id": "0",
                "IO_group_name": "io_grp0",
                "mapping_type": "private",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi"
            }
        ]
        m = IBMSVCMigrate()
        data = m.get_source_hosts()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.discover_partner_system')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_map_host_vol_remote(self, auth, dps, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        dps.return_value = "9.71.42.198"
        cmd1.return_value = {
            "id": "2",
            "message": "Host, id [2], successfully created"
        }
        m = IBMSVCMigrate()
        argument = ['host1']
        m.map_host_vol_remote(argument)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.discover_partner_system')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_return_remote_hosts(self, auth, dps, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        dps.return_value = "9.71.42.198"
        cmd1.return_value = [
            {
                "id": "0",
                "name": "altran-hv-1",
                "port_count": "2",
                "iogrp_count": "4",
                "status": "degraded",
                "site_id": "",
                "site_name": "",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "portset_id": "",
                "portset_name": ""
            },
            {
                "id": "1",
                "name": "altran-esxi-06-iscsi",
                "port_count": "2",
                "iogrp_count": "4",
                "status": "online",
                "site_id": "1",
                "site_name": "site1",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "portset_id": "",
                "portset_name": ""
            },
            {
                "id": "3",
                "name": "altran-esxi-07-iscsi",
                "port_count": "2",
                "iogrp_count": "4",
                "status": "online",
                "site_id": "2",
                "site_name": "site2",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "portset_id": "",
                "portset_name": ""
            }
        ]
        m = IBMSVCMigrate()
        data = m.return_remote_hosts()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.create_remote_hosts')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_replicate_source_hosts(self, auth, cmd1, crr):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        argument = ["tesla"]
        argument = [
            {
                "id": "69",
                "name": "tesla",
                "SCSI_id": "3",
                "host_id": "0",
                "host_name": "altran-esxi-06-iscsi",
                "vdisk_UID": "60050768108180ED7000000000000388",
                "IO_group_id": "0",
                "IO_group_name": "io_grp0",
                "mapping_type": "private",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi"
            }
        ]
        cmd1.return_value = {
            "id": "0",
            "name": "altran-esxi-06-iscsi",
            "port_count": "2",
            "type": "generic",
            "mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "iogrp_count": "4",
            "status": "online",
            "site_id": "1",
            "site_name": "site1",
            "host_cluster_id": "",
            "host_cluster_name": "",
            "protocol": "scsi",
            "status_policy": "redundant",
            "status_site": "all",
            "nodes": [
                {
                    "WWPN": "2100000E1EC228B9",
                    "node_logged_in_count": "4",
                    "state": "active"
                },
                {
                    "WWPN": "2100000E1EC228B8",
                    "node_logged_in_count": "2",
                    "state": "active"
                }
            ],
            "owner_id": "",
            "owner_name": "",
            "portset_id": "",
            "portset_name": ""
        }
        m = IBMSVCMigrate()
        m.replicate_source_hosts(argument)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.map_host_vol_remote')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.construct_remote_rest')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.return_remote_hosts')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_remote_hosts(self, auth, rrh, crr, src, mhvr):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        argument_1 = {
            "altran-esxi-06-iscsi": ["2100000E1EC228B9", "2100000E1EC228B8"],
            "host_x": ["50050768100225E8", "50050768100125E8"]
        }
        argument_2 = {}
        rrh.return_value = [
            {
                "id": "0",
                "name": "altran-hv-1",
                "port_count": "2",
                "iogrp_count": "4",
                "status": "degraded",
                "site_id": "",
                "site_name": "",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "portset_id": "",
                "portset_name": ""
            },
            {
                "id": "1",
                "name": "altran-esxi-06-iscsi",
                "port_count": "2",
                "iogrp_count": "4",
                "status": "online",
                "site_id": "1",
                "site_name": "site1",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "portset_id": "",
                "portset_name": ""
            },
            {
                "id": "3",
                "name": "altran-esxi-07-iscsi",
                "port_count": "2",
                "iogrp_count": "4",
                "status": "online",
                "site_id": "2",
                "site_name": "site2",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "portset_id": "",
                "portset_name": ""
            }
        ]
        m = IBMSVCMigrate()
        m.create_remote_hosts(argument_1, argument_2)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.construct_remote_rest')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vdisk_create(self, auth, crr, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        argument = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "", "RC_name": "",
                "vdisk_UID": "60050768108180ED700000000000038E", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "210811071953", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "", "owner_name": "",
                "encrypt": "no", "volume_id": "69", "volume_name": "tesla", "function": "", "throttle_id": "",
                "throttle_name": "", "IOPs_limit": "", "bandwidth_limit_MB": "", "volume_group_id": "",
                "volume_group_name": "", "cloud_backup_enabled": "no", "cloud_account_id": "",
                "cloud_account_name": "", "backup_status": "off", "last_backup_time": "",
                "restore_status": "none", "backup_grain_size": "", "deduplicated_copy_count": "0",
                "protocol": "scsi", "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100", "autoexpand": "",
                "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        cmd1.return_value = {
            "id": "77",
            "message": "Volume, id [77], successfully created"
        }
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.vdisk_create(argument)
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.construct_remote_rest')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_verify_remote_volume_mapping(self, auth, crr, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = None
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.verify_remote_volume_mapping()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_verify_target(self, auth, cmd1, cmd2):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        source_data = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        target_data = None
        cmd1.return_value = source_data, target_data
        m = IBMSVCMigrate()
        m.verify_target()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_source_volume_absent(self, auth, cmd1, cmd2):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        source_data = None
        target_data = None
        cmd1.return_value = source_data, target_data
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.verify_target()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_when_source_volume_in_relationship(self, auth, cmd1, cmd2):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        source_data = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "x", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        target_data = None
        cmd1.return_value = source_data, target_data
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.verify_target()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_when_target_volume_in_relationship(self, auth, cmd1, cmd2):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        source_data = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        target_data = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "x", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        cmd1.return_value = source_data, target_data
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.verify_target()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_when_target_exist_in_different_size(self, auth, cmd1, cmd2):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        source_data = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        target_data = [
            {
                "id": "69", "name": "tesla_target", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485766", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        cmd1.return_value = source_data, target_data
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.verify_target()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_relationsip(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = {
            "id": "69",
            "message": "RC Relationship, id [69], successfully created"
        }
        m = IBMSVCMigrate()
        m.create_relationship()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vol_relationsip(self, auth, cmd1, cmd2):
        set_module_args({
            "clustername": "9.71.42.119",
            "username": "superuser",
            "password": "passw0rd",
            "state": "cleanup",
            "source_volume": "tesla"
        })
        source_data = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        target_data = None
        cmd1.return_value = source_data, target_data
        cmd2.return_value = {
            "id": "69",
            "name": "migrate_tesla",
            "master_cluster_id": "0000020420603B5C",
            "master_cluster_name": "Cluster_9.71.42.119",
            "master_vdisk_id": "69",
            "master_vdisk_name": "tesla",
            "aux_cluster_id": "0000010022206192",
            "aux_cluster_name": "Cluster_9.71.42.198",
            "aux_vdisk_id": "77",
            "aux_vdisk_name": "tesla_target",
            "primary": "aux",
            "consistency_group_id": "",
            "consistency_group_name": "",
            "state": "consistent_synchronized",
            "bg_copy_priority": "50",
            "progress": "",
            "freeze_time": "",
            "status": "online",
            "sync": "",
            "copy_type": "migration",
            "cycling_mode": "",
            "cycle_period_seconds": "300",
            "master_change_vdisk_id": "",
            "master_change_vdisk_name": "",
            "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "",
            "previous_primary": "",
            "channel": "none"
        }
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.source_vol_relationship("tesla")
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vol_relationsip_fail_when_source_missng(self, auth, cmd1, cmd2):
        set_module_args({
            "clustername": "9.71.42.119",
            "username": "superuser",
            "password": "passw0rd",
            "state": "cleanup",
            "source_volume": "tesla"
        })
        source_data = None
        target_data = None
        cmd1.return_value = source_data, target_data
        cmd2.return_value = {
            "id": "69",
            "name": "migrate_tesla",
            "master_cluster_id": "0000020420603B5C",
            "master_cluster_name": "Cluster_9.71.42.119",
            "master_vdisk_id": "69",
            "master_vdisk_name": "tesla",
            "aux_cluster_id": "0000010022206192",
            "aux_cluster_name": "Cluster_9.71.42.198",
            "aux_vdisk_id": "77",
            "aux_vdisk_name": "tesla_target",
            "primary": "aux",
            "consistency_group_id": "",
            "consistency_group_name": "",
            "state": "consistent_synchronized",
            "bg_copy_priority": "50",
            "progress": "",
            "freeze_time": "",
            "status": "online",
            "sync": "",
            "copy_type": "migration",
            "cycling_mode": "",
            "cycle_period_seconds": "300",
            "master_change_vdisk_id": "",
            "master_change_vdisk_name": "",
            "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "",
            "previous_primary": "",
            "channel": "none"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            m = IBMSVCMigrate()
            m.source_vol_relationship("tesla")
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_migration.IBMSVCMigrate.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vol_relationsip_fail_when_source_copytype_not_migration(self, auth, cmd1, cmd2):
        set_module_args({
            "clustername": "9.71.42.119",
            "username": "superuser",
            "password": "passw0rd",
            "state": "cleanup",
            "source_volume": "tesla"
        })
        source_data = [
            {
                "id": "69", "name": "tesla", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1",
                "capacity": "10485760", "type": "striped", "formatted": "yes", "formatting": "no",
                "mdisk_id": "", "mdisk_name": "", "FC_id": "", "FC_name": "", "RC_id": "",
                "RC_name": "", "vdisk_UID": "60050768108180ED7000000000000388", "preferred_node_id": "1",
                "fast_write_state": "not_empty", "cache": "readwrite", "udid": "", "fc_map_count": "0",
                "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "filesystem": "",
                "mirror_write_priority": "latency", "RC_change": "no", "compressed_copy_count": "0",
                "access_IO_group_count": "1", "last_access_time": "", "parent_mdisk_grp_id": "2",
                "parent_mdisk_grp_name": "site1pool1", "owner_type": "none", "owner_id": "",
                "owner_name": "", "encrypt": "no", "volume_id": "69", "volume_name": "tesla",
                "function": "", "throttle_id": "", "throttle_name": "", "IOPs_limit": "",
                "bandwidth_limit_MB": "", "volume_group_id": "", "volume_group_name": "",
                "cloud_backup_enabled": "no", "cloud_account_id": "", "cloud_account_name": "",
                "backup_status": "off", "last_backup_time": "", "restore_status": "none",
                "backup_grain_size": "", "deduplicated_copy_count": "0", "protocol": "scsi",
                "preferred_node_name": "node1", "safeguarded_expiration_time": "",
                "safeguarded_backup_count": "0"
            },
            {
                "copy_id": "0", "status": "online", "sync": "yes", "auto_delete": "no", "primary": "yes",
                "mdisk_grp_id": "2", "mdisk_grp_name": "site1pool1", "type": "striped", "mdisk_id": "",
                "mdisk_name": "", "fast_write_state": "not_empty", "used_capacity": "10485760",
                "real_capacity": "10485760", "free_capacity": "0", "overallocation": "100",
                "autoexpand": "", "warning": "", "grainsize": "", "se_copy": "no", "easy_tier": "on",
                "easy_tier_status": "balanced", "tiers": [
                    {"tier": "tier_scm", "tier_capacity": "0"},
                    {"tier": "tier0_flash", "tier_capacity": "10485760"},
                    {"tier": "tier1_flash", "tier_capacity": "0"},
                    {"tier": "tier_enterprise", "tier_capacity": "0"},
                    {"tier": "tier_nearline", "tier_capacity": "0"}
                ], "compressed_copy": "no", "uncompressed_used_capacity": "10485760",
                "parent_mdisk_grp_id": "2", "parent_mdisk_grp_name": "site1pool1", "encrypt": "no",
                "deduplicated_copy": "no", "used_capacity_before_reduction": "",
                "safeguarded_mdisk_grp_id": "", "safeguarded_mdisk_grp_name": ""
            }
        ]
        target_data = None
        cmd1.return_value = source_data, target_data
        cmd2.return_value = {
            "id": "69",
            "name": "migrate_tesla",
            "master_cluster_id": "0000020420603B5C",
            "master_cluster_name": "Cluster_9.71.42.119",
            "master_vdisk_id": "69",
            "master_vdisk_name": "tesla",
            "aux_cluster_id": "0000010022206192",
            "aux_cluster_name": "Cluster_9.71.42.198",
            "aux_vdisk_id": "77",
            "aux_vdisk_name": "tesla_target",
            "primary": "aux",
            "consistency_group_id": "",
            "consistency_group_name": "",
            "state": "consistent_synchronized",
            "bg_copy_priority": "50",
            "progress": "",
            "freeze_time": "",
            "status": "online",
            "sync": "",
            "copy_type": "",
            "cycling_mode": "",
            "cycle_period_seconds": "300",
            "master_change_vdisk_id": "",
            "master_change_vdisk_name": "",
            "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "",
            "previous_primary": "",
            "channel": "none"
        }
        with pytest.raises(AnsibleFailJson) as exc:
            m = IBMSVCMigrate()
            m.source_vol_relationship("tesla")
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_existing_rc(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = None
        m = IBMSVCMigrate()
        m.existing_rc()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_verify_existing_rel(self, auth):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        argument = {
            "id": "69",
            "name": "migrate_tesla",
            "master_cluster_id": "0000020420603B5C",
            "master_cluster_name": "Cluster_9.71.42.119",
            "master_vdisk_id": "69",
            "master_vdisk_name": "tesla",
            "aux_cluster_id": "0000010022206192",
            "aux_cluster_name": "Cluster_9.71.42.198",
            "aux_vdisk_id": "77",
            "aux_vdisk_name": "tesla_target",
            "primary": "aux",
            "consistency_group_id": "",
            "consistency_group_name": "",
            "state": "consistent_synchronized",
            "bg_copy_priority": "50",
            "progress": "",
            "freeze_time": "",
            "status": "online",
            "sync": "",
            "copy_type": "migration",
            "cycling_mode": "",
            "cycle_period_seconds": "300",
            "master_change_vdisk_id": "",
            "master_change_vdisk_name": "",
            "aux_change_vdisk_id": "",
            "aux_change_vdisk_name": "",
            "previous_primary": "",
            "channel": "none"
        }
        m = IBMSVCMigrate()
        m.verify_existing_rel(argument)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_relationship(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = ''
        m = IBMSVCMigrate()
        m.start_relationship()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_switch(self, auth, cmd1):
        set_module_args({
            "source_volume": "tesla",
            "target_volume": "tesla_target",
            "clustername": "9.71.42.119",
            "remote_cluster": "Cluster_9.71.42.198",
            "username": "superuser",
            "password": "passw0rd",
            "state": "initiate",
            "replicate_hosts": True,
            "remote_username": "superuser",
            "remote_password": "passw0rd",
            "relationship_name": "migrate_tesla",
            "remote_pool": "site2pool1"
        })
        cmd1.return_value = ''
        m = IBMSVCMigrate()
        m.switch()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete(self, auth, cmd1):
        set_module_args({
            "clustername": "9.71.42.119",
            "username": "superuser",
            "password": "passw0rd",
            "state": "cleanup",
            "source_volume": "tesla"
        })
        cmd1.return_value = ''
        m = IBMSVCMigrate()
        m.delete()


if __name__ == "__main__":
    unittest.main()
