# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_vol_map """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_vol_map import IBMSVCvdiskhostmap


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


class TestIBMSVCvdiskhostmap(unittest.TestCase):
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
            IBMSVCvdiskhostmap()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_vdiskhostmap(self, svc_authorize_mock,
                                       svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'host': 'host4test',
        })
        mapping_ret = [{"id": "0", "name": "volume_Ansible_collections",
                        "SCSI_id": "0", "host_id": "14",
                        "host_name": "host_ansible_collects",
                        "vdisk_UID": "6005076810CA0166C00000000000019F",
                        "IO_group_id": "0", "IO_group_name": "io_grp0",
                        "mapping_type": "private", "host_cluster_id": "",
                        "host_cluster_name": "", "protocol": "scsi"}]
        svc_obj_info_mock.return_value = mapping_ret
        host_mapping_data = IBMSVCvdiskhostmap().get_existing_vdiskhostmap()
        for host_mapping in host_mapping_data:
            self.assertEqual('volume_Ansible_collections', host_mapping['name'])
            self.assertEqual('0', host_mapping['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.vdiskhostmap_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_mapping_create_get_existing_vdiskhostmap_called(
            self, svc_authorize_mock, vdiskhostmap_probe_mock,
            get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'host': 'host4test',
        })
        host_mapping_created = IBMSVCvdiskhostmap()
        vdiskhostmap_probe_mock.return_value = []
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.vdiskhostmap_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_mapping_but_host_mapping_existed(
            self, svc_authorize_mock,
            vdiskhostmap_create_mock,
            get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'host': 'host4test',
        })
        host_mapping = {u'message': u'Virtual Disk to Host map, id [0], '
                                    u'successfully created', u'id': u'0'}
        vdiskhostmap_create_mock.return_value = host_mapping
        get_existing_vdiskhostmap_mock.return_value = []
        host_mapping_created = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.vdiskhostmap_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_mapping_successfully(self, svc_authorize_mock,
                                              vdiskhostmap_create_mock,
                                              get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'host': 'host4test',
        })
        host_mapping = {u'message': u'Virtual Disk to Host map, id [0], '
                                    u'successfully created', u'id': u'0'}
        vdiskhostmap_create_mock.return_value = host_mapping
        get_existing_vdiskhostmap_mock.return_value = []
        host_mapping_created = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_host_but_host_not_existed(self, svc_authorize_mock,
                                              get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'host': 'host4test',
        })
        get_existing_vdiskhostmap_mock.return_value = []
        host_mapping_deleted = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.vdiskhostmap_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_host_successfully(self, svc_authorize_mock,
                                      host_delete_mock,
                                      get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'host': 'host4test',
        })
        mapping_ret = [{"id": "0", "name": "volume_Ansible_collections",
                        "SCSI_id": "0", "host_id": "14",
                        "host_name": "host_ansible_collects",
                        "vdisk_UID": "6005076810CA0166C00000000000019F",
                        "IO_group_id": "0", "IO_group_name": "io_grp0",
                        "mapping_type": "private", "host_cluster_id": "",
                        "host_cluster_name": "", "protocol": "scsi"}]
        get_existing_vdiskhostmap_mock.return_value = mapping_ret
        host_mapping_deleted = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_deleted.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.vdiskhostclustermap_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_mapping_successfully(self, svc_authorize_mock,
                                                     vdiskhostclustermap_create_mock,
                                                     get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'hostcluster': 'hostcluster4test',
        })
        host_mapping = {u'message': u'Volume to Host Cluster map, id [0], '
                                    u'successfully created', u'id': u'0'}
        vdiskhostclustermap_create_mock.return_value = host_mapping
        get_existing_vdiskhostmap_mock.return_value = []
        host_mapping_created = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.vdiskhostclustermap_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_mapping_but_mapping_exist(
            self, svc_authorize_mock,
            vdiskhostclustermap_create_mock,
            get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'hostcluster': 'hostcluster4test',
        })
        host_mapping = {u'message': u'Volume to Host Cluster map, id [0], '
                                    u'successfully created', u'id': u'0'}
        vdiskhostclustermap_create_mock.return_value = host_mapping
        get_existing_vdiskhostmap_mock.return_value = []
        host_mapping_created = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_hostcluster_mapping_not_exist(self, svc_authorize_mock,
                                                  get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'hostcluster': 'hostcluster4test',
        })
        get_existing_vdiskhostmap_mock.return_value = []
        host_mapping_deleted = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.get_existing_vdiskhostmap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_vol_map.IBMSVCvdiskhostmap.vdiskhostclustermap_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_hostcluster_mapping_successfully(self, svc_authorize_mock,
                                                     host_delete_mock,
                                                     get_existing_vdiskhostmap_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'volname': 'volume0',
            'hostcluster': 'hostcluster4test',
        })
        mapping_ret = [{"id": "0", "name": "volume_Ansible_collections",
                        "SCSI_id": "0", "host_id": "",
                        "host_name": "",
                        "vdisk_UID": "6005076810CA0166C00000000000019F",
                        "IO_group_id": "0", "IO_group_name": "io_grp0",
                        "mapping_type": "private", "host_cluster_id": "1",
                        "host_cluster_name": "hostcluster4test", "protocol": "scsi"}]
        get_existing_vdiskhostmap_mock.return_value = mapping_ret
        host_mapping_deleted = IBMSVCvdiskhostmap()
        with pytest.raises(AnsibleExitJson) as exc:
            host_mapping_deleted.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_vdiskhostmap_mock.assert_called_with()


if __name__ == '__main__':
    unittest.main()
