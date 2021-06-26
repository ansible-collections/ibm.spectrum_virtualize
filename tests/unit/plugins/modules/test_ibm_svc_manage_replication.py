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
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_replication import IBMSVCManageReplication


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


class TestIBMSVCManageReplication(unittest.TestCase):
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
            IBMSVCManageReplication()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_existing_vdisk(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
        })
        svc_obj_info_mock.return_value = {
            'id': '157',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '157',
            'master_vdisk_name': 'test_master',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'metro',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        obj = IBMSVCManageReplication()
        rc_data = obj.existing_vdisk('test_name')
        self.assertEqual('test_name', rc_data['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_existing_rc(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
        })
        svc_obj_info_mock.return_value = {
            'id': '157',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '157',
            'master_vdisk_name': 'test_master',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'metro',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        obj = IBMSVCManageReplication()
        rc_data = obj.existing_rc()
        self.assertEqual('test_name', rc_data['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_cycleperiod_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'GMCV',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
            'cyclingperiod': 300
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCManageReplication()
        return_data = obj.cycleperiod_update()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_cyclemode_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'GMCV',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
            'cyclingperiod': 300
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCManageReplication()
        return_data = obj.cyclemode_update()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rcrelationship_probe_metro(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
        })
        arg_data = {
            'id': '157',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '157',
            'master_vdisk_name': 'test_master_1',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux_1',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group_1',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'global',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        obj = IBMSVCManageReplication()
        probe_return = obj.rcrelationship_probe(arg_data)
        self.assertEqual('test_consistency_group', probe_return[0]['consistgrp'])
        self.assertEqual('test_master', probe_return[0]['master'])
        self.assertEqual('test_aux', probe_return[0]['aux'])
        self.assertEqual(True, probe_return[0]['metro'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.cyclemode_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.cycleperiod_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rcrelationship_update(self, svc_authorize_mock, svc_run_command_mock, cp_u_mock, cm_u_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'global',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
            'cyclingperiod': 299
        })
        modify = {
            'consistgrp': 'test_consistency_group',
            'master': 'test_master',
            'aux': 'test_aux',
            'metro': True
        }
        modifycv = {
            'masterchange': 'test_masterchange_volume',
            'nomasterchange': 'test_auxchange_volume',
            'cycleperiodseconds': 299,
            'cyclingmode': True,
        }
        svc_run_command_mock.return_value = None
        cp_u_mock.return_value = None
        cm_u_mock.return_value = None
        obj = IBMSVCManageReplication()
        update_return = obj.rcrelationship_update(modify, modifycv)
        self.assertEqual(None, update_return)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'global',
            'sync': 'true',
            'consistgrp': 'test_consistency_group'
        })
        svc_run_command_mock.return_value = {
            'message': 'RC Relationship, id [0], successfully created',
            'id': '0'
        }
        existing_rc_mock.return_value = {
            'id': '0',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '0',
            'master_vdisk_name': 'test_master',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'metro',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        obj = IBMSVCManageReplication()
        create_return = obj.create()
        self.assertEqual('test_name', create_return['name'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_with_invalid_copytype(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'wrong_input',
            'sync': 'true',
            'consistgrp': 'test_consistency_group'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.create()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_for_failure(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.create()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_parameter_name_missing(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.create()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_parameter_master_missing(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'remotecluster': 'test_remotecluster',
            'name': 'test_name',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.create()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_parameter_aux_missing(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'remotecluster': 'test_remotecluster',
            'name': 'test_name',
            'master': 'test_master',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.create()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_parameter_remotecluster_missing(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.create()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
            'force': 'true'
        })
        svc_run_command_mock.return_value = ''
        obj = IBMSVCManageReplication()
        delete_return = obj.delete()
        self.assertEqual(None, delete_return)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_failure(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
            'force': 'true'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.delete()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_relationship(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock, create_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
        })
        existing_rc_mock.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCManageReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_non_existing_relationship(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
        })
        existing_rc_mock.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCManageReplication()
            obj.apply()
        self.assertEqual(False, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_for_failure_with_activeactive(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
        })
        existing_rc_mock.return_value = {
            'id': '157',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '157',
            'master_vdisk_name': 'test_master',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'activeactive',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCManageReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_existing_relationship(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock, delete_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
        })
        existing_rc_mock.return_value = {
            'id': '157',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '157',
            'master_vdisk_name': 'test_master',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'metro',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCManageReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_existing_relationship(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock, create_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master',
            'aux': 'test_aux',
            'copytype': 'metro',
            'sync': 'true',
            'consistgrp': 'test_consistency_group',
        })
        existing_rc_mock.return_value = {
            'id': '157',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '157',
            'master_vdisk_name': 'test_master',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'metro',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCManageReplication()
            obj.apply()
        self.assertEqual(False, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_replication.IBMSVCManageReplication.existing_rc')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_existing_relationship(self, svc_authorize_mock, svc_run_command_mock, existing_rc_mock, create_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'remotecluster': 'test_remotecluster',
            'master': 'test_master_1',
            'aux': 'test_aux_1',
            'copytype': 'global',
            'sync': 'true',
            'consistgrp': 'test_consistency_group_1',
        })
        existing_rc_mock.return_value = {
            'id': '157',
            'name': 'test_name',
            'master_cluster_id': '0000020321E04566',
            'master_cluster_name': 'FlashSystem V9000',
            'master_vdisk_id': '157',
            'master_vdisk_name': 'test_master',
            'aux_cluster_id': '0000020321E04566',
            'aux_cluster_name': 'FlashSystem V9000',
            'aux_vdisk_id': '161',
            'aux_vdisk_name': 'test_aux',
            'primary': 'aux',
            'consistency_group_id': '8',
            'consistency_group_name': 'test_consistency_group',
            'state': 'consistent_synchronized',
            'bg_copy_priority': '50',
            'progress': '',
            'freeze_time': '',
            'status': 'online',
            'sync': '',
            'copy_type': 'metro',
            'cycling_mode': '',
            'cycle_period_seconds': '300',
            'master_change_vdisk_id': '',
            'master_change_vdisk_name': '',
            'aux_change_vdisk_id': '',
            'aux_change_vdisk_name': ''
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCManageReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])


if __name__ == "__main__":
    unittest.main()
