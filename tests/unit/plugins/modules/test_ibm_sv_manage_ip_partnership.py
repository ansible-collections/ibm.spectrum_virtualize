# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_manage_ip_partnership """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_manage_ip_partnership import IBMSVCIPPartnership


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


class TestIBMSVCIPPartnership(unittest.TestCase):
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
            IBMSVCIPPartnership()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, mock_auth):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        ip = IBMSVCIPPartnership()
        data = ip.basic_checks()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_state_missing(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIPPartnership()
            ip.apply()
            print('Info: %s' % exc)
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_remote_clusterip_missing(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIPPartnership()
            ip.apply()
            print('Info: %s' % exc)
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_ip(self, mock_auth, mock_soi):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        mock_soi.return_value = {
            "id": "123456789",
            "name": "Cluster_x.x.x.x",
            "location": "local",
            "partnership": "",
            "total_mdisk_capacity": "1.7TB",
            "space_in_mdisk_grps": "1.7TB",
            "space_allocated_to_vdisks": "20.58GB",
            "total_free_space": "1.7TB",
            "total_vdiskcopy_capacity": "20.00GB",
            "total_used_capacity": "19.02GB",
            "total_overallocation": "1",
            "total_vdisk_capacity": "20.00GB",
            "total_allocated_extent_capacity": "21.00GB",
            "statistics_status": "on",
            "statistics_frequency": "15",
            "cluster_locale": "",
            "time_zone": "",
            "code_level": "8.5.0.2 (build 157.12.2204111405000)",
            "console_IP": "x.x.x.x:443",
            "id_alias": "112233",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "gm_max_host_delay": "5",
            "email_reply": "",
            "email_contact": "",
            "email_contact_primary": "",
            "email_contact_alternate": "",
            "email_contact_location": "",
            "email_contact2": "",
            "email_contact2_primary": "",
            "email_contact2_alternate": "",
            "email_state": "stopped",
            "inventory_mail_interval": "0",
            "cluster_ntp_IP_address": "",
            "cluster_isns_IP_address": "",
            "iscsi_auth_method": "none",
            "iscsi_chap_secret": "",
            "auth_service_configured": "no",
            "auth_service_enabled": "no",
            "auth_service_url": "",
            "auth_service_user_name": "",
            "auth_service_pwd_set": "no",
            "auth_service_cert_set": "no",
            "auth_service_type": "ldap",
            "relationship_bandwidth_limit": "25",
            "tiers": [
                {
                    "tier": "tier_scm",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier0_flash",
                    "tier_capacity": "1.74TB",
                    "tier_free_capacity": "1.72TB"
                },
                {
                    "tier": "tier1_flash",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_enterprise",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_nearline",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                }
            ],
            "easy_tier_acceleration": "off",
            "has_nas_key": "no",
            "layer": "storage",
            "rc_buffer_size": "256",
            "compression_active": "no",
            "compression_virtual_capacity": "0.00MB",
            "compression_compressed_capacity": "0.00MB",
            "compression_uncompressed_capacity": "0.00MB",
            "cache_prefetch": "on",
            "email_organization": "",
            "email_machine_address": "",
            "email_machine_city": "",
            "email_machine_state": "XX",
            "email_machine_zip": "",
            "email_machine_country": "",
            "total_drive_raw_capacity": "0",
            "compression_destage_mode": "off",
            "local_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "partner_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "high_temp_mode": "off",
            "topology": "standard",
            "topology_status": "",
            "rc_auth_method": "none",
            "vdisk_protection_time": "15",
            "vdisk_protection_enabled": "yes",
            "product_name": "IBM FlashSystem 9200",
            "odx": "off",
            "max_replication_delay": "0",
            "partnership_exclusion_threshold": "315",
            "gen1_compatibility_mode_enabled": "no",
            "ibm_customer": "",
            "ibm_component": "",
            "ibm_country": "",
            "tier_scm_compressed_data_used": "0.00MB",
            "tier0_flash_compressed_data_used": "0.00MB",
            "tier1_flash_compressed_data_used": "0.00MB",
            "tier_enterprise_compressed_data_used": "0.00MB",
            "tier_nearline_compressed_data_used": "0.00MB",
            "total_reclaimable_capacity": "0.00MB",
            "physical_capacity": "1.74TB",
            "physical_free_capacity": "1.72TB",
            "used_capacity_before_reduction": "0.00MB",
            "used_capacity_after_reduction": "1.02GB",
            "overhead_capacity": "18.00GB",
            "deduplication_capacity_saving": "0.00MB",
            "enhanced_callhome": "on",
            "censor_callhome": "off",
            "host_unmap": "on",
            "backend_unmap": "on",
            "quorum_mode": "standard",
            "quorum_site_id": "",
            "quorum_site_name": "",
            "quorum_lease": "short",
            "automatic_vdisk_analysis_enabled": "on",
            "callhome_accepted_usage": "no",
            "safeguarded_copy_suspended": "no"
        }
        restapi_local = IBMSVCRestApi(
            self.mock_module_helper,
            '1.2.3.4',
            'domain.ibm.com',
            'username',
            'password',
            False,
            'test.log',
            ''
        )
        ip = IBMSVCIPPartnership()
        data = ip.get_ip(restapi_local)
        self.assertEqual(data, 'x.x.x.x')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_get_ip(self, mock_auth, mock_soi):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        mock_soi.return_value = None
        restapi_local = IBMSVCRestApi(
            self.mock_module_helper,
            '1.2.3.4',
            'domain.ibm.com',
            'username',
            'password',
            False,
            'test.log',
            ''
        )
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIPPartnership()
            ip.get_ip(restapi_local)
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_all_partnership(self, mock_auth, mock_soi):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        mock_soi.return_value = [
            {
                "id": "1234",
                "name": "Cluster_x.x.x.x",
                "location": "local",
                "partnership": "",
                "type": "",
                "cluster_ip": "",
                "event_log_sequence": "",
                "link1": "",
                "link2": "",
                "link1_ip_id": "",
                "link2_ip_id": ""
            }
        ]
        restapi_local = IBMSVCRestApi(
            self.mock_module_helper,
            '1.2.3.4',
            'domain.ibm.com',
            'username',
            'password',
            False,
            'test.log',
            ''
        )
        ip = IBMSVCIPPartnership()
        data = ip.get_all_partnership(restapi_local)
        self.assertEqual(data[0]['name'], 'Cluster_x.x.x.x')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_filter_partnership(self, mock_auth):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        data = [
            {
                "id": "1234",
                "name": "Cluster_x.x.x.x",
                "location": "local",
                "partnership": "",
                "type": "",
                "cluster_ip": "",
                "event_log_sequence": "",
                "link1": "",
                "link2": "",
                "link1_ip_id": "",
                "link2_ip_id": ""
            },
            {
                "id": "12345",
                "name": "Cluster_z.z.z.z",
                "location": "remote",
                "partnership": "",
                "type": "",
                "cluster_ip": "z.z.z.z",
                "event_log_sequence": "",
                "link1": "",
                "link2": "",
                "link1_ip_id": "",
                "link2_ip_id": ""
            }
        ]
        restapi_local = IBMSVCRestApi(
            self.mock_module_helper,
            '1.2.3.4',
            'domain.ibm.com',
            'username',
            'password',
            False,
            'test.log',
            ''
        )
        ip = IBMSVCIPPartnership()
        data = ip.filter_partnership(data, "z.z.z.z")
        self.assertEqual(len(data), 1)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_partnership_detail(self, mock_auth, mock_soi):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        mock_soi.return_value = {
            "id": "1234",
            "name": "test_Cluster_x.x.x.x",
            "location": "remote",
            "partnership": "not_present",
            "code_level": "8.5.1.0 (build 159.1.2203020902000)",
            "console_IP": "x.x.x.x:443",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "relationship_bandwidth_limit": "25",
            "gm_max_host_delay": "5",
            "type": "ipv4",
            "cluster_ip": "x.x.x.x",
            "chap_secret": "",
            "event_log_sequence": "",
            "link_bandwidth_mbits": "100",
            "background_copy_rate": "50",
            "max_replication_delay": "0",
            "compressed": "yes",
            "link1": "portset1",
            "link2": "",
            "link1_ip_id": "1",
            "link2_ip_id": "",
            "secured": "no"
        }
        restapi_local = IBMSVCRestApi(
            self.mock_module_helper,
            '1.2.3.4',
            'domain.ibm.com',
            'username',
            'password',
            False,
            'test.log',
            ''
        )
        ip = IBMSVCIPPartnership()
        data = ip.get_partnership_detail(restapi_local, '1234')
        self.assertEqual(data['id'], '1234')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_partnership(self, mock_auth, mock_src):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        mock_src.return_value = ''
        ip = IBMSVCIPPartnership()
        data = ip.create_partnership('local', 'y.y.y.y')
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_partnership(self, mock_auth, mock_src):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'absent',
            'remote_clusterip': 'y.y.y.y'
        })
        mock_src.return_value = ''
        ip = IBMSVCIPPartnership()
        data = ip.remove_partnership('local', 'y.y.y.y')
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_probe_partnership(self, mock_auth):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset1',
            'remote_link1': 'portset1'
        })
        local_data = {
            "id": "1234",
            "name": "test_Cluster_x.x.x.x",
            "location": "remote",
            "partnership": "not_present",
            "code_level": "8.5.1.0 (build 159.1.2203020902000)",
            "console_IP": "x.x.x.x:443",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "relationship_bandwidth_limit": "25",
            "gm_max_host_delay": "5",
            "type": "ipv4",
            "cluster_ip": "x.x.x.x",
            "chap_secret": "",
            "event_log_sequence": "",
            "link_bandwidth_mbits": "100",
            "background_copy_rate": "50",
            "max_replication_delay": "0",
            "compressed": "no",
            "link1": "portset1",
            "link2": "",
            "link1_ip_id": "1",
            "link2_ip_id": "",
            "secured": "no"
        }
        remote_data = {
            "id": "12345",
            "name": "test_Cluster_x.x.x.x",
            "location": "remote",
            "partnership": "not_present",
            "code_level": "8.5.1.0 (build 159.1.2203020902000)",
            "console_IP": "x.x.x.x:443",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "relationship_bandwidth_limit": "25",
            "gm_max_host_delay": "5",
            "type": "ipv4",
            "cluster_ip": "x.x.x.x",
            "chap_secret": "",
            "event_log_sequence": "",
            "link_bandwidth_mbits": "100",
            "background_copy_rate": "50",
            "max_replication_delay": "0",
            "compressed": "no",
            "link1": "portset1",
            "link2": "",
            "link1_ip_id": "1",
            "link2_ip_id": "",
            "secured": "no"
        }
        ip = IBMSVCIPPartnership()
        local_modify, remote_modify = ip.probe_partnership(local_data, remote_data)
        self.assertEqual(local_modify['compressed'], 'yes')
        self.assertEqual(remote_modify['compressed'], 'yes')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_partnership(self, mock_auth, mock_src):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        restapi_local = IBMSVCRestApi(
            self.mock_module_helper,
            '1.2.3.4',
            'domain.ibm.com',
            'username',
            'password',
            False,
            'test.log',
            ''
        )
        mock_src.return_value = ''
        ip = IBMSVCIPPartnership()
        data = ip.start_partnership(restapi_local, '0000020428A03B90')
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_partnership(self, mock_auth, mock_src):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        restapi_local = IBMSVCRestApi(
            self.mock_module_helper,
            '1.2.3.4',
            'domain.ibm.com',
            'username',
            'password',
            False,
            'test.log',
            ''
        )
        mock_src.return_value = ''
        ip = IBMSVCIPPartnership()
        data = ip.stop_partnership(restapi_local, '1234')
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_partnership(self, mock_auth, mock_src):
        set_module_args({
            'clustername': 'x.x.x.x',
            'domain': '',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'y.y.y.y',
            'remote_domain': '',
            'remote_username': 'remote username',
            'remote_password': 'remote_password',
            'log_path': 'playbook.log',
            'state': 'present',
            'remote_clusterip': 'y.y.y.y',
            'type': 'ipv4',
            'linkbandwidthmbits': 100,
            'backgroundcopyrate': 50,
            'compressed': 'yes',
            'link1': 'portset2',
            'remote_link1': 'portset1'
        })
        mock_src.return_value = ''
        modify_local = {
            'linkbandwidthmbits': '101',
            'backgroundcopyrate': '52'
        }
        ip = IBMSVCIPPartnership()
        data = ip.update_partnership('local', '1234', modify_local)
        self.assertEqual(data, None)


if __name__ == '__main__':
    unittest.main()
