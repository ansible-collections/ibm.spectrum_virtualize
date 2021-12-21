# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_callhome """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_callhome import IBMSVCCallhome


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


class TestIBMSVCCallhome(unittest.TestCase):
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
            'state': 'enabled'
        })

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVCCallhome()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        ch = IBMSVCCallhome()
        data = ch.basic_checks()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_system_data(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_soi.return_value = {
            "id": "0000010023806192",
            "name": "Cluster_9.71.42.198",
            "location": "local",
            "partnership": "",
            "total_mdisk_capacity": "3.6TB",
            "space_in_mdisk_grps": "3.6TB",
            "space_allocated_to_vdisks": "449.70GB",
            "total_free_space": "3.2TB",
            "total_vdiskcopy_capacity": "993.00GB",
            "total_used_capacity": "435.67GB",
            "total_overallocation": "26",
            "total_vdisk_capacity": "993.00GB",
            "total_allocated_extent_capacity": "455.00GB",
            "statistics_status": "on",
            "statistics_frequency": "15",
            "cluster_locale": "en_US",
            "time_zone": "503 SystemV/PST8",
            "code_level": "8.4.2.0 (build 154.20.2109031944000)",
            "console_IP": "9.71.42.198:443",
            "id_alias": "0000010023806192",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "gm_max_host_delay": "5",
            "email_reply": "sreshtant.bohidar@ibm.com",
            "email_contact": "Sreshtant Bohidar",
            "email_contact_primary": "9439394132",
            "email_contact_alternate": "9439394132",
            "email_contact_location": "floor 2",
            "email_contact2": "",
            "email_contact2_primary": "",
            "email_contact2_alternate": "",
            "email_state": "stopped",
            "inventory_mail_interval": "1",
            "cluster_ntp_IP_address": "2.2.2.2",
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
                    "tier_capacity": "1.78TB",
                    "tier_free_capacity": "1.47TB"
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
                    "tier_capacity": "1.82TB",
                    "tier_free_capacity": "1.68TB"
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
            "email_organization": "IBM",
            "email_machine_address": "Street 39",
            "email_machine_city": "New York",
            "email_machine_state": "CAN",
            "email_machine_zip": "123456",
            "email_machine_country": "US",
            "total_drive_raw_capacity": "10.10TB",
            "compression_destage_mode": "off",
            "local_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "partner_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "high_temp_mode": "off",
            "topology": "hyperswap",
            "topology_status": "dual_site",
            "rc_auth_method": "none",
            "vdisk_protection_time": "15",
            "vdisk_protection_enabled": "no",
            "product_name": "IBM Storwize V7000",
            "odx": "off",
            "max_replication_delay": "0",
            "partnership_exclusion_threshold": "315",
            "gen1_compatibility_mode_enabled": "no",
            "ibm_customer": "262727272",
            "ibm_component": "",
            "ibm_country": "383",
            "tier_scm_compressed_data_used": "0.00MB",
            "tier0_flash_compressed_data_used": "0.00MB",
            "tier1_flash_compressed_data_used": "0.00MB",
            "tier_enterprise_compressed_data_used": "0.00MB",
            "tier_nearline_compressed_data_used": "0.00MB",
            "total_reclaimable_capacity": "380.13MB",
            "physical_capacity": "3.60TB",
            "physical_free_capacity": "3.15TB",
            "used_capacity_before_reduction": "361.81MB",
            "used_capacity_after_reduction": "14.27GB",
            "overhead_capacity": "34.00GB",
            "deduplication_capacity_saving": "0.00MB",
            "enhanced_callhome": "on",
            "censor_callhome": "on",
            "host_unmap": "off",
            "backend_unmap": "on",
            "quorum_mode": "standard",
            "quorum_site_id": "",
            "quorum_site_name": "",
            "quorum_lease": "short",
            "automatic_vdisk_analysis_enabled": "on",
            "callhome_accepted_usage": "no",
            "safeguarded_copy_suspended": "no",
            'serverIP': '9.20.118.16',
            'serverPort': 25
        }
        ch = IBMSVCCallhome()
        data = ch.get_system_data()
        self.assertEqual(data['callhome_accepted_usage'], 'no')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_email_user_data(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_soi.return_value = [
            {
                "id": "0",
                "name": "emailuser0",
                "address": "callhome1@de.ibm.com",
                "user_type": "support",
                "error": "on",
                "warning": "off",
                "info": "off",
                "inventory": "on"
            },
            {
                "id": "1",
                "name": "emailuser1",
                "address": "test@domain.com",
                "user_type": "local",
                "error": "off",
                "warning": "off",
                "info": "off",
                "inventory": "off"
            }
        ]
        ch = IBMSVCCallhome()
        data = ch.get_existing_email_user_data()
        self.assertEqual(data['address'], 'test@domain.com')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_check_email_server_exists(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_soi.return_value = [
            {
                "id": "0",
                "name": "emailserver0",
                "IP_address": "9.20.118.16",
                "port": "25",
                "status": "active"
            }
        ]
        ch = IBMSVCCallhome()
        data = ch.check_email_server_exists()
        self.assertEqual(data, True)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_check_email_user_exists(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_soi.return_value = [
            {
                "id": "0",
                "name": "emailuser0",
                "address": "test@domain.com",
                "user_type": "support",
                "error": "on",
                "warning": "off",
                "info": "off",
                "inventory": "off"
            }
        ]
        ch = IBMSVCCallhome()
        data = ch.check_email_user_exists()
        self.assertEqual(data['id'], '0')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_email_server(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_src.return_value = {
            'id': '0',
            'message': 'Email Server id [0] successfully created'
        }
        ch = IBMSVCCallhome()
        data = ch.create_email_server()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_email_user(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_src.return_value = {
            'id': '0',
            'message': 'User, id [0], successfully created'
        }
        ch = IBMSVCCallhome()
        data = ch.create_email_user()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_enable_email_callhome(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.enable_email_callhome()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_disable_email_callhome(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'disabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.disable_email_callhome()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_email_data(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'disabled',
            'callhome_type': 'email',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25
        })
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.update_email_data()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_proxy(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'disabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'open_proxy'
        })
        mock_soi.return_value = {
            "enabled": "yes",
            "url": "http://h-proxy3.ssd.hursley.ibm.com",
            "port": "3128",
            "username": "",
            "password_set": "no",
            "certificate": "0 fields"
        }
        ch = IBMSVCCallhome()
        data = ch.get_existing_proxy()
        self.assertEqual(data['port'], '3128')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_proxy(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'no_proxy'
        })
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.remove_proxy()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_proxy(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'open_proxy'
        })
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.create_proxy()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_probe_proxy(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'open_proxy'
        })
        data = {
            "enabled": "yes",
            "url": "http://h-proxy3.ssd.hursley.ibm.com",
            "port": "3127",
            "username": "",
            "password_set": "no",
            "certificate": "0 fields"
        }
        ch = IBMSVCCallhome()
        data = ch.probe_proxy(data)
        self.assertEqual(data['port'], 3128)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_proxy(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'open_proxy'
        })
        data = {
            'port': 3128
        }
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.update_proxy(data)
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_cloud_callhome_data(self, mock_svc_authorize, mock_soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'disabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'open_proxy'
        })
        mock_soi.return_value = {
            "status": "disabled",
            "connection": "",
            "error_sequence_number": "",
            "last_success": "",
            "last_failure": ""
        }
        ch = IBMSVCCallhome()
        data = ch.get_existing_cloud_callhome_data()
        self.assertEqual(data['status'], 'disabled')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_enable_cloud_callhome(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'enabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'open_proxy'
        })
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.enable_cloud_callhome()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_disable_cloud_callhome(self, mock_svc_authorize, mock_src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'disabled',
            'callhome_type': 'cloud services',
            'company_name': 'company_name',
            'address': 'address',
            'city': 'city',
            'province': 'PRV',
            'postalcode': '123456',
            'country': 'US',
            'location': 'location',
            'contact_name': 'contact_name',
            'contact_email': 'test@domain.com',
            'phonenumber_primary': '1234567890',
            'serverIP': '9.20.118.16',
            'serverPort': 25,
            'proxy_url': 'http://h-proxy3.ssd.hursley.ibm.com',
            'proxy_port': 3128,
            'proxy_type': 'open_proxy'
        })
        mock_src.return_value = ''
        ch = IBMSVCCallhome()
        data = ch.disable_cloud_callhome()
        self.assertEqual(data, None)


if __name__ == '__main__':
    unittest.main()
