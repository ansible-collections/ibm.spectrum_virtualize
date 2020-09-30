# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_fcconsistgrp """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_fcconsistgrp import IBMSVCFCCG


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


class TestIBMSVCFCCG(unittest.TestCase):
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
            IBMSVCFCCG()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_fccg(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_get_existing_fccg',
        })
        fccg_ret = [{"id": "0", "name": "fccg4test", "status": "empty",
                     "start_time": "", "owner_id": "", "owner_name": ""}]
        svc_obj_info_mock.return_value = fccg_ret
        fccg = IBMSVCFCCG().get_existing_fccg()
        self.assertEqual('fccg4test', fccg['name'])
        self.assertEqual('0', fccg['id'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.get_existing_fccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fccg_create_get_existing_fccg_called(self, svc_authorize_mock,
                                                  get_existing_fccg_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_fccg_create_get_existing_fccg_called',
        })
        fccg_created = IBMSVCFCCG()
        with pytest.raises(AnsibleFailJson) as exc:
            fccg_created.apply()
        get_existing_fccg_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.get_existing_fccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.fccg_probe')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fccg_but_fccg_existed(self, svc_authorize_mock,
                                          fccg_probe_mock,
                                          get_existing_fccg_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_fccg',
        })
        fccg_ret = [{"id": "1", "name": "fccstgrp0", "status": "empty",
                     "start_time": "", "owner_id": "", "owner_name": ""}]
        get_existing_fccg_mock.return_value = fccg_ret
        fccg_probe_mock.return_value = []
        host_created = IBMSVCFCCG()
        with pytest.raises(AnsibleExitJson) as exc:
            host_created.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_fccg_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.get_existing_fccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.fccg_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fccg_successfully(self, svc_authorize_mock,
                                      fccg_create_mock,
                                      get_existing_fccg_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_create_fccg_successfully',
        })
        fccg = {u'message': u'FlashCopy Consistency Group, id [35], '
                            u'successfully created', u'id': u'35'}
        fccg_create_mock.return_value = fccg
        get_existing_fccg_mock.return_value = []
        fccg_created = IBMSVCFCCG()
        with pytest.raises(AnsibleExitJson) as exc:
            fccg_created.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_fccg_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.get_existing_fccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fccg_failed_since_missed_required_param(
            self, svc_authorize_mock, get_existing_fccg_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
        })
        get_existing_fccg_mock.return_value = []
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVCFCCG()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.get_existing_fccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_flashcopymap_probe(self, svc_authorize_mock,
                                get_existing_fccg_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'fccg4test',
            'autodelete': 'on'
        })
        fccg_ret = {'id': '1', 'name': 'fccg4test', 'status': 'empty',
                    'autodelete': 'off', 'start_time': '', 'owner_id': '',
                    'owner_name': ''}
        get_existing_fccg_mock.return_value = fccg_ret
        ret = IBMSVCFCCG().fccg_probe(fccg_ret)
        self.assertTrue(ret['autodelete'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.get_existing_fccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_fccg_but_fccg_not_existed(self, svc_authorize_mock,
                                              get_existing_fccg_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_delete_fccg_but_fccg_not_existed',
        })
        get_existing_fccg_mock.return_value = []
        host_deleted = IBMSVCFCCG()
        with pytest.raises(AnsibleExitJson) as exc:
            host_deleted.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_existing_fccg_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.get_existing_fccg')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_fcconsistgrp.IBMSVCFCCG.fccg_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_fccg_successfully(self, svc_authorize_mock,
                                      fccg_delete_mock,
                                      get_existing_fccg_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'test_delete_fccg_successfully',
        })
        fccg_ret = [{"id": "1", "name": "fccstgrp0", "status": "empty",
                     "start_time": "", "owner_id": "", "owner_name": ""}]
        get_existing_fccg_mock.return_value = fccg_ret
        host_deleted = IBMSVCFCCG()
        with pytest.raises(AnsibleExitJson) as exc:
            host_deleted.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        get_existing_fccg_mock.assert_called_with()


if __name__ == '__main__':
    unittest.main()
