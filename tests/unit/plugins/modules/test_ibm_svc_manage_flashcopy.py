# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_flashcopy """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_flashcopy import IBMSVCFlashcopy


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


class TestIBMSVCFlashcopy(unittest.TestCase):
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
            IBMSVCFlashcopy()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_run_command(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        arg = ["lsvdisk", {'bytes': True, 'filtervalue': 'name=test_source'}, None]
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
        obj = IBMSVCFlashcopy()
        data = obj.run_command(arg)
        self.assertEqual("test_name", data["name"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_gather_data(self, svc_authorize_mock, s1):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
        })
        s1.return_value = {
            "id": "45", "name": "test_name", "source_vdisk_id": "320", "source_vdisk_name": "Ans_n7",
            "target_vdisk_id": "323", "target_vdisk_name": "target_vdisk", "group_id": "1", "group_name": "test_group",
            "status": "idle_or_copied", "progress": "0", "copy_rate": "0", "start_time": "",
            "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "0",
            "incremental": "off", "difference": "100", "grain_size": "256", "IO_group_id": "0",
            "IO_group_name": "io_grp_name", "partner_FC_id": "43", "partner_FC_name": "test_fcmap",
            "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic",
            "restore_progress": "0", "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        obj = IBMSVCFlashcopy()
        data = obj.gather_data()
        self.assertEqual(data[0]["name"], "test_name")

    """
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_fcmapping(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
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
        obj = IBMSVCFlashcopy()
        data = obj.get_existing_fcmapping()
        self.assertEqual("test_name", data["name"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_vdisk(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        svc_obj_info_mock.return_value = [
            {
                "id": "500", "name": "test_source", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
                "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
                "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
                "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
                "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
                "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
                "volume_name": "master_vol_8", "function": "master", "protocol": ""
            },
            {
                "id": "501", "name": "test_target", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster", "capacity": "10737418240", "type": "striped", "FC_id": "",
                "FC_name": "", "RC_id": "501", "RC_name": "rcopy_9", "vdisk_UID": "60050768108101C7C0000000000009D1",
                "fc_map_count": "0", "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1",
                "RC_change": "no", "compressed_copy_count": "0", "parent_mdisk_grp_id": "1",
                "parent_mdisk_grp_name": "AnsibleMaster", "owner_id": "", "owner_name": "", "formatting": "no",
                "encrypt": "no", "volume_id": "501", "volume_name": "master_vol_9", "function": "master", "protocol": ""
            },
            {
                "id": "502", "name": "test_target_temp_xxxx", "IO_group_id": "0", "IO_group_name": "io_grp0",
                "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
                "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "",
                "RC_id": "502", "RC_name": "rcopy_10", "vdisk_UID": "60050768108101C7C0000000000009D2", "fc_map_count": "0",
                "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no", "compressed_copy_count": "0",
                "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster", "owner_id": "", "owner_name": "",
                "formatting": "no", "encrypt": "no", "volume_id": "502", "volume_name": "master_vol_10", "function": "master", "protocol": ""
            }
        ]
        obj = IBMSVCFlashcopy()
        data = obj.get_existing_vdisk()
        self.assertEqual('test_source', data[0]['name'])
        self.assertEqual('test_target', data[1]['name'])
        self.assertEqual('test_target_temp_xxxx', data[2][0])
    """

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_target_create(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        svc_run_command_mock.return_value = {
            'id': '324',
            'message': 'Volume, id [324], successfully created'
        }
        temp_target_name_arg = 'test_target_temp_1609848271.2538939'
        sdata_arg = {
            'id': '146', 'name': 'test_source', 'IO_group_id': '0', 'IO_group_name': 'io_grp0', 'status': 'online',
            'mdisk_grp_id': '1', 'mdisk_grp_name': 'AnsibleMaster', 'capacity': '1073741824', 'type': 'striped',
            'FC_id': '', 'FC_name': '', 'RC_id': '', 'RC_name': '', 'vdisk_UID': '60050768108101C7C0000000000009E1',
            'fc_map_count': '0', 'copy_count': '1', 'fast_write_state': 'empty', 'se_copy_count': '0', 'RC_change': 'no',
            'compressed_copy_count': '0', 'parent_mdisk_grp_id': '1', 'parent_mdisk_grp_name': 'AnsibleMaster',
            'owner_id': '', 'owner_name': '', 'formatting': 'no', 'encrypt': 'no', 'volume_id': '146',
            'volume_name': 'test_source', 'function': '', 'protocol': ''
        }
        obj = IBMSVCFlashcopy()
        data = obj.target_create(temp_target_name_arg, sdata_arg)
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcmap_create(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        svc_run_command_mock.return_value = {
            'id': '39',
            'message': 'FlashCopy Mapping, id [39], successfully created'
        }
        temp_target_name_arg = 'test_target_temp_1609848271.2538939'
        obj = IBMSVCFlashcopy()
        data = obj.fcmap_create(temp_target_name_arg)
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcmap_delete(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCFlashcopy()
        data = obj.fcmap_delete()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_temp_to_target(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        temp_target_name_arg = 'test_target_temp_1609848271.2538939'
        svc_run_command_mock.return_value = None
        obj = IBMSVCFlashcopy()
        data = obj.rename_temp_to_target(temp_target_name_arg)
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_fcmap_probe(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 256,
        })
        data_arg = {
            "id": "45", "name": "test_name", "source_vdisk_id": "320", "source_vdisk_name": "test_source",
            "target_vdisk_id": "323", "target_vdisk_name": "test_target", "group_id": "1", "group_name": "test_group",
            "status": "idle_or_copied", "progress": "0", "copy_rate": "0", "start_time": "",
            "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "0",
            "incremental": "off", "difference": "100", "grain_size": "256", "IO_group_id": "0",
            "IO_group_name": "io_grp_name", "partner_FC_id": "43", "partner_FC_name": "test_fcmap",
            "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic",
            "restore_progress": "0", "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        obj = IBMSVCFlashcopy()
        data = obj.fcmap_probe(data_arg)
        self.assertEqual('test_consistgrp', data['consistgrp'])
        self.assertEqual('50', data['copyrate'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcmap_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        modify_arg = {
            'consistgrp': 'test_consistgrp',
            'copyrate': 50
        }
        obj = IBMSVCFlashcopy()
        data = obj.fcmap_update(modify_arg)
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.rename_temp_to_target')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.fcmap_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.target_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.gather_data')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_creating_fcmap(self, svc_authorize_mock, svc_run_command_mock, gd, tcm, fcm, rtttm):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        sdata = {
            "id": "500", "name": "test_source", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        gd.return_value = ({}, [sdata], None, [])
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.gather_data')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_creating_existing_fcmap(self, svc_authorize_mock, svc_run_command_mock, gd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        fdata = {
            "id": "45", "name": "test_name", "source_vdisk_id": "320", "source_vdisk_name": "test_source",
            "target_vdisk_id": "323", "target_vdisk_name": "test_target", "group_id": "1", "group_name": "test_consistgrp",
            "status": "idle_or_copied", "progress": "0", "copy_rate": "50", "start_time": "",
            "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "0",
            "incremental": "off", "difference": "100", "grain_size": "64", "IO_group_id": "0",
            "IO_group_name": "io_grp_name", "partner_FC_id": "43", "partner_FC_name": "test_fcmap",
            "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic",
            "restore_progress": "0", "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        sdata = {
            "id": "500", "name": "test_source", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        tdata = {
            "id": "500", "name": "test_target", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        gd.return_value = (fdata, sdata, tdata, [])
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(False, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.gather_data')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_updating_existing_fcmap(self, svc_authorize_mock, svc_run_command_mock, gd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        fdata = {
            "id": "45", "name": "test_name", "source_vdisk_id": "320", "source_vdisk_name": "test_source",
            "target_vdisk_id": "323", "target_vdisk_name": "test_target", "group_id": "1", "group_name": "new_consistgrp",
            "status": "idle_or_copied", "progress": "0", "copy_rate": "100", "start_time": "",
            "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "0",
            "incremental": "off", "difference": "100", "grain_size": "64", "IO_group_id": "0",
            "IO_group_name": "io_grp_name", "partner_FC_id": "43", "partner_FC_name": "test_fcmap",
            "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic",
            "restore_progress": "0", "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        sdata = {
            "id": "500", "name": "test_source", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        tdata = {
            "id": "500", "name": "test_target", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        gd.return_value = (fdata, sdata, tdata, [])
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.gather_data')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_with_source_missing(self, svc_authorize_mock, svc_run_command_mock, gd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        gd.return_value = (None, None, None, [])
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.rename_temp_to_target')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.fcmap_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.target_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.gather_data')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_with_more_temp_vdisk(self, svc_authorize_mock, svc_run_command_mock, gd, tcm, fcm, rtttm):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 50,
            'grainsize': 64,
        })
        sdata = {
            "id": "500", "name": "test_source", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        temp1 = {
            "id": "500", "name": "test_target_temp_1609848271.2538939", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        temp2 = {
            "id": "500", "name": "test_target_temp_1609848272.2538939", "IO_group_id": "0", "IO_group_name": "io_grp0",
            "status": "online", "mdisk_grp_id": "1", "mdisk_grp_name": "AnsibleMaster",
            "capacity": "10737418240", "type": "striped", "FC_id": "", "FC_name": "", "RC_id": "500",
            "RC_name": "rcopy_8", "vdisk_UID": "60050768108101C7C0000000000009D0", "fc_map_count": "0",
            "copy_count": "1", "fast_write_state": "not_empty", "se_copy_count": "1", "RC_change": "no",
            "compressed_copy_count": "0", "parent_mdisk_grp_id": "1", "parent_mdisk_grp_name": "AnsibleMaster",
            "owner_id": "", "owner_name": "", "formatting": "no", "encrypt": "no", "volume_id": "500",
            "volume_name": "master_vol_8", "function": "master", "protocol": ""
        }
        gd.return_value = ({}, sdata, None, [temp1, temp2])
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.gather_data')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_deleting_existing_fcmap(self, svc_authorize_mock, svc_run_command_mock, gd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
        })
        fdata = {
            "id": "45", "name": "test_name", "source_vdisk_id": "320", "source_vdisk_name": "Ans_n7",
            "target_vdisk_id": "323", "target_vdisk_name": "target_vdisk", "group_id": "1", "group_name": "new_consistgrp",
            "status": "idle_or_copied", "progress": "0", "copy_rate": "100", "start_time": "",
            "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "0",
            "incremental": "off", "difference": "100", "grain_size": "64", "IO_group_id": "0",
            "IO_group_name": "io_grp_name", "partner_FC_id": "43", "partner_FC_name": "test_fcmap",
            "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic",
            "restore_progress": "0", "fc_controlled": "no", "owner_id": "", "owner_name": ""
        }
        gd.return_value = [fdata, None, None, []]
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_flashcopy.IBMSVCFlashcopy.gather_data')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_deleting_non_existing_fcmap(self, svc_authorize_mock, svc_run_command_mock, gd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_name'
        })
        gd.return_value = [{}, None, None, []]
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(False, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_with_missing_parameter(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
        })
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_with_copyrate_outside_range(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'copytype': 'snapshot',
            'source': 'test_source',
            'target': 'test_target',
            'mdiskgrp': 'test_mdiskgrp',
            'consistgrp': 'test_consistgrp',
            'copyrate': 500,
            'grainsize': 64,
        })
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCFlashcopy()
            data = obj.apply()

        self.assertEqual(True, exc.value.args[0]['failed'])


if __name__ == "__main__":
    unittest.main()
