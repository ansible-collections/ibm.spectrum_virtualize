# Copyright (C) 2022 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi1.jain@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_manage_snapshotpolicy """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_manage_snapshotpolicy import IBMSVCSnapshotPolicy


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


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an
    exception """
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestIBMSVCSnapshotPolicy(unittest.TestCase):
    """
    Group of related Unit Tests
    """

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

    def test_module_with_blank_values(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': ''
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSnapshotPolicy()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_without_state_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshotpolicy',
            'backupunit': 'day',
            'backupinterval': '1',
            'backupstarttime': '2102281800',
            'retentiondays': '2'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSnapshotPolicy()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshotpolicy.IBMSVCSnapshotPolicy.policy_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_snapshot_policy(self, svc_authorize_mock,
                                    svc_run_command_mock, sp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshotpolicy0',
            'backupunit': 'day',
            'backupinterval': '1',
            'backupstarttime': '2102281800',
            'retentiondays': '10',
            'state': 'present'
        })

        sp_exists_mock.return_value = {}

        sp = IBMSVCSnapshotPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            sp.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_snapshotpolicy_idempotency(self, svc_authorize_mock,
                                               svc_run_command_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshotpolicy0',
            'backupunit': 'day',
            'backupinterval': '1',
            'backupstarttime': '2102281800',
            'retentiondays': '10',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "policy_id": "3",
            "policy_name": "snapshotpolicy0",
            "schedule_id": "1",
            "backup_unit": "day",
            "backup_interval": "1",
            "backup_start_time": "210228180000",
            "retention_days": "10"
        }

        sp = IBMSVCSnapshotPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            sp.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshotpolicy.IBMSVCSnapshotPolicy.policy_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_snapshot_policy_failure(self, svc_authorize_mock,
                                            svc_run_command_mock, sp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshotpolicy0',
            'backupunit': 'day',
            'backupinterval': '1',
            'backupstarttime': '2102281800',
            'retentiondays': '10',
            'state': 'absent'
        })

        sp_exists_mock.return_value = {
            "policy_id": "3",
            "policy_name": "snapshotpolicy0",
            "schedule_id": "1",
            "backup_unit": "day",
            "backup_interval": "1",
            "backup_start_time": "210228180000",
            "retention_days": "10"
        }

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSnapshotPolicy()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshotpolicy.IBMSVCSnapshotPolicy.policy_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_snapshot_policy(self, svc_authorize_mock,
                                    svc_run_command_mock, sp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshotpolicy0',
            'state': 'absent'
        })

        sp_exists_mock.return_value = {
            "policy_id": "3",
            "policy_name": "snapshotpolicy0",
            "schedule_id": "1",
            "backup_unit": "day",
            "backup_interval": "1",
            "backup_start_time": "210228180000",
            "retention_days": "10"
        }

        sp = IBMSVCSnapshotPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            sp.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshotpolicy.IBMSVCSnapshotPolicy.policy_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_snapshotpolicy_idempotency(self, svc_authorize_mock,
                                               svc_run_command_mock, sp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshotpolicy0',
            'state': 'absent'
        })

        sp_exists_mock.return_value = {}

        sp = IBMSVCSnapshotPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            sp.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshotpolicy.IBMSVCSnapshotPolicy.policy_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_suspend_snapshotpolicy_failure(self, svc_authorize_mock,
                                            svc_run_command_mock, sp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshotpolicy0',
            'backupunit': 'day',
            'backupinterval': '1',
            'backupstarttime': '2102281800',
            'retentiondays': '10',
            'state': 'suspend'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSnapshotPolicy()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshotpolicy.IBMSVCSnapshotPolicy.policy_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_suspend_snapshotpolicy(self, svc_authorize_mock,
                                    svc_run_command_mock, sp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'suspend'
        })

        sp = IBMSVCSnapshotPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            sp.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshotpolicy.IBMSVCSnapshotPolicy.policy_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_resume_snapshotpolicy(self, svc_authorize_mock,
                                   svc_run_command_mock, sp_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'resume'
        })

        sp = IBMSVCSnapshotPolicy()

        with pytest.raises(AnsibleExitJson) as exc:
            sp.apply()
        self.assertTrue(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
