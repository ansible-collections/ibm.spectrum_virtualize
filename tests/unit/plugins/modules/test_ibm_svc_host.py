# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#            Sudheesh Reddy Satti<Sudheesh.Reddy.Satti@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_host """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_host import IBMSVChost


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


class TestIBMSVChost(unittest.TestCase):
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
        self.existing_fcwwpn = []

    def set_default_args(self):
        return dict({
            'name': 'test',
            'state': 'present'
        })

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVChost()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_host(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "scsi", "owner_id": "",
                     "owner_name": ""}]
        svc_obj_info_mock.return_value = host_ret
        host = IBMSVChost().get_existing_host('ansible_host')
        self.assertEqual('ansible_host', host['name'])
        self.assertEqual('1', host['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_create_get_existing_host_called(self, svc_authorize_mock,
                                                  get_existing_host_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
        })
        get_existing_host_mock.return_value = [1]
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_but_host_existed(self, svc_authorize_mock,
                                          host_probe_mock,
                                          get_existing_host_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "scsi", "owner_id": "",
                     "owner_name": ""}]
        get_existing_host_mock.return_value = host_ret
        host_probe_mock.return_value = []
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_successfully(self, svc_authorize_mock,
                                      host_create_mock,
                                      get_existing_host_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'fcwwpn': '100000109B570216'
        })
        host = {u'message': u'Host, id [14], '
                            u'successfully created', u'id': u'14'}
        host_create_mock.return_value = host
        get_existing_host_mock.return_value = []
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_failed_since_missed_required_param(
            self, svc_authorize_mock, get_existing_host_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
        get_existing_host_mock.return_value = []
        host_created = IBMSVChost()
        with pytest.raises(AnsibleFailJson) as exc:
            host_created.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_host_but_host_not_existed(self, svc_authorize_mock,
                                              get_existing_host_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
        get_existing_host_mock.return_value = []
        host_deleted = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_host_successfully(self, svc_authorize_mock,
                                      host_delete_mock,
                                      get_existing_host_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "scsi", "owner_id": "",
                     "owner_name": ""}]
        get_existing_host_mock.return_value = host_ret
        host_deleted = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_deleted.apply()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_fcwwpn_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcwwpn_update_when_existing_absent(self, svc_authorize_mock, get_existing_host_mock, host_fcwwpn_update_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570262',
            'protocol': 'scsi',
            'type': 'generic'
        })
        lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                       'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                       'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                       'protocol': 'scsi', 'nodes': [{'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                                                     {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                                                     {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}]}
        get_existing_host_mock.return_value = lshost_data
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_fcwwpn_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcwwpn_update_when_new_added(self, svc_authorize_mock, get_existing_host_mock, host_fcwwpn_update_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570260:1000001AA0570261:1000001AA0570262:1000001AA0570264',
            'protocol': 'scsi',
            'type': 'generic'
        })
        lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                       'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                       'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                       'protocol': 'scsi', 'nodes': [{'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                                                     {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                                                     {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}]}
        get_existing_host_mock.return_value = lshost_data
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_fcwwpn_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcwwpn_update_when_existing_removes_and_new_added(self, svc_authorize_mock, get_existing_host_mock, host_fcwwpn_update_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570264:1000001AA0570265:1000001AA0570266',
            'protocol': 'scsi',
            'type': 'generic'
        })
        lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                       'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                       'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                       'protocol': 'scsi', 'nodes': [{'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                                                     {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                                                     {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}]}
        get_existing_host_mock.return_value = lshost_data
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_fcwwpn_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570264:1000001AA0570265:1000001AA0570266',
            'protocol': 'scsi',
            'type': 'generic'
        })
        obj = IBMSVChost()
        obj.existing_fcwwpn = ['1000001AA0570262', '1000001AA0570263', '1000001AA0570264']
        obj.input_fcwwpn = ['1000001AA0570264', '1000001AA0570265', '1000001AA0570266']
        self.assertEqual(obj.host_fcwwpn_update(), None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_site_update(self, svc_authorize_mock, svc_obj_info_mock, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570260:1000001AA0570261:1000001AA0570262',
            'protocol': 'scsi',
            'type': 'generic',
            'site': 'site1'
        })
        svc_obj_info_mock.return_value = {
            'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
            'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
            'site_id': '', 'site_name': 'site2', 'host_cluster_id': '', 'host_cluster_name': '',
            'protocol': 'scsi', 'nodes': [
                {'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}
            ]
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVChost()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_hostcluster_update(self, svc_authorize_mock, svc_obj_info_mock, src):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'protocol': 'scsi',
            'type': 'generic',
            'site': 'site1',
            'hostcluster': 'hostcluster0'
        })
        svc_obj_info_mock.return_value = {
            'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
            'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
            'site_id': '', 'site_name': 'site2', 'host_cluster_id': '1', 'host_cluster_name': 'hostcluster0'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVChost()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_duplicate_checker(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570260:1000001AA0570260:1000001AA0570260',
            'protocol': 'scsi',
            'type': 'generic',
            'site': 'site1'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVChost()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_rename(self, mock_auth, mock_old, mock_cmd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'old_name': 'name',
            'name': 'new_name',
            'state': 'present',
        })
        mock_old.return_value = [
            {
                "id": "1", "name": "ansible_host", "port_count": "1",
                "iogrp_count": "4", "status": "offline",
                "site_id": "", "site_name": "",
                "host_cluster_id": "", "host_cluster_name": "",
                "protocol": "scsi", "owner_id": "",
                "owner_name": ""
            }
        ]
        arg_data = []
        mock_cmd.return_value = None
        v = IBMSVChost()
        data = v.host_rename(arg_data)
        self.assertEqual(data, 'Host [name] has been successfully rename to [new_name].')

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_rename_failure_for_unsupported_param(self, am):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'old_name': 'name',
            'name': 'new_name',
            'state': 'present',
            'fcwwpn': True
        })
        with pytest.raises(AnsibleFailJson) as exc:
            v = IBMSVChost()
            v.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_iscsiname_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_iscsiname_update_when_existing_absent(self, svc_authorize_mock, get_existing_host_mock, host_iscsinmae_update_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a',
            'protocol': 'scsi',
            'type': 'generic'
        })
        lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                       'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                       'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                       'protocol': 'scsi', 'nodes': [{'iscsi_name': 'iqn.1994-05.com.redhat:2e358e438b8a', 'node_logged_in_count': '0', 'state': 'offline'},
                                                     {'iscsi_name': 'iqn.localhost.hostid.7f000001', 'node_logged_in_count': '0', 'state': 'offline'},
                                                     {'iscsi_name': 'iqn.localhost.hostid.7f000002', 'node_logged_in_count': '0', 'state': 'offline'}]}
        get_existing_host_mock.return_value = lshost_data
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_iscsiname_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_iscsiname_update_when_new_added(self, svc_authorize_mock, get_existing_host_mock, host_iscsiname_update_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a,iqn.localhost.hostid.7f000001,iqn.localhost.hostid.7f000002',
            'protocol': 'scsi',
            'type': 'generic'
        })
        lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                       'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                       'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                       'protocol': 'scsi', 'nodes': [{'iscsi_name': 'iqn.1994-05.com.redhat:2e358e438b8a', 'node_logged_in_count': '0', 'state': 'offline'},
                                                     {'iscsi_name': 'iqn.localhost.hostid.7f000001', 'node_logged_in_count': '0', 'state': 'offline'}]}
        get_existing_host_mock.return_value = lshost_data
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_iscsiname_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a,iqn.localhost.hostid.7f000002',
            'protocol': 'scsi',
            'type': 'generic'
        })
        obj = IBMSVChost()
        obj.existing_iscsiname = ['iqn.1994-05.com.redhat:2e358e438b8a', 'iqn.localhost.hostid.7f000001']
        obj.input_iscsiname = ['iqn.1994-05.com.redhat:2e358e438b8a', 'iqn.localhost.hostid.7f000002']
        self.assertEqual(obj.host_iscsiname_update(), None)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rdmanvme_nqn_update_when_new_added(self, svc_authorize_mock, host_create_mock, get_existing_host_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'nqn': 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78434,nqn.2014-08.com.example:nvme:nvm-example-sn-d78433',
            'protocol': 'rdmanvme',
            'portset': 'portset0',
            'type': 'generic'
        })

        host = {u'message': u'Host, id [14], '
                            u'successfully created', u'id': u'14'}
        host_create_mock.return_value = host
        get_existing_host_mock.return_value = []
        host_created = IBMSVChost()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_nqn_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'nqn': 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78434,nqn.2014-08.com.example:nvme:nvm-example-sn-d78431',
            'protocol': 'rdmanvme',
            'type': 'generic'
        })
        obj = IBMSVChost()
        obj.existing_nqn = ['nqn.2014-08.com.example:nvme:nvm-example-sn-d78434', 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78433']
        obj.input_nqn = ['nqn.2014-08.com.example:nvme:nvm-example-sn-d78434', 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78431']
        self.assertEqual(obj.host_nqn_update(), None)


if __name__ == '__main__':
    unittest.main()
