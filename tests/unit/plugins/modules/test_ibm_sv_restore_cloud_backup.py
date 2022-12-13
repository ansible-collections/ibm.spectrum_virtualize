# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_restore_cloud_backup """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_restore_cloud_backup import IBMSVRestoreCloudBackup


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


class TestIBMSVRestoreCloudBackup(unittest.TestCase):
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

    def test_missing_mandatory_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVRestoreCloudBackup()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_cancel_with_invalid_parameters(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cancel': 'true',
            'source_volume_uid': '83094832040980',
            'generation': 1,
            'target_volume_name': 'vol1'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVRestoreCloudBackup()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_restore_volume(self, svc_authorize_mock,
                            svc_obj_info_mock,
                            svc_token_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'source_volume_uid': '83094832040980',
            'generation': 1,
            'target_volume_name': 'vol1'
        })

        svc_obj_info_mock.return_value = {'id': 1, 'name': 'volume_backup'}
        svc_token_mock.return_value = {'out': ''}
        with pytest.raises(AnsibleExitJson) as exc:
            aws = IBMSVRestoreCloudBackup()
            aws.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_restore_volume_idempotency(self, svc_authorize_mock,
                                        svc_obj_info_mock,
                                        svc_token_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'source_volume_uid': '83094832040980',
            'generation': 1,
            'target_volume_name': 'vol1'
        })

        aws = IBMSVRestoreCloudBackup()
        svc_obj_info_mock.return_value = {'id': 1, 'name': 'volume_backup'}
        svc_token_mock.return_value = {'out': b'CMMVC9103E'}

        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_cancel_restore(self, svc_authorize_mock,
                            svc_obj_info_mock,
                            svc_token_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cancel': True,
            'target_volume_name': 'vol1'
        })

        aws = IBMSVRestoreCloudBackup()
        svc_obj_info_mock.return_value = {'id': 1, 'name': 'vol1', 'restore_status': 'restoring'}
        svc_token_mock.return_value = {'out': ''}
        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_cancel_restore_idempotency(self, svc_authorize_mock,
                                        svc_obj_info_mock,
                                        svc_token_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'cancel': True,
            'target_volume_name': 'vol1'
        })

        aws = IBMSVRestoreCloudBackup()
        svc_obj_info_mock.return_value = {'id': 1, 'name': 'vol1', 'restore_status': 'available'}
        svc_token_mock.return_value = {'out': ''}
        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
