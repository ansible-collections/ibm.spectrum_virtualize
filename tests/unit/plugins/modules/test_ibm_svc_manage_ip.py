# Copyright (C) 2022 IBM CORPORATION
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
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_ip import IBMSVCIp


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
            IBMSVCIp()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        ip = IBMSVCIp()
        data = ip.basic_checks()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_ip_info(self, mock_svc_authorize, soim):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 'portset0',
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        soim.return_value = [
            {
                "id": "0",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "0",
                "portset_name": "portset0",
                "IP_address": "10.0.1.1",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "1",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "1",
                "portset_name": "portset1",
                "IP_address": "10.0.1.2",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "2",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "2",
                "portset_name": "portset2",
                "IP_address": "10.0.1.3",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "3",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "3",
                "portset_name": "portset3",
                "IP_address": "10.0.1.4",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "4",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "4",
                "portset_name": "Portset4",
                "IP_address": "10.0.1.5",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            }
        ]
        ip = IBMSVCIp()
        data = ip.get_ip_info()
        self.assertEqual(data[0]["IP_address"], "10.0.1.1")

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_ip(self, mock_svc_authorize, srcm):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        srcm.return_value = {
            'id': '0',
            'message': 'IP Address, id [0], successfully created'
        }
        ip = IBMSVCIp()
        data = ip.create_ip()
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_ip(self, mock_svc_authorize, srcm):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'absent'
        })
        srcm.return_value = None
        ip = IBMSVCIp()
        data = ip.remove_ip(0)
        self.assertEqual(data, None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_when_state_absent(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_when_node_absent(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_when_port_absent(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_when_portset_absent(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_when_ip_missing(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_node_missing(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_port_missing(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'portset': 0,
            'ip_address': '10.0.1.1',
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_portset_missing(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'ip_address': '10.0.1.1',
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_ip_missing(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_subnet_present(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_gateway_present(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'gateway': '10.10.10.10',
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_vlan_present(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'vlan': 1,
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_when_shareip_present(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'shareip': True,
            'state': 'absent'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_creation(self, mock_svc_authorize, soi, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        })
        soi.return_value = []
        src.return_value = {
            'id': '0',
            'message': 'IP Address, id [0], successfully created'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertEquall(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_deletion(self, mock_svc_authorize, soi, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'state': 'absent'
        })
        soi.return_value = [
            {
                "id": "0",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "0",
                "portset_name": "portset0",
                "IP_address": "10.0.1.1",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "1",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "1",
                "portset_name": "portset1",
                "IP_address": "10.0.1.2",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "2",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "2",
                "portset_name": "portset2",
                "IP_address": "10.0.1.3",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "3",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "3",
                "portset_name": "portset3",
                "IP_address": "10.0.1.4",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "4",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "4",
                "portset_name": "Portset4",
                "IP_address": "10.0.1.5",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            }
        ]
        src.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertEqual(exc.value.args[0]['changed'], True)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_deletion_when_multiple_IP_detected(self, mock_svc_authorize, soi):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'absent'
        })
        soi.return_value = [
            {
                "id": "0",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "0",
                "portset_name": "portset0",
                "IP_address": "10.0.1.1",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "1",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "0",
                "portset_name": "portset0",
                "IP_address": "10.0.1.1",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "2",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "2",
                "portset_name": "portset2",
                "IP_address": "10.0.1.3",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "3",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "3",
                "portset_name": "portset3",
                "IP_address": "10.0.1.4",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            },
            {
                "id": "4",
                "node_id": "1",
                "node_name": "node1",
                "port_id": "1",
                "portset_id": "4",
                "portset_name": "Portset4",
                "IP_address": "10.0.1.5",
                "prefix": "20",
                "vlan": "",
                "gateway": "",
                "owner_id": "",
                "owner_name": ""
            }
        ]
        with pytest.raises(AnsibleFailJson) as exc:
            ip = IBMSVCIp()
            ip.apply()
            self.assertEqual(exc.value.args[0]['failed'], True)


if __name__ == '__main__':
    unittest.main()
