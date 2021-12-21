# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_initial_setup """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_initial_setup import IBMSVCInitialSetup


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


class TestIBMSVCInitialSetup(unittest.TestCase):
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

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.license_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_module_with_no_input_params(self,
                                         run_cmd_mock,
                                         system_info_mock,
                                         license_probe_mock,
                                         dns_info_mock,
                                         auth_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
        })

        license_probe_mock.return_value = []

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_fail_with_mutually_exclusive_param(self, auth_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'time': '101009142021',
            'ntpip': '9.9.9.9'
        })

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleFailJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_dns_validation_1(self, auth_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'dnsip': ['9.9.9.9']
        })

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleFailJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_dns_validation_2(self, auth_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'dnsip': ['9.9.9.9'],
            'dnsname': []
        })

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleFailJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.license_probe')
    def test_module_system_and_dns(self,
                                   license_probe_mock,
                                   auth_mock,
                                   system_info_mock,
                                   run_cmd_mock,
                                   dns_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'system_name': 'cluster_test_0',
            'time': '101009142021',
            'timezone': 200,
            'dnsname': ['test_dns'],
            'dnsip': ['1.1.1.1']
        })

        system_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "",
            "location": "local",
            "cluster_locale": "en_US",
            "time_zone": "200 Asia/Calcutta",
            "cluster_ntp_IP_address": "",
        }

        license_probe_mock.return_value = []

        dns_info_mock.return_value = [
            {
                "id": "0",
                "name": "h",
                "type": "ipv4",
                "IP_address": "9.20.136.11",
                "status": "active"
            },
            {
                "id": "1",
                "name": "i",
                "type": "ipv4",
                "IP_address": "9.20.136.25",
                "status": "active"
            }
        ]

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.license_probe')
    def test_with_already_existed_system_and_dns(
            self,
            license_probe_mock,
            auth_mock,
            system_info_mock,
            run_cmd_mock,
            dns_info_mock):

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'system_name': 'cluster_test_0',
            'ntpip': '9.9.9.9',
            'timezone': 200,
            'dnsname': ['test_dns'],
            'dnsip': ['1.1.1.1']
        })

        system_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "cluster_test_0",
            "location": "local",
            "cluster_locale": "en_US",
            "time_zone": "200 Asia/Calcutta",
            "cluster_ntp_IP_address": "9.9.9.9",
        }

        license_probe_mock.return_value = []

        dns_info_mock.return_value = [
            {
                "id": "0",
                "name": "test_dns",
                "type": "ipv4",
                "IP_address": "1.1.1.1",
                "status": "active"
            }
        ]

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.license_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_license_key_update(self,
                                       auth_mock,
                                       system_info_mock,
                                       run_cmd_mock,
                                       license_probe_mock,
                                       dns_info_mock):

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'license_key': ['0123-4567-89AB-CDEF']
        })

        license_probe_mock.return_value = []

        run_cmd_mock.return_value = [
            {
                "id": "0",
                "name": "encryption",
                "state": "inactive",
                "license_key": "",
                "trial_expiration_date": "",
                "serial_num": "",
                "mtm": ""
            }
        ]

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.license_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_with_existing_license_key_update(self,
                                              auth_mock,
                                              system_info_mock,
                                              run_cmd_mock,
                                              license_probe_mock,
                                              dns_info_mock):

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'license_key': ['0123-4567-89AB-CDEF']
        })

        license_probe_mock.return_value = []

        run_cmd_mock.return_value = [
            {
                "id": "0",
                "name": "encryption",
                "state": "inactive",
                "license_key": "0123-4567-89AB-CDEF",
                "trial_expiration_date": "",
                "serial_num": "",
                "mtm": ""
            }
        ]

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.license_probe')
    def test_module_empty_timezone(self,
                                   license_probe_mock,
                                   auth_mock,
                                   system_info_mock,
                                   run_cmd_mock,
                                   dns_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'system_name': 'cluster_test_0',
            'time': '101009142021',
            'timezone': 200,
        })

        system_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "",
            "location": "local",
            "cluster_locale": "en_US",
            "time_zone": "",
            "cluster_ntp_IP_address": "",
        }

        license_probe_mock.return_value = []

        dns_info_mock.return_value = []

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_license_update_storwize(self,
                                     auth_mock,
                                     system_info_mock,
                                     run_cmd_mock,
                                     dns_info_mock):

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 1,
            'compression': 4,
            'cloud': 1,
            'easytier': 1,
            'physical_flash': True,
            'encryption': True
        })

        system_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "cluster_test_0",
            "location": "local",
            "cluster_locale": "en_US",
            "time_zone": "200 Asia/Calcutta",
            "cluster_ntp_IP_address": "9.9.9.9",
            "product_name": "IBM Storwize V7000"
        }

        run_cmd_mock.return_value = {
            "license_flash": "0",
            "license_remote": "4",
            "license_virtualization": "0",
            "license_physical_disks": "0",
            "license_physical_flash": "off",
            "license_physical_remote": "off",
            "license_compression_capacity": "4",
            "license_compression_enclosures": "5",
            "license_easy_tier": "0",
            "license_cloud_enclosures": "0"
        }

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_existing_license_storwize(self,
                                              auth_mock,
                                              system_info_mock,
                                              run_cmd_mock,
                                              dns_info_mock):

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 0,
            'compression': 4,
            'cloud': 0,
            'easytier': 0,
            'physical_flash': "off",
            'encryption': True
        })

        system_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "cluster_test_0",
            "location": "local",
            "cluster_locale": "en_US",
            "time_zone": "200 Asia/Calcutta",
            "cluster_ntp_IP_address": "9.9.9.9",
            "product_name": "IBM Storwize V7000"
        }

        run_cmd_mock.return_value = {
            "license_flash": "0",
            "license_remote": "5",
            "license_virtualization": "1",
            "license_physical_disks": "0",
            "license_physical_flash": "off",
            "license_physical_remote": "off",
            "license_compression_capacity": "0",
            "license_compression_enclosures": "4",
            "license_easy_tier": "0",
            "license_cloud_enclosures": "0"
        }

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()

        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_license_update_with_SVC(self,
                                     auth_mock,
                                     system_info_mock,
                                     run_cmd_mock,
                                     dns_info_mock):

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 1,
            'compression': 4,
            'cloud': 1,
            'easytier': 1,
            'physical_flash': True,
            'encryption': True
        })

        system_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "cluster_test_0",
            "location": "local",
            "cluster_locale": "en_US",
            "time_zone": "200 Asia/Calcutta",
            "cluster_ntp_IP_address": "9.9.9.9",
            "product_name": "SVC"
        }

        run_cmd_mock.return_value = {
            "license_flash": "0",
            "license_remote": "4",
            "license_virtualization": "0",
            "license_physical_disks": "0",
            "license_physical_flash": "off",
            "license_physical_remote": "off",
            "license_compression_capacity": "0",
            "license_compression_enclosures": "4",
            "license_easy_tier": "0",
            "license_cloud_enclosures": "0"
        }

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()

        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_existing_dnsservers')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_license_update_existing_SVC(self,
                                         auth_mock,
                                         system_info_mock,
                                         run_cmd_mock,
                                         dns_info_mock):

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 1,
            'compression': 4,
            'cloud': 1,
            'easytier': 1,
            'physical_flash': "on",
            'encryption': True
        })

        system_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "cluster_test_0",
            "location": "local",
            "cluster_locale": "en_US",
            "time_zone": "200 Asia/Calcutta",
            "cluster_ntp_IP_address": "9.9.9.9",
            "product_name": "SVC"
        }

        run_cmd_mock.return_value = {
            "license_flash": "1",
            "license_remote": "5",
            "license_virtualization": "1",
            "license_physical_disks": "0",
            "license_physical_flash": "on",
            "license_physical_remote": "off",
            "license_compression_capacity": "4",
            "license_compression_enclosures": "5",
            "license_easy_tier": "1",
            "license_cloud_enclosures": "1"
        }

        svc_is = IBMSVCInitialSetup()
        with pytest.raises(AnsibleExitJson) as exc:
            svc_is.apply()

        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
