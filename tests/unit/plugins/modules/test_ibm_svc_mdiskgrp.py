# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_mdiskgrp """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_mdiskgrp import IBMSVCmdiskgrp


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


class TestIBMSVCmdiskgrp(unittest.TestCase):
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
            IBMSVCmdiskgrp()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_pool(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_get_existing_pool',
        })
        pool_ret = {"id": "0", "name": "Pool_Ansible_collections",
                    "status": "online", "mdisk_count": "1", "vdisk_count": "1",
                    "capacity": "5.23TB", "extent_size": "1024",
                    "free_capacity": "5.23TB", "virtual_capacity": "4.00GB",
                    "used_capacity": "4.00GB", "real_capacity": "4.00GB",
                    "overallocation": "0", "warning": "0", "easy_tier": "on",
                    "easy_tier_status": "balanced",
                    "compression_active": "no",
                    "compression_virtual_capacity": "0.00MB",
                    "compression_compressed_capacity": "0.00MB",
                    "compression_uncompressed_capacity": "0.00MB",
                    "parent_mdisk_grp_id": "0",
                    "parent_mdisk_grp_name": "Pool_Ansible_collections",
                    "child_mdisk_grp_count": "0",
                    "child_mdisk_grp_capacity": "0.00MB", "type": "parent",
                    "encrypt": "no", "owner_type": "none", "owner_id": "",
                    "owner_name": "", "site_id": "", "site_name": "",
                    "data_reduction": "no",
                    "used_capacity_before_reduction": "0.00MB",
                    "used_capacity_after_reduction": "0.00MB",
                    "overhead_capacity": "0.00MB",
                    "deduplication_capacity_saving": "0.00MB",
                    "reclaimable_capacity": "0.00MB",
                    "easy_tier_fcm_over_allocation_max": "100%"}
        svc_obj_info_mock.return_value = pool_ret
        pool = IBMSVCmdiskgrp().mdiskgrp_exists()
        self.assertEqual('Pool_Ansible_collections', pool['name'])
        self.assertEqual('0', pool['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_create_get_existing_pool_called(self, svc_authorize_mock, get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
        })
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_create_with_provisioning_policy(self,
                                                  svc_authorize_mock,
                                                  svc_run_command_mock,
                                                  get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0',
            'ext': True
        })
        get_existing_pool_mock.return_value = {}
        svc_run_command_mock.return_value = {
            u'message': u'Storage pool, id [0], '
                        u'successfully created',
            u'id': u'0'
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_create_with_provisioning_policy_idempotency(self,
                                                              svc_authorize_mock,
                                                              svc_run_command_mock,
                                                              get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0',
            'ext': True
        })
        get_existing_pool_mock.return_value = {
            "id": "0",
            "name": "test_pool_create_get_existing_pool_called",
            "provisioning_policy_name": "pp0"
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_create_with_replicationpoollinkuid_failed(self,
                                                            svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0',
            'replicationpoollinkuid': '000000000000000100000123456789C4',
            'ext': True
        })
        message = 'Following parameters are required together: replicationpoollinkuid, replication_partner_clusterid'
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCmdiskgrp()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'], message)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_create_with_replicationpoollinkuid(self,
                                                     svc_authorize_mock,
                                                     svc_run_command_mock,
                                                     svc_obj_info_mock,
                                                     get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0',
            'replicationpoollinkuid': '000000000000000100000123456789C4',
            'replication_partner_clusterid': 'x.x.x.x',
            'ext': True
        })
        get_existing_pool_mock.return_value = {}
        svc_run_command_mock.return_value = {
            u'message': u'Storage pool, id [0], '
                        u'successfully created',
            u'id': u'0'
        }
        svc_obj_info_mock.return_value = {
            "id": "000002022A104B10",
            "partnership_index": "1"
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_create_with_replicationpoollinkuid_idempotency(self,
                                                                 svc_authorize_mock,
                                                                 svc_run_command_mock,
                                                                 svc_obj_info_mock,
                                                                 get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0',
            'replicationpoollinkuid': '000000000000000100000123456789C4',
            'replication_partner_clusterid': 'x.x.x.x',
            'ext': True
        })
        get_existing_pool_mock.return_value = {
            "id": 0,
            "name": "test_pool_create_get_existing_pool_called",
            "replication_pool_link_uid": "000000000000000100000123456789C4",
            "provisioning_policy_name": "pp0",
            "replication_pool_linked_systems_mask": "0000000000000000000000000000000000000000000000000000000000000010"
        }
        svc_run_command_mock.return_value = {
            u'message': u'Storage pool, id [0], '
                        u'successfully created',
            u'id': u'0'
        }
        svc_obj_info_mock.return_value = {
            "id": "000002022A104B10",
            "partnership_index": "1"
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_update_with_replicationpoollinkuid(self,
                                                     svc_authorize_mock,
                                                     svc_run_command_mock,
                                                     svc_obj_info_mock,
                                                     get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0',
            'replicationpoollinkuid': '000000000000000100000123456789C4',
            'replication_partner_clusterid': 'x.x.x.x',
            'ext': True
        })
        get_existing_pool_mock.return_value = {
            'id': 0,
            'name': 'test_pool_create_get_existing_pool_called',
            'replication_pool_link_uid': '000000000000000100000123456789C5',
            'replication_pool_linked_systems_mask': '0000000000000000000000000000000000000000000000000000000000000100',
            'provisioning_policy_name': ''
        }
        svc_run_command_mock.return_value = {
            u'message': u'Storage pool, id [0], '
                        u'successfully created',
            u'id': u'0'
        }
        svc_obj_info_mock.return_value = {
            "id": "000002022A104B10",
            "partnership_index": "1"
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_update_with_replicationpoollinkuid_idempotency(self,
                                                                 svc_authorize_mock,
                                                                 svc_run_command_mock,
                                                                 svc_obj_info_mock,
                                                                 get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0',
            'replicationpoollinkuid': '000000000000000100000123456789C5',
            'replication_partner_clusterid': 'x.x.x.x',
            'ext': True
        })
        get_existing_pool_mock.return_value = {
            'id': 0,
            'name': 'test_pool_create_get_existing_pool_called',
            'replication_pool_link_uid': '000000000000000100000123456789C5',
            'replication_pool_linked_systems_mask': '0000000000000000000000000000000000000000000000000000000000000010',
            'provisioning_policy_name': 'pp0'
        }
        svc_run_command_mock.return_value = {
            u'message': u'Storage pool, id [0], '
                        u'successfully created',
            u'id': u'0'
        }
        svc_obj_info_mock.return_value = {
            "id": "000002022A104B10",
            "partnership_index": "1"
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_pool_update_with_provisioning_policy(self,
                                                  svc_authorize_mock,
                                                  svc_run_command_mock,
                                                  get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'provisioningpolicy': 'pp0'
        })
        get_existing_pool_mock.return_value = {
            "id": "0",
            "name": "test_pool_create_get_existing_pool_called",
            "provisioning_policy_name": ""
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_discard_provisioning_policy_from_pool(self,
                                                   svc_authorize_mock,
                                                   svc_run_command_mock,
                                                   get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_pool_create_get_existing_pool_called',
            'noprovisioningpolicy': True
        })
        get_existing_pool_mock.return_value = {
            "id": "0",
            "name": "test_pool_create_get_existing_pool_called",
            "provisioning_policy_name": "pp0"
        }
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_pool_failed_since_missed_required_param(self,
                                                            svc_authorize_mock,
                                                            get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_pool',
        })
        get_existing_pool_mock.return_value = []
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleFailJson) as exc:
            pool_created.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_pool_but_pool_existed(self,
                                          svc_authorize_mock,
                                          pool_probe_mock,
                                          get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_pool',
        })
        pool_ret = {"id": "0", "name": "Pool_Ansible_collections",
                    "status": "online", "mdisk_count": "1",
                    "vdisk_count": "1",
                    "capacity": "5.23TB", "extent_size": "1024",
                    "free_capacity": "5.23TB", "virtual_capacity": "4.00GB",
                    "used_capacity": "4.00GB", "real_capacity": "4.00GB",
                    "overallocation": "0", "warning": "0", "easy_tier": "on",
                    "easy_tier_status": "balanced",
                    "compression_active": "no",
                    "compression_virtual_capacity": "0.00MB",
                    "compression_compressed_capacity": "0.00MB",
                    "compression_uncompressed_capacity": "0.00MB",
                    "parent_mdisk_grp_id": "0",
                    "parent_mdisk_grp_name": "Pool_Ansible_collections",
                    "child_mdisk_grp_count": "0",
                    "child_mdisk_grp_capacity": "0.00MB", "type": "parent",
                    "encrypt": "no", "owner_type": "none", "owner_id": "",
                    "owner_name": "", "site_id": "", "site_name": "",
                    "data_reduction": "no",
                    "used_capacity_before_reduction": "0.00MB",
                    "used_capacity_after_reduction": "0.00MB",
                    "overhead_capacity": "0.00MB",
                    "deduplication_capacity_saving": "0.00MB",
                    "reclaimable_capacity": "0.00MB",
                    "easy_tier_fcm_over_allocation_max": "100%"
                    }
        get_existing_pool_mock.return_value = pool_ret
        pool_probe_mock.return_value = []
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_pool_successfully(self,
                                      svc_authorize_mock,
                                      pool_create_mock,
                                      get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_pool',
            'datareduction': 'no',
            'easytier': 'auto',
            'encrypt': 'no',
            'ext': '1024',
        })
        pool = {u'message': u'Storage pool, id [0], '
                            u'successfully created', u'id': u'0'}
        pool_create_mock.return_value = pool
        get_existing_pool_mock.return_value = []
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_pool_failed_since_no_message_in_result(self,
                                                           svc_authorize_mock,
                                                           svc_run_command_mock,
                                                           get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_pool',
            'datareduction': 'no',
            'easytier': 'auto',
            'encrypt': 'no',
            'ext': '1024',
        })
        pool = {u'id': u'0'}
        svc_run_command_mock.return_value = pool
        get_existing_pool_mock.return_value = []
        pool_created = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleFailJson) as exc:
            pool_created.apply()
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_pool_but_pool_not_existed(self,
                                              svc_authorize_mock,
                                              get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_pool',
            'datareduction': 'no',
            'easytier': 'auto',
            'encrypt': 'no',
            'ext': '1024',
        })
        get_existing_pool_mock.return_value = []
        pool_deleted = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_mdiskgrp.IBMSVCmdiskgrp.mdiskgrp_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_pool_successfully(self,
                                      svc_authorize_mock,
                                      pool_delete_mock,
                                      get_existing_pool_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_pool',
        })
        pool_ret = {"id": "0", "name": "Pool_Ansible_collections",
                    "status": "online", "mdisk_count": "1",
                    "vdisk_count": "1",
                    "capacity": "5.23TB", "extent_size": "1024",
                    "free_capacity": "5.23TB", "virtual_capacity": "4.00GB",
                    "used_capacity": "4.00GB", "real_capacity": "4.00GB",
                    "overallocation": "0", "warning": "0", "easy_tier": "on",
                    "easy_tier_status": "balanced",
                    "compression_active": "no",
                    "compression_virtual_capacity": "0.00MB",
                    "compression_compressed_capacity": "0.00MB",
                    "compression_uncompressed_capacity": "0.00MB",
                    "parent_mdisk_grp_id": "0",
                    "parent_mdisk_grp_name": "Pool_Ansible_collections",
                    "child_mdisk_grp_count": "0",
                    "child_mdisk_grp_capacity": "0.00MB", "type": "parent",
                    "encrypt": "no", "owner_type": "none", "owner_id": "",
                    "owner_name": "", "site_id": "", "site_name": "",
                    "data_reduction": "no",
                    "used_capacity_before_reduction": "0.00MB",
                    "used_capacity_after_reduction": "0.00MB",
                    "overhead_capacity": "0.00MB",
                    "deduplication_capacity_saving": "0.00MB",
                    "reclaimable_capacity": "0.00MB",
                    "easy_tier_fcm_over_allocation_max": "100%"}
        get_existing_pool_mock.return_value = pool_ret
        pool_deleted = IBMSVCmdiskgrp()
        with pytest.raises(AnsibleExitJson) as exc:
            pool_deleted.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_pool_mock.assert_called_with()


if __name__ == '__main__':
    unittest.main()
