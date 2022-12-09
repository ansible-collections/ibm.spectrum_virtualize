# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module_utils: ibm_svc_utils """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi


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


class TestIBMSVModuleUtils(unittest.TestCase):
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
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
        })

    def test_return_port_and_protocol(self):
        self.assertEqual(self.restapi.port, '7443')
        self.assertEqual(self.restapi.protocol, 'https')

    def test_return_resturl(self):
        resturl = 'https://1.2.3.4.domain.ibm.com:7443/rest'
        self.assertEqual(self.restapi.resturl, resturl)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible.module_utils.basic.AnsibleModule')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    def test_svc_rest_with_module(self, mock_svc_token_wrap, mock_module,
                                  mock_svc_authorize):
        PARAMS_FOR_PRESENT = {
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password'
        }
        mock_module.params = PARAMS_FOR_PRESENT
        mock_module.return_value = mock_module
        mock_svc_token_wrap.return_value = {'err': 'err', 'out': []}
        self.restapi = IBMSVCRestApi(mock_module, '1.2.3.4',
                                     'domain.ibm.com', 'username', 'password',
                                     False, 'test.log', '')

        self.restapi.svc_run_command('lshost', {}, [])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    def test_svc_run_command_successfully(self, mock_svc_token_wrap):
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
        mock_svc_token_wrap.return_value = {'err': '', 'out': host_ret}
        ret = self.restapi.svc_run_command('lshost', {}, [])
        mock_svc_token_wrap.assert_called_with('lshost', {}, [], 10)
        self.assertDictEqual(ret[0], host_ret[0])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    def test_svc_obj_info_return_none(self, mock_svc_token_wrap):
        mock_svc_token_wrap.return_value = {'code': 500}
        self.assertEqual(None, self.restapi.svc_obj_info('lshost', {}, []))

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    def test_svc_obj_info_successfully(self, mock_svc_token_wrap):
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
        mock_svc_token_wrap.return_value = {'out': host_ret, 'code': 1,
                                            'err': ''}
        ret = self.restapi.svc_obj_info('lshost', {}, [])
        self.assertDictEqual(ret[0], host_ret[0])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    def test_get_auth_token(self, mock_svc_token_wrap, mock_svc_authorize):
        test_var = 'a2ca1d31d663ce181b955c07f51a000c2f75835b3d87735d1f334cf4b913880c'
        mock_svc_authorize.return_value = test_var
        ret = self.restapi.get_auth_token()
        self.assertEqual(test_var, ret)


if __name__ == '__main__':
    unittest.main()
