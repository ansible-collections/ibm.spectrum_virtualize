# Copyright (C) 2020 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_hostcluster """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_hostcluster import IBMSVChostcluster


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


class TestIBMSVChostcluster(unittest.TestCase):
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
            IBMSVChostcluster()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_hostcluster(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
        })
        hostcluster_ret = [{"id": "1", "name": "ansible_hostcluster", "port_count": "1",
                            "mapping_count": "4", "status": "offline", "host_count": "1",
                            "protocol": "nvme", "owner_id": "",
                            "owner_name": ""}]
        svc_obj_info_mock.return_value = hostcluster_ret
        host = IBMSVChostcluster().get_existing_hostcluster()
        self.assertEqual('ansible_hostcluster', host['name'])
        self.assertEqual('1', host['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_hostcluster_create_get_existing_hostcluster_called(self, svc_authorize_mock,
                                                                get_existing_hostcluster_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
        })
        hostcluster_created = IBMSVChostcluster()
        with pytest.raises(AnsibleExitJson) as exc:
            hostcluster_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_but_hostcluster_exist(self, svc_authorize_mock,
                                                      get_existing_hostcluster_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'hostcluster0',
        })
        hostcluster_ret = {
            "id": "0",
            "name": "hostcluster0",
            "status": "online",
            "host_count": "1",
            "mapping_count": "0",
            "port_count": "1",
            "protocol": "scsi",
            "owner_id": "0",
            "owner_name": "group5"
        }
        get_existing_hostcluster_mock.return_value = hostcluster_ret
        hostcluster_created = IBMSVChostcluster()
        with pytest.raises(AnsibleExitJson) as exc:
            hostcluster_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.hostcluster_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_successfully(self, svc_authorize_mock,
                                             hostcluster_create_mock,
                                             get_existing_hostcluster_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster'
        })
        host = {u'message': u'Host cluster, id [14], '
                            u'successfully created', u'id': u'14'}
        hostcluster_create_mock.return_value = host
        get_existing_hostcluster_mock.return_value = []
        hostcluster_created = IBMSVChostcluster()
        with pytest.raises(AnsibleExitJson) as exc:
            hostcluster_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_failed_since_missed_required_param(
            self, svc_authorize_mock, get_existing_hostcluster_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster'
        })
        get_existing_hostcluster_mock.return_value = []
        hostcluster_created = IBMSVChostcluster()
        with pytest.raises(AnsibleFailJson) as exc:
            hostcluster_created.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_hostcluster_but_hostcluster_not_exist(self, svc_authorize_mock,
                                                          get_existing_hostcluster_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
        })
        get_existing_hostcluster_mock.return_value = []
        hostcluster_deleted = IBMSVChostcluster()
        with pytest.raises(AnsibleExitJson) as exc:
            hostcluster_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.hostcluster_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_hostcluster_successfully(self, svc_authorize_mock,
                                             hostcluster_delete_mock,
                                             get_existing_hostcluster_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
        })
        hostcluster_ret = [{"id": "1", "name": "ansible_hostcluster", "port_count": "1",
                            "mapping_count": "4", "status": "offline", "host_count": "1",
                            "protocol": "nvme", "owner_id": "",
                            "owner_name": ""}]
        get_existing_hostcluster_mock.return_value = hostcluster_ret
        hostcluster_deleted = IBMSVChostcluster()
        with pytest.raises(AnsibleExitJson) as exc:
            hostcluster_deleted.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_hostcluster_update(self, auth, cmd1):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'ownershipgroup': 'new'
        })
        modify = [
            'ownershipgroup'
        ]
        cmd1.return_value = None
        h = IBMSVChostcluster()
        h.hostcluster_update(modify)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_to_validate_update(self, auth, cmd1, cmd2):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'hostcluster0',
            'ownershipgroup': 'group1'
        })
        cmd1.return_value = {
            "id": "0",
            "name": "hostcluster0",
            "status": "online",
            "host_count": "1",
            "mapping_count": "0",
            "port_count": "1",
            "protocol": "scsi",
            "owner_id": "0",
            "owner_name": "group5"
        }
        cmd2.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            h = IBMSVChostcluster()
            h.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_to_validate_noownershipgroup(self, auth, cmd1, cmd2):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'hostcluster0',
            'noownershipgroup': True
        })
        cmd1.return_value = {
            "id": "0",
            "name": "hostcluster0",
            "status": "online",
            "host_count": "1",
            "mapping_count": "0",
            "port_count": "1",
            "protocol": "scsi",
            "owner_id": "0",
            "owner_name": "group5"
        }
        cmd2.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            h = IBMSVChostcluster()
            h.apply()
        self.assertTrue(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
