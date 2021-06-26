# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_start_stop_flashcopy """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_start_stop_flashcopy import IBMSVCFlashcopyStartStop


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


class TestIBMSVCFlashcopyStartStop(unittest.TestCase):
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
            IBMSVCFlashcopyStartStop()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_fcmapping(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started'
        })
        svc_obj_info_mock.return_value = {
            "id": "45", "name": "test_name", "source_vdisk_id": "320", "source_vdisk_name": "Ans_n7",
            "target_vdisk_id": "323", "target_vdisk_name": "target_vdisk", "group_id": "1", "group_name": "test_group",
            "status": "idle_or_copied", "progress": "0", "copy_rate": "0", "start_time": "",
            "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "0",
            "incremental": "off", "difference": "100", "grain_size": "256", "IO_group_id": "0",
            "IO_group_name": "io_grp_name", "partner_FC_id": "43", "partner_FC_name": "test_fcmap",
            "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic",
            "restore_progress": "0", "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        obj = IBMSVCFlashcopyStartStop()
        data = obj.get_existing_fcmapping()
        self.assertEqual('test_name', data['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_fcmapping_isgroup(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_group',
            'state': 'started',
            'isgroup': True
        })
        svc_obj_info_mock.return_value = {
            'id': '4', 'name': 'test_group', 'status': 'stopped',
            'autodelete': 'off', 'start_time': '', 'owner_id': '0',
            'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '39',
            'FC_mapping_name': 'test_mapping'
        }
        obj = IBMSVCFlashcopyStartStop()
        data = obj.get_existing_fcmapping()
        self.assertEqual('test_group', data['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_fc(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCFlashcopyStartStop()
        data = obj.start_fc()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_fc_isgroup(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'isgroup': True
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCFlashcopyStartStop()
        data = obj.start_fc()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_fc(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCFlashcopyStartStop()
        data = obj.stop_fc()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_fc_isgroup(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
            'isgroup': True
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCFlashcopyStartStop()
        data = obj.stop_fc()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.start_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_existsting_fc_mappping(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started'
        })
        gef.return_value = {
            "id": "39", "name": "test_mapping", "source_vdisk_id": "146",
            "source_vdisk_name": "test_source", "target_vdisk_id": "324",
            "target_vdisk_name": "test_target", "group_id": "", "group_name": "",
            "status": "idle_or_copied", "progress": "0", "copy_rate": "41", "start_time": "",
            "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100",
            "clean_rate": "50", "incremental": "off", "difference": "100", "grain_size": "256",
            "IO_group_id": "0", "IO_group_name": "io_grp0", "partner_FC_id": "",
            "partner_FC_name": "", "restoring": "no", "rc_controlled": "no", "keep_target": "no",
            "type": "generic", "restore_progress": "0", "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.start_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_nonexiststing_fc_mappping(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started'
        })
        gef.return_value = {}
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(False, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.start_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_existsting_fc_consistgrp(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_group',
            'state': 'started',
            'isgroup': True
        })
        gef.return_value = {
            'id': '4', 'name': 'test_group', 'status': 'copying',
            'autodelete': 'off', 'start_time': '210112110946', 'owner_id': '0',
            'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '39',
            'FC_mapping_name': 'test_mapping'
        }
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(False, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.start_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_nonexiststing_fc_consistgrp(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_group',
            'state': 'started',
            'isgroup': True
        })
        gef.return_value = {}
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(False, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.stop_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_mappping(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped'
        })
        gef.return_value = {
            "id": "39", "name": "test_mapping", "source_vdisk_id": "146",
            "source_vdisk_name": "test_source", "target_vdisk_id": "324",
            "target_vdisk_name": "test_target", "group_id": "4",
            "group_name": "test_group", "status": "copying", "progress": "0",
            "copy_rate": "41", "start_time": "210112113610", "dependent_mappings": "0",
            "autodelete": "off", "clean_progress": "100", "clean_rate": "50",
            "incremental": "off", "difference": "100", "grain_size": "256",
            "IO_group_id": "0", "IO_group_name": "io_grp0", "partner_FC_id": "",
            "partner_FC_name": "", "restoring": "no", "rc_controlled": "no",
            "keep_target": "no", "type": "generic", "restore_progress": "0",
            "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.stop_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_mappping_with_force(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
            'force': True
        })
        gef.return_value = {
            "id": "39", "name": "test_mapping", "source_vdisk_id": "146",
            "source_vdisk_name": "test_source", "target_vdisk_id": "324",
            "target_vdisk_name": "test_target", "group_id": "4",
            "group_name": "test_group", "status": "copying", "progress": "0",
            "copy_rate": "41", "start_time": "210112113610", "dependent_mappings": "0",
            "autodelete": "off", "clean_progress": "100", "clean_rate": "50",
            "incremental": "off", "difference": "100", "grain_size": "256",
            "IO_group_id": "0", "IO_group_name": "io_grp0", "partner_FC_id": "",
            "partner_FC_name": "", "restoring": "no", "rc_controlled": "no",
            "keep_target": "no", "type": "generic", "restore_progress": "0",
            "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.stop_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_nonexiststing_fc_mappping(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped'
        })
        gef.return_value = {}
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(False, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.stop_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_consistgrp(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped'
        })
        gef.return_value = {
            'id': '4', 'name': 'test_group', 'status': 'copying',
            'autodelete': 'off', 'start_time': '210112113610', 'owner_id': '0',
            'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '39',
            'FC_mapping_name': 'test_mapping'
        }
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.stop_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_consistgrp_with_force(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
            'force': True
        })
        gef.return_value = {
            'id': '4', 'name': 'test_group', 'status': 'copying',
            'autodelete': 'off', 'start_time': '210112113610', 'owner_id': '0',
            'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '39',
            'FC_mapping_name': 'test_mapping'
        }
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.stop_fc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_flashcopy.IBMSVCFlashcopyStartStop.get_existing_fcmapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_nonexiststing_fc_consistgrp(self, svc_authorize_mock, gef, sc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped'
        })
        gef.return_value = {}
        sc.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyStartStop()
            obj.apply()
        self.assertEqual(False, exc.value.args[0]["changed"])


if __name__ == "__main__":
    unittest.main()
