# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_info """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_info import IBMSVCGatherInfo


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


class TestIBMSVCGatherInfo(unittest.TestCase):
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
            IBMSVCGatherInfo()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_hosts_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_host_list_called(self, mock_svc_authorize,
                                  get_hosts_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host',
        })
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_hosts_list_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_pools_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_volumes_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_hosts_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_pool_vol_host_list_called(self, mock_svc_authorize,
                                           get_hosts_list_mock,
                                           get_volumes_list_mock,
                                           get_pools_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'pool,host,vol',
        })
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
            get_hosts_list_mock.assert_called_with()
            get_pools_list_mock.assert_called_with()
            get_volumes_list_mock.assert_called_with()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_host_result_by_gather_info(self, svc_authorize_mock,
                                            svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
        svc_obj_info_mock.return_value = host_ret
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['Host'][0], host_ret[0])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_host_and_vol_result_by_gather_info(self, svc_authorize_mock,
                                                    svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host,vol',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
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
        svc_obj_info_mock.side_effect = [vol_ret, host_ret]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['Host'][0], host_ret[0])
        self.assertDictEqual(exc.value.args[0]['Volume'][0], vol_ret[0])


if __name__ == '__main__':
    unittest.main()
