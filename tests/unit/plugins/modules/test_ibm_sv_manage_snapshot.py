# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_manage_snapshot """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_manage_snapshot import IBMSVSnapshot


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


class TestIBMSVSnapshot(unittest.TestCase):
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
            IBMSVSnapshot()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_module_without_state_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVSnapshot()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_case(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'src_volume_names': 'vol0:vol1',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVSnapshot()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_snapshot_validation(self, svc_authorize_mock, snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'old_name': 'snapshot0',
            'state': 'present',
        })
        snapshot_exists_mock.return_value = True
        ss = IBMSVSnapshot()

        with pytest.raises(AnsibleFailJson) as exc:
            ss.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_snapshot_validation_1(self, svc_authorize_mock,
                                          lsvolumegroupsnapshot_mock,
                                          snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'ownershipgroup': 'owner0',
            'safeguarded': True,
            'retentiondays': 5,
            'state': 'present',
        })
        snapshot_exists_mock.return_value = True
        lsvolumegroupsnapshot_mock.return_value = {'owner_name': '', 'safeguarded': 'yes'}
        ss = IBMSVSnapshot()

        with pytest.raises(AnsibleFailJson) as exc:
            ss.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_snapshot_validation(self, svc_authorize_mock,
                                        snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'ownershipgroup': 'owner0',
            'state': 'present',
        })
        snapshot_exists_mock.return_value = False
        ss = IBMSVSnapshot()

        with pytest.raises(AnsibleFailJson) as exc:
            ss.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_snapshot_validation_2(self, svc_authorize_mock,
                                          lsvolumegroupsnapshot_mock,
                                          snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'snapshot_pool': 'childpool0',
            'ownershipgroup': 'owner0',
            'state': 'present',
        })
        snapshot_exists_mock.return_value = True
        lsvolumegroupsnapshot_mock.return_value = {'owner_name': ''}
        ss = IBMSVSnapshot()

        with pytest.raises(AnsibleFailJson) as exc:
            ss.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_snapshot(self,
                                         svc_authorize_mock,
                                         svc_run_command_mock,
                                         snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'state': 'present',
        })

        snapshot_exists_mock.return_value = {}

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_snapshot_idempotency(self,
                                                     svc_authorize_mock,
                                                     svc_run_command_mock,
                                                     lsvg_mock,
                                                     snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'state': 'present',
        })

        snapshot_exists_mock.return_value = {
            "id": '0',
            "name": 'snapshot0',
            "owner_name": ''
        }

        lsvg_mock.return_value = {
            "id": '0',
            "name": 'snapshot0',
            "owner_name": ''
        }

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_safeguarded_volumegroup_snapshot(self,
                                                     svc_authorize_mock,
                                                     svc_run_command_mock,
                                                     snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'state': 'present',
            'safeguarded': True,
            'retentiondays': 2
        })

        snapshot_exists_mock.return_value = {}

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_safeguarded_volumegroup_snapshot_idempotency(self,
                                                                 svc_authorize_mock,
                                                                 svc_run_command_mock,
                                                                 lsvg_mock,
                                                                 snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volumegroup_name': 'volgrp0',
            'state': 'present',
            'safeguarded': True,
            'retentiondays': 2
        })

        snapshot_exists_mock.return_value = {
            "id": '0',
            "name": 'snapshot0',
            "owner_name": '',
            'safeguarded': 'yes'
        }

        lsvg_mock.return_value = {
            "id": '0',
            "name": 'snapshot0',
            "owner_name": '',
            'safeguarded': 'yes'
        }

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volume_snapshot(self,
                                    svc_authorize_mock,
                                    svc_run_command_mock,
                                    snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volume_names': 'vol0:vol1',
            'state': 'present',
        })

        snapshot_exists_mock.return_value = {}

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volume_snapshot_idempotency(self,
                                                svc_authorize_mock,
                                                svc_run_command_mock,
                                                lsvg_mock,
                                                snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volume_names': 'vol0:vol1',
            'state': 'present',
        })

        snapshot_exists_mock.return_value = {
            'id': 1,
            'snapshot_name': 'snapshot0'
        }

        lsvg_mock.return_value = {
            'id': 1,
            'snapshot_name': 'snapshot0'
        }

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_safeguarded_volume_snapshot(self,
                                                svc_authorize_mock,
                                                svc_run_command_mock,
                                                snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volume_names': 'vol0:vol1',
            'state': 'present',
            'safeguarded': True,
            'retentiondays': 2
        })

        snapshot_exists_mock.return_value = {}

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_safeguarded_volume_snapshot_idempotency(self,
                                                            svc_authorize_mock,
                                                            svc_run_command_mock,
                                                            lsvg_mock,
                                                            snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'src_volume_names': 'vol0:vol1',
            'state': 'present',
            'safeguarded': True,
            'retentiondays': 2
        })

        snapshot_exists_mock.return_value = {
            'id': 1,
            'snapshot_name': 'snapshot0',
            'safeguarded': 'yes'
        }

        lsvg_mock.return_value = {
            'id': 1,
            'snapshot_name': 'snapshot0',
            'safeguarded': 'yes'
        }

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.snapshot_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_snapshot_name_ownership(self,
                                            svc_authorize_mock,
                                            svc_run_command_mock,
                                            snapshot_probe_mock,
                                            lsvg_mock,
                                            snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snap0',
            'src_volumegroup_name': 'volgrp0',
            'old_name': 'snapshot0',
            'ownershipgroup': 'owner0',
            'state': 'present',
        })

        snapshot_probe_mock.return_value = ['name', 'ownershipgroup']

        snapshot_exists_mock.return_value = {
            "id": '0',
            "name": 'snapshot0',
            "owner_name": ''
        }

        lsvg_mock.return_value = {
            "id": '0',
            "name": 'snapshot0',
            "owner_name": ''
        }

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.lsvolumegroupsnapshot')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_snapshot_ownership_idempotency(self,
                                                   svc_authorize_mock,
                                                   svc_run_command_mock,
                                                   lsvg_mock,
                                                   snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snap0',
            'src_volumegroup_name': 'volgrp0',
            'ownershipgroup': 'owner0',
            'state': 'present',
        })

        snapshot_exists_mock.return_value = {
            "id": '0',
            "name": 'snap0',
            "owner_name": 'owner0'
        }

        lsvg_mock.return_value = {
            "id": '0',
            "name": 'snap0',
            "owner_name": 'owner0'
        }

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_snapshot(self,
                             svc_authorize_mock,
                             svc_run_command_mock,
                             snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'state': 'absent',
        })

        snapshot_exists_mock.side_effect = iter([
            {
                "id": '0',
                "name": 'snapshot0',
                "owner_name": ''
            },
            {}
        ])

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_snapshot_idempotency(self,
                                         svc_authorize_mock,
                                         svc_run_command_mock,
                                         snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'state': 'absent',
        })

        snapshot_exists_mock.return_value = {}

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_snapshot.IBMSVSnapshot.is_snapshot_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_dependent_snapshot(self,
                                       svc_authorize_mock,
                                       svc_run_command_mock,
                                       snapshot_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'snapshot0',
            'state': 'absent',
        })

        snapshot_exists_mock.side_effect = iter([
            {
                "id": '0',
                "name": 'snapshot0',
                "owner_name": ''
            },
            {
                "id": '0',
                "name": 'snapshot0',
                "owner_name": ''
            }
        ])

        fc = IBMSVSnapshot()

        with pytest.raises(AnsibleExitJson) as exc:
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
