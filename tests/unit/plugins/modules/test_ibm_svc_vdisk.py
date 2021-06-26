# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_vdisk """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_vdisk import IBMSVCvdisk


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


class TestIBMSVCvdisk(unittest.TestCase):
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
            IBMSVCvdisk()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_volume(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_get_existing_volume',
            'mdiskgrp': 'Ansible-Pool'
        })
        vol_ret = [{"id": "0", "name": "test_get_existing_volume",
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
        vol = IBMSVCvdisk().get_existing_vdisk()
        self.assertEqual('test_get_existing_volume', vol[0]['name'])
        self.assertEqual('0', vol[0]['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_volume_create_get_existing_volume_called(
            self, svc_authorize_mock,
            get_existing_volume_mock,
            vdisk_create_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
        })
        vol_created = IBMSVCvdisk()
        get_existing_volume_mock.return_value = []
        vdisk_create_mock.return_value = {
            u'message': u'Storage volume, id [0] successfully created',
            u'id': u'0'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            vol_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volume_failed_since_missed_required_param(
            self, svc_authorize_mock, get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_failed_since_missed_required_param',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
        })
        get_existing_volume_mock.return_value = []
        vol_created = IBMSVCvdisk()
        with pytest.raises(AnsibleFailJson) as exc:
            vol_created.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.vdisk_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volume_but_volume_existed(self, svc_authorize_mock,
                                              volume_probe_mock,
                                              get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
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
        get_existing_volume_mock.return_value = vol_ret
        volume_probe_mock.return_value = []
        volume_created = IBMSVCvdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volume_successfully(self, svc_authorize_mock,
                                        volume_create_mock,
                                        get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
        })
        volume = {u'message': u'Storage volume, id [0], '
                              u'successfully created', u'id': u'0'}
        volume_create_mock.return_value = volume
        get_existing_volume_mock.return_value = []
        volume_created = IBMSVCvdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volume_failed_since_no_message_in_result(
            self, svc_authorize_mock, svc_run_command_mock,
            get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
        })
        volume = {u'id': u'0'}
        svc_run_command_mock.return_value = volume
        get_existing_volume_mock.return_value = []
        volume_created = IBMSVCvdisk()
        with pytest.raises(AnsibleFailJson) as exc:
            volume_created.apply()
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_volume_but_volume_not_existed(self, svc_authorize_mock,
                                                  get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'size': '4294967296',
            'unit': 'b',
        })
        get_existing_volume_mock.return_value = []
        volume_deleted = IBMSVCvdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.vdisk_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_volume_successfully(self, svc_authorize_mock,
                                        volume_delete_mock,
                                        get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_delete_volume_successfully',
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
        get_existing_volume_mock.return_value = vol_ret
        volume_deleted = IBMSVCvdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_deleted.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.vdisk_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_thin_volume_but_volume_existed(self, svc_authorize_mock, volume_probe_mock, get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
            'rsize': '20%',
            'autoexpand': True
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
        get_existing_volume_mock.return_value = vol_ret
        volume_probe_mock.return_value = []
        volume_created = IBMSVCvdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_thin_volume_successfully(self, svc_authorize_mock, volume_create_mock, get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
            'rsize': '20%'
        })
        volume = {u'message': u'Storage volume, id [0], '
                              u'successfully created', u'id': u'0'}
        volume_create_mock.return_value = volume
        get_existing_volume_mock.return_value = []
        volume_created = IBMSVCvdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.get_existing_vdisk')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vdisk.IBMSVCvdisk.vdisk_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_thin_volume_successfully_with_autoexpand(self, svc_authorize_mock, volume_create_mock, get_existing_volume_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '4294967296',
            'unit': 'b',
            'rsize': '20%',
            'autoexpand': True
        })
        volume = {u'message': u'Storage volume, id [0], '
                              u'successfully created', u'id': u'0'}
        volume_create_mock.return_value = volume
        get_existing_volume_mock.return_value = []
        volume_created = IBMSVCvdisk()
        with pytest.raises(AnsibleExitJson) as exc:
            volume_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_volume_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_convert_to_bytes(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_volume_but_volume_existed',
            'mdiskgrp': 'Ansible-Pool',
            'easytier': 'off',
            'size': '2',
            'unit': 'gb',
            'rsize': '20%',
            'autoexpand': True
        })
        v = IBMSVCvdisk()
        data = v.convert_to_bytes()
        self.assertEqual(2147483648, data)


if __name__ == '__main__':
    unittest.main()
