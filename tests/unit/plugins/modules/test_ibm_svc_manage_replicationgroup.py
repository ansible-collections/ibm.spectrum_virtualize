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
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_replicationgroup import IBMSVCRCCG


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


class TestIBMSVCRCCG(unittest.TestCase):
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
            IBMSVCRCCG()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_rccg(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
        })
        svc_obj_info_mock.return_value = {
            "id": "11",
            "name": "test_name",
            "master_cluster_id": "0000020321E04566",
            "master_cluster_name": "test_remotecluster",
            "aux_cluster_id": "0000020321E04566",
            "aux_cluster_name": "test_remotecluster",
            "primary": "",
            "state": "empty",
            "relationship_count": "0",
            "freeze_time": "",
            "status": "",
            "sync": "",
            "copy_type": "metro",
            "cycling_mode": "",
            "cycle_period_seconds": "0"
        }
        obj = IBMSVCRCCG()
        return_data = obj.get_existing_rccg()
        self.assertEqual('test_name', return_data['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rccg_probe(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'copytype': 'metro',
        })
        arg_data = {
            "id": "11",
            "name": "test_name",
            "master_cluster_id": "0000020321E04566",
            "master_cluster_name": "test_remotecluster",
            "aux_cluster_id": "0000020321E04566",
            "aux_cluster_name": "test_remotecluster",
            "primary": "",
            "state": "empty",
            "relationship_count": "0",
            "freeze_time": "",
            "status": "",
            "sync": "",
            "copy_type": "global",
            "cycling_mode": "",
            "cycle_period_seconds": "0"
        }
        obj = IBMSVCRCCG()
        return_data = obj.rccg_probe(arg_data)
        self.assertIn('metro', return_data[0])
        self.assertTrue(return_data[0]["metro"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rccg_probe_failure_when_invalid_input(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'copytype': 'invalid_input'
        })
        arg_data = {
            "id": "11",
            "name": "test_name",
            "master_cluster_id": "0000020321E04566",
            "master_cluster_name": "test_remotecluster",
            "aux_cluster_id": "0000020321E04566",
            "aux_cluster_name": "test_remotecluster",
            "primary": "",
            "state": "empty",
            "relationship_count": "0",
            "freeze_time": "",
            "status": "",
            "sync": "",
            "copy_type": "global",
            "cycling_mode": "",
            "cycle_period_seconds": "0"
        }
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCRCCG()
            obj.rccg_probe(arg_data)
        self.assertTrue(exc.value.args[0]["failed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replicationgroup.IBMSVCRCCG.get_existing_rccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rccg_create(self, svc_authorize_mock, get_existing_rccg_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'copytype': 'metro'
        })
        get_existing_rccg_mock.return_value = {}
        svc_run_command_mock.return_value = {
            'message': 'RC Consistency Group, id [3], successfully created',
            'id': '3'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCRCCG()
            obj.rccg_create()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rccg_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'copytype': 'metro',
            'cyclingperiod': 299
        })
        sample_modify = {
            'global': True
        }
        sample_modifycv = {
            'cycleperiodseconds': 300,
        }
        obj = IBMSVCRCCG()
        return_data = obj.rccg_update(sample_modify, sample_modifycv)
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replicationgroup.IBMSVCRCCG.get_existing_rccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rccg_delete(self, svc_authorize_mock, get_existing_rccg_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'copytype': 'metro'
        })
        get_existing_rccg_mock.return_value = {
            "id": "11",
            "name": "test_name",
            "master_cluster_id": "0000020321E04566",
            "master_cluster_name": "test_remotecluster",
            "aux_cluster_id": "0000020321E04566",
            "aux_cluster_name": "test_remotecluster",
            "primary": "",
            "state": "empty",
            "relationship_count": "0",
            "freeze_time": "",
            "status": "",
            "sync": "",
            "copy_type": "metro",
            "cycling_mode": "",
            "cycle_period_seconds": "0"
        }
        svc_run_command_mock.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCRCCG()
            obj.rccg_delete()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replicationgroup.IBMSVCRCCG.get_existing_rccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_deletion(self, svc_authorize_mock, svc_run_command_mock, get_existing_rccg_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
        })
        get_existing_rccg_mock.return_value = {
            "id": "11",
            "name": "test_name",
            "master_cluster_id": "0000020321E04566",
            "master_cluster_name": "test_remotecluster",
            "aux_cluster_id": "0000020321E04566",
            "aux_cluster_name": "test_remotecluster",
            "primary": "",
            "state": "empty",
            "relationship_count": "0",
            "freeze_time": "",
            "status": "",
            "sync": "",
            "copy_type": "metro",
            "cycling_mode": "",
            "cycle_period_seconds": "0"
        }
        svc_run_command_mock.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCRCCG()
            obj.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replicationgroup.IBMSVCRCCG.get_existing_rccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_creation(self, svc_authorize_mock, svc_run_command_mock, get_existing_rccg_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present'
        })
        get_existing_rccg_mock.return_value = {}
        svc_run_command_mock.return_value = {
            'message': 'RC Consistency Group, id [3], successfully created',
            'id': '3'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCRCCG()
            obj.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replicationgroup.IBMSVCRCCG.get_existing_rccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_updation(self, svc_authorize_mock, svc_run_command_mock, get_existing_rccg_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'copytype': 'global'
        })
        get_existing_rccg_mock.return_value = {
            "id": "11",
            "name": "test_name",
            "master_cluster_id": "0000020321E04566",
            "master_cluster_name": "test_remotecluster",
            "aux_cluster_id": "0000020321E04566",
            "aux_cluster_name": "test_remotecluster",
            "primary": "",
            "state": "empty",
            "relationship_count": "0",
            "freeze_time": "",
            "status": "",
            "sync": "",
            "copy_type": "metro",
            "cycling_mode": "",
            "cycle_period_seconds": "0"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCRCCG()
            obj.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replicationgroup.IBMSVCRCCG.get_existing_rccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_existing(self, svc_authorize_mock, svc_run_command_mock, get_existing_rccg_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'copytype': 'metro'
        })
        get_existing_rccg_mock.return_value = {
            "id": "11",
            "name": "test_name",
            "master_cluster_id": "0000020321E04566",
            "master_cluster_name": "test_remotecluster",
            "aux_cluster_id": "0000020321E04566",
            "aux_cluster_name": "test_remotecluster",
            "primary": "",
            "state": "empty",
            "relationship_count": "0",
            "freeze_time": "",
            "status": "",
            "sync": "",
            "copy_type": "metro",
            "cycling_mode": "",
            "cycle_period_seconds": "0"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCRCCG()
            obj.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replicationgroup.IBMSVCRCCG.get_existing_rccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_non_existing(self, svc_authorize_mock, svc_run_command_mock, get_existing_rccg_mock):
        set_module_args({
            'clustername': 'test_remotecluster',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
            'copytype': 'metro'
        })
        get_existing_rccg_mock.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCRCCG()
            obj.apply()
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == "__main__":
    unittest.main()
