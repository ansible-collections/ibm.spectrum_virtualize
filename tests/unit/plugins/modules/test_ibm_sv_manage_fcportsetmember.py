# Copyright (C) 2023 IBM CORPORATION
# Author(s): Sudheesh Reddy Satti<Sudheesh.Reddy.Satti@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_sv_manage_fcportsetmember """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_sv_manage_fcportsetmember import \
    IBMSVFCPortsetmember


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


class TestIBMSVFCPortsetmember(unittest.TestCase):
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

    def test_module_with_blank_values(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVFCPortsetmember()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_case(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': "",
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVFCPortsetmember()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_fcportsetmember.IBMSVFCPortsetmember.add_fcportsetmember')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmemeber(self,
                                  svc_authorize_mock,
                                  add_fcportsetmember_mock,
                                  svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'present'
        })
        add_fcportsetmember = IBMSVFCPortsetmember()

        with pytest.raises(AnsibleExitJson) as exc:
            add_fcportsetmember.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember_idempotency(self,
                                             svc_authorize_mock,
                                             svc_run_command_mock,
                                             svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '3',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "id": "4",
            "fc_io_port_id": "1",
            "portset_id": "3",
            "portset_name": "portset0",
            "owner_id": "",
            "owner_name": ""
        }
        p = IBMSVFCPortsetmember()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_fcportsetmember.IBMSVFCPortsetmember.remove_fcportsetmember')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_fcportsetmemeber(self,
                                     svc_authorize_mock,
                                     add_fcportsetmember_mock,
                                     svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'absent'
        })
        remove_fcportsetmember = IBMSVFCPortsetmember()

        with pytest.raises(AnsibleExitJson) as exc:
            remove_fcportsetmember.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_sv_manage_fcportsetmember.IBMSVFCPortsetmember.is_fcportsetmember_exists')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_portset_idempotency(self, svc_authorize_mock,
                                        svc_run_command_mock,
                                        fcportsetmember_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '3',
            'state': 'absent'
        })

        fcportsetmember_exist_mock.return_value = {}
        p = IBMSVFCPortsetmember()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
