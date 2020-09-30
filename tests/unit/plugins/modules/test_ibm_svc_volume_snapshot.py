# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_volume_snapshot """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_volume_snapshot import IBMSVCSnapshot


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


class TestIBMSVCSnapshot(unittest.TestCase):
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
                                     False, 'test.log')

    def set_default_args(self):
        return dict({
            'name': 'test',
            'state': 'present'
        })

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVCSnapshot()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_snapshot(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_get_existing_snapshot',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol'
        })
        vol_ret = [{"id": "0", "name": "volume_Ansible_collections",
                    "IO_group_id": "0", "IO_group_name": "io_grp0",
                    "status": "online", "mdisk_grp_id": "0",
                    "mdisk_grp_name": "Pool_Ansible_collections",
                    "capacity": "4.00GB", "type": "striped", "FC_id": "",
                    "FC_name": "", "RC_id": "", "RC_name": "",
                    "vdisk_UID": "6005076810CA0166C00000000000019F",
                    "fc_map_count": "0", "copy_count": "1",
                    "fast_write_state": "empty", "se_copy_count": "0",
                    "RC_change": "no", "compressed_copy_count": "0",
                    "parent_mdisk_grp_id": "0",
                    "parent_mdisk_grp_name": "Pool_Ansible_collections",
                    "owner_id": "", "owner_name": "", "formatting": "no",
                    "encrypt": "no", "volume_id": "0",
                    "volume_name": "volume_Ansible_collections",
                    "function": "", "protocol": "scsi"}]
        svc_obj_info_mock.return_value = vol_ret
        vol = IBMSVCSnapshot().get_existing_snapshot()
        self.assertEqual('volume_Ansible_collections', vol['name'])
        self.assertEqual('0', vol['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.get_fc_mapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.flashcopymap_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcmap_create_get_fc_mapping_called(self, svc_authorize_mock,
                                                mock_flashcopymap_probe,
                                                get_fc_mapping_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_get_existing_snapshot',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol'
        })
        fcmap_created = IBMSVCSnapshot()
        mock_flashcopymap_probe.return_value = []
        with pytest.raises(AnsibleExitJson) as exc:
            fcmap_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_fc_mapping_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fcmap_for_snapshot_failed_since_missed_required_param(
            self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_get_existing_snapshot',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSnapshot().apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.get_fc_mapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.flashcopymap_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fcmap_but_fcmap_existed(self, svc_authorize_mock,
                                            flashcopymap_probe_mock,
                                            get_fc_mapping_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'vol_snapshot_fcmapping',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol'
        })
        fcmap_ret = [{'id': '0', 'name': 'vol_snapshot_fcmapping',
                      'source_vdisk_id': '0',
                      'source_vdisk_name': 'volume_Ansible_collections',
                      'target_vdisk_id': '1',
                      'target_vdisk_name': 'volume_Ansible_snapshot',
                      'group_id': '', 'group_name': '',
                      'status': 'idle_or_copied', 'progress': '0',
                      'copy_rate': '0', 'start_time': '',
                      'dependent_mappings': '0', 'autodelete': 'off',
                      'clean_progress': '100', 'clean_rate': '50',
                      'incremental': 'off', 'difference': '100',
                      'grain_size': '256', 'IO_group_id': '0',
                      'IO_group_name': 'io_grp0', 'partner_FC_id': '',
                      'partner_FC_name': '', 'restoring': 'no',
                      'rc_controlled': 'no', 'keep_target': 'no',
                      'type': 'generic', 'restore_progress': '0',
                      'fc_controlled': 'no', 'owner_id': '', 'owner_name': ''}]
        get_fc_mapping_mock.return_value = fcmap_ret
        flashcopymap_probe_mock.return_value = []
        volume_created = IBMSVCSnapshot()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_fc_mapping_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.get_fc_mapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_flashcopymap_probe(self, svc_authorize_mock, get_fc_mapping_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'vol_snapshot_fcmapping',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol',
            'copyrate': '50'
        })
        fcmap_ret = [{'id': '0', 'name': 'vol_snapshot_fcmapping',
                      'source_vdisk_id': '0',
                      'source_vdisk_name': 'volume_Ansible_collections',
                      'target_vdisk_id': '1',
                      'target_vdisk_name': 'volume_Ansible_snapshot',
                      'group_id': '', 'group_name': '',
                      'status': 'idle_or_copied', 'progress': '0',
                      'copy_rate': '0', 'start_time': '',
                      'dependent_mappings': '0', 'autodelete': 'off',
                      'clean_progress': '100', 'clean_rate': '50',
                      'incremental': 'off', 'difference': '100',
                      'grain_size': '256', 'IO_group_id': '0',
                      'IO_group_name': 'io_grp0', 'partner_FC_id': '',
                      'partner_FC_name': '', 'restoring': 'no',
                      'rc_controlled': 'no', 'keep_target': 'no',
                      'type': 'generic', 'restore_progress': '0',
                      'fc_controlled': 'no', 'owner_id': '', 'owner_name': ''}]
        get_fc_mapping_mock.return_value = fcmap_ret
        ret = IBMSVCSnapshot().flashcopymap_probe(fcmap_ret[0])
        print('Info: %s' % ret['copyrate'])
        self.assertEqual('50', ret['copyrate'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.get_fc_mapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.flashcopymap_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_snapshot_successfully(self, svc_authorize_mock,
                                          flashcopymap_create_mock,
                                          get_fc_mapping_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'volume_Ansible_collections',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol'
        })
        fcmap = {u'message': u'Flash Copy mapping, id [0], '
                             u'successfully created', u'id': u'0'}
        flashcopymap_create_mock.return_value = fcmap
        get_fc_mapping_mock.return_value = []
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCSnapshot().apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_fc_mapping_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.get_fc_mapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_snapshot_failed_since_no_message_in_result(
            self, svc_authorize_mock, svc_run_command_mock,
            get_fc_mapping_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'volume_Ansible_collections',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol'
        })
        snapshot = {u'id': u'0'}
        svc_run_command_mock.return_value = snapshot
        get_fc_mapping_mock.return_value = []
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCSnapshot().apply()
        get_fc_mapping_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.get_fc_mapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_fcmap_but_fcmap_not_existed(self, svc_authorize_mock,
                                                get_fc_mapping_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'volume_Ansible_collections',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol'
        })
        get_fc_mapping_mock.return_value = []
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCSnapshot().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_fc_mapping_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.get_fc_mapping')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_volume_snapshot.IBMSVCSnapshot.flashcopymap_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_fcmap_successfully(self, svc_authorize_mock,
                                       flashcopymap_delete_mock,
                                       get_fc_mapping_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'volume_Ansible_collections',
            'mdiskgrp': 'Ansible-Pool',
            'volume': 'source-vol',
            'snapshot': 'snapshot-vol'
        })
        fcmap_ret = [{'id': '0', 'name': 'vol_snapshot_fcmapping',
                      'source_vdisk_id': '0',
                      'source_vdisk_name': 'volume_Ansible_collections',
                      'target_vdisk_id': '1',
                      'target_vdisk_name': 'volume_Ansible_snapshot',
                      'group_id': '', 'group_name': '',
                      'status': 'idle_or_copied', 'progress': '0',
                      'copy_rate': '0', 'start_time': '',
                      'dependent_mappings': '0', 'autodelete': 'off',
                      'clean_progress': '100', 'clean_rate': '50',
                      'incremental': 'off', 'difference': '100',
                      'grain_size': '256', 'IO_group_id': '0',
                      'IO_group_name': 'io_grp0', 'partner_FC_id': '',
                      'partner_FC_name': '', 'restoring': 'no',
                      'rc_controlled': 'no', 'keep_target': 'no',
                      'type': 'generic', 'restore_progress': '0',
                      'fc_controlled': 'no', 'owner_id': '', 'owner_name': ''}]
        get_fc_mapping_mock.return_value = fcmap_ret
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCSnapshot().apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_fc_mapping_mock.assert_called_with()


if __name__ == '__main__':
    unittest.main()
