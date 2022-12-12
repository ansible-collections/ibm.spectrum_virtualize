# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_manage_awss3_cloudaccount """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_manage_awss3_cloudaccount import IBMSVAWSS3


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


class TestIBMSVAWSS3(unittest.TestCase):
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

    def test_missing_state_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVAWSS3()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_mandatory_parameter_validation(self, svc_authorize_mock,
                                            svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {}

        with pytest.raises(AnsibleFailJson) as exc:
            aws = IBMSVAWSS3()
            aws.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_aws_acc_create(self, svc_authorize_mock,
                            svc_obj_info_mock,
                            svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'bucketprefix': 'ansible',
            'accesskeyid': 's3access',
            'secretaccesskey': 'saldhsalhdljsah',
            'upbandwidthmbits': 20,
            'downbandwidthmbits': 20,
            'region': 'us-east',
            'encrypt': 'no',
            'state': 'present'
        })

        aws = IBMSVAWSS3()
        svc_obj_info_mock.return_value = {}

        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_aws_acc_create_idempotency(self, svc_authorize_mock,
                                        svc_obj_info_mock,
                                        svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'bucketprefix': 'ansible',
            'accesskeyid': 's3access',
            'secretaccesskey': 'saldhsalhdljsah',
            'upbandwidthmbits': 20,
            'downbandwidthmbits': 20,
            'region': 'us-east',
            'encrypt': 'no',
            'state': 'present'
        })

        aws = IBMSVAWSS3()
        svc_obj_info_mock.return_value = {
            "id": "0",
            "name": "awss3acc",
            "type": "awss3",
            "status": "online",
            "mode": "normal",
            "active_volume_count": "1",
            "backup_volume_count": "1",
            "import_system_id": "",
            "import_system_name": "",
            "error_sequence_number": "",
            "refreshing": "no",
            "up_bandwidth_mbits": "20",
            "down_bandwidth_mbits": "20",
            "backup_timestamp": "221007111148",
            "encrypt": "no",
            "certificate": "yes",
            "certificate_expiry": "",
            "endpoint": "",
            "awss3_bucket_prefix": "ansible",
            "awss3_access_key_id": "s3access",
            "awss3_region": "us-east",
            "swift_keystone": "no",
            "swift_container_prefix": "",
            "swift_tenant_name": "",
            "swift_user_name": ""
        }

        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_awss3_cloudaccount.IBMSVAWSS3.is_aws_account_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_aws_account(self,
                                svc_authorize_mock,
                                svc_run_command_mock,
                                aws_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3_new',
            'old_name': 'awss3acc',
            'accesskeyid': 'newaccess',
            'secretaccesskey': 'saldhsalhdljsah',
            'upbandwidthmbits': 10,
            'downbandwidthmbits': 10,
            'state': 'present'
        })

        aws_exists_mock.side_effect = iter([
            {
                "id": "0",
                "name": "awss3acc",
                "up_bandwidth_mbits": "20",
                "down_bandwidth_mbits": "20",
                "awss3_access_key_id": "s3access"
            },
            {},
            {
                "id": "0",
                "name": "awss3acc",
                "up_bandwidth_mbits": "20",
                "down_bandwidth_mbits": "20",
                "awss3_access_key_id": "s3access"
            }
        ])

        aws = IBMSVAWSS3()
        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        svc_run_command_mock.assert_called_with(
            'chcloudaccountawss3',
            {
                'secretaccesskey': 'saldhsalhdljsah',
                'downbandwidthmbits': '10',
                'upbandwidthmbits': '10',
                'name': 'awss3_new',
                'accesskeyid': 'newaccess',
            },
            cmdargs=['awss3acc'],
            timeout=20
        )
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_awss3_cloudaccount.IBMSVAWSS3.is_aws_account_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_aws_account_idempotency(self,
                                            svc_authorize_mock,
                                            svc_run_command_mock,
                                            aws_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3_new',
            'old_name': 'awss3acc',
            'accesskeyid': 'newaccess',
            'secretaccesskey': 'saldhsalhdljsah',
            'upbandwidthmbits': 10,
            'downbandwidthmbits': 10,
            'state': 'present'
        })

        aws_exists_mock.side_effect = iter([
            {},
            {
                "id": "0",
                "name": "awss3_new",
                "up_bandwidth_mbits": "20",
                "down_bandwidth_mbits": "20",
                "awss3_access_key_id": "s3access"
            },
            {}
        ])
        aws = IBMSVAWSS3()

        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_aws_acc_update(self, svc_authorize_mock,
                            svc_obj_info_mock,
                            svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'accesskeyid': 'newaccess',
            'secretaccesskey': 'saldhsalhdljsah',
            'upbandwidthmbits': 10,
            'downbandwidthmbits': 10,
            'state': 'present'
        })

        aws = IBMSVAWSS3()
        svc_obj_info_mock.return_value = {
            "id": "0",
            "name": "awss3acc",
            "type": "awss3",
            "status": "online",
            "mode": "normal",
            "active_volume_count": "1",
            "backup_volume_count": "1",
            "import_system_id": "",
            "import_system_name": "",
            "error_sequence_number": "",
            "refreshing": "no",
            "up_bandwidth_mbits": "20",
            "down_bandwidth_mbits": "20",
            "backup_timestamp": "221007111148",
            "encrypt": "no",
            "certificate": "yes",
            "certificate_expiry": "",
            "endpoint": "",
            "awss3_bucket_prefix": "ansible",
            "awss3_access_key_id": "s3access",
            "awss3_region": "us-east",
            "swift_keystone": "no",
            "swift_container_prefix": "",
            "swift_tenant_name": "",
            "swift_user_name": ""
        }

        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_aws_acc_update_idempotency(self, svc_authorize_mock,
                                        svc_obj_info_mock,
                                        svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'accesskeyid': 'newaccess',
            'secretaccesskey': 'saldhsalhdljsah',
            'upbandwidthmbits': 10,
            'downbandwidthmbits': 10,
            'state': 'present'
        })

        aws = IBMSVAWSS3()
        svc_obj_info_mock.return_value = {
            "id": "0",
            "name": "awss3acc",
            "type": "awss3",
            "status": "online",
            "mode": "normal",
            "active_volume_count": "1",
            "backup_volume_count": "1",
            "import_system_id": "",
            "import_system_name": "",
            "error_sequence_number": "",
            "refreshing": "no",
            "up_bandwidth_mbits": "10",
            "down_bandwidth_mbits": "10",
            "backup_timestamp": "221007111148",
            "encrypt": "no",
            "certificate": "no",
            "certificate_expiry": "",
            "endpoint": "",
            "awss3_bucket_prefix": "ansible",
            "awss3_access_key_id": "newaccess",
            "awss3_region": "us-west",
            "swift_keystone": "no",
            "swift_container_prefix": "",
            "swift_tenant_name": "",
            "swift_user_name": ""
        }

        with pytest.raises(AnsibleExitJson) as exc:
            aws.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_accesskey_without_secretkey(self, svc_authorize_mock,
                                                svc_obj_info_mock,
                                                svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'accesskeyid': 'newaccess',
            'upbandwidthmbits': 10,
            'downbandwidthmbits': 10,
            'region': 'us-west',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "id": "0",
            "name": "awss3acc",
            "type": "awss3",
            "status": "online",
            "mode": "normal",
            "active_volume_count": "1",
            "backup_volume_count": "1",
            "import_system_id": "",
            "import_system_name": "",
            "error_sequence_number": "",
            "refreshing": "no",
            "up_bandwidth_mbits": "20",
            "down_bandwidth_mbits": "20",
            "backup_timestamp": "221007111148",
            "encrypt": "no",
            "certificate": "yes",
            "certificate_expiry": "",
            "endpoint": "",
            "awss3_bucket_prefix": "ansible",
            "awss3_access_key_id": "s3access",
            "awss3_region": "us-east",
            "swift_keystone": "no",
            "swift_container_prefix": "",
            "swift_tenant_name": "",
            "swift_user_name": ""
        }

        with pytest.raises(AnsibleFailJson) as exc:
            aws = IBMSVAWSS3()
            aws.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_aws_account_validation(self, svc_authorize_mock,
                                           svc_obj_info_mock,
                                           svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'accesskeyid': 'newaccess',
            'upbandwidthmbits': 10,
            'downbandwidthmbits': 10,
            'region': 'us-west',
            'state': 'absent'
        })

        svc_obj_info_mock.return_value = {
            "id": "0",
            "name": "awss3acc",
            "type": "awss3",
            "status": "online",
            "mode": "normal",
            "active_volume_count": "1",
            "backup_volume_count": "1",
            "import_system_id": "",
            "import_system_name": "",
            "error_sequence_number": "",
            "refreshing": "no",
            "up_bandwidth_mbits": "20",
            "down_bandwidth_mbits": "20",
            "backup_timestamp": "221007111148",
            "encrypt": "no",
            "certificate": "yes",
            "certificate_expiry": "",
            "endpoint": "",
            "awss3_bucket_prefix": "ansible",
            "awss3_access_key_id": "s3access",
            "awss3_region": "us-east",
            "swift_keystone": "no",
            "swift_container_prefix": "",
            "swift_tenant_name": "",
            "swift_user_name": ""
        }

        with pytest.raises(AnsibleFailJson) as exc:
            aws = IBMSVAWSS3()
            aws.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_aws_account(self, svc_authorize_mock,
                                svc_obj_info_mock,
                                svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'state': 'absent'
        })

        svc_obj_info_mock.return_value = {
            "id": "0",
            "name": "awss3acc",
            "type": "awss3",
            "status": "online",
            "mode": "normal",
            "active_volume_count": "1",
            "backup_volume_count": "1",
            "import_system_id": "",
            "import_system_name": "",
            "error_sequence_number": "",
            "refreshing": "no",
            "up_bandwidth_mbits": "20",
            "down_bandwidth_mbits": "20",
            "backup_timestamp": "221007111148",
            "encrypt": "no",
            "certificate": "yes",
            "certificate_expiry": "",
            "endpoint": "",
            "awss3_bucket_prefix": "ansible",
            "awss3_access_key_id": "s3access",
            "awss3_region": "us-east",
            "swift_keystone": "no",
            "swift_container_prefix": "",
            "swift_tenant_name": "",
            "swift_user_name": ""
        }

        with pytest.raises(AnsibleExitJson) as exc:
            aws = IBMSVAWSS3()
            aws.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_aws_account_idempotency(self, svc_authorize_mock,
                                            svc_obj_info_mock,
                                            svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'awss3acc',
            'state': 'absent'
        })

        svc_obj_info_mock.return_value = {}

        with pytest.raises(AnsibleExitJson) as exc:
            aws = IBMSVAWSS3()
            aws.apply()
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
