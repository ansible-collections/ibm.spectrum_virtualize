# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_consistgrp_flashcopy """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_manage_consistgrp_flashcopy import IBMSVCFlashcopyConsistgrp


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation """
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


class TestIBMSVCFlashcopyConsistgrp(unittest.TestCase):
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
            IBMSVCFlashcopyConsistgrp()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_fcconsistgrp(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        svc_obj_info_mock.return_value = {
            "id": "3", "name": "test_name", "status": "empty",
            "autodelete": "off", "start_time": "",
            "owner_id": "", "owner_name": "ownershipgroup_name"
        }
        obj = IBMSVCFlashcopyConsistgrp()
        data = obj.get_existing_fcconsistgrp()
        self.assertEqual("test_name", data["name"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcconsistgrp_create(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        svc_run_command_mock.return_value = {
            'id': '4',
            'message': 'FlashCopy Consistency Group, id [4], successfully created'
        }
        obj = IBMSVCFlashcopyConsistgrp()
        data = obj.fcconsistgrp_create()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcconsistgrp_delete(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
        })
        svc_run_command_mock.return_value = None
        obj = IBMSVCFlashcopyConsistgrp()
        data = obj.fcconsistgrp_delete()
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcconsistgrp_probe(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        modify_arg = {
            "id": "3", "name": "test_name", "status": "empty",
            "autodelete": "off", "start_time": "",
            "owner_id": "", "owner_name": "ownershipgroup_name_old"
        }
        obj = IBMSVCFlashcopyConsistgrp()
        data = obj.fcconsistgrp_probe(modify_arg)
        self.assertIn('ownershipgroup', data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcconsistgrp_probe_noconsistgrp(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'noownershipgroup': True
        })
        modify_arg = {
            "id": "3", "name": "test_name", "status": "empty",
            "autodelete": "off", "start_time": "",
            "owner_id": "", "owner_name": "ownershipgroup_name"
        }
        obj = IBMSVCFlashcopyConsistgrp()
        data = obj.fcconsistgrp_probe(modify_arg)
        self.assertIn('noownershipgroup', data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcconsistgrp_update(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        modify_arg = {
            'ownershipgroup': 'ownershipgroup_name',
        }
        obj = IBMSVCFlashcopyConsistgrp()
        data = obj.fcconsistgrp_update(modify_arg)
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcconsistgrp_update_noconsistgrp(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        modify_arg = {
            'noownershipgroup': True,
        }
        obj = IBMSVCFlashcopyConsistgrp()
        data = obj.fcconsistgrp_update(modify_arg)
        self.assertEqual(None, data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.fcconsistgrp_create')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.get_existing_fcconsistgrp')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_nonexisting_fcconsisgrp(self, svc_authorize_mock, svc_run_command_mock, gef, fc):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        gef.return_value = {}
        fc.return_value = {
            'id': '4',
            'message': 'FlashCopy Consistency Group, id [4], successfully created'
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyConsistgrp()
            obj.apply()

        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.get_existing_fcconsistgrp')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_existing_fcconsisgrp(self, svc_authorize_mock, svc_run_command_mock, gef):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        gef.return_value = {
            "id": "3", "name": "test_name", "status": "empty",
            "autodelete": "off", "start_time": "",
            "owner_id": "", "owner_name": "ownershipgroup_name"
        }
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyConsistgrp()
            obj.apply()

        self.assertEqual(False, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.fcconsistgrp_update')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.get_existing_fcconsistgrp')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_updating_existing_fcconsisgrp(self, svc_authorize_mock, svc_run_command_mock, gef, fu):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        })
        gef.return_value = {
            "id": "3", "name": "test_name", "status": "empty",
            "autodelete": "off", "start_time": "",
            "owner_id": "", "owner_name": "ownershipgroup_name_old"
        }
        fu.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyConsistgrp()
            obj.apply()

        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.fcconsistgrp_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.get_existing_fcconsistgrp')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_deleting_existing_fcconsisgrp(self, svc_authorize_mock, svc_run_command_mock, gef, fd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
        })
        gef.return_value = {
            "id": "3", "name": "test_name", "status": "empty",
            "autodelete": "off", "start_time": "",
            "owner_id": "", "owner_name": "ownershipgroup_name"
        }
        fd.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyConsistgrp()
            obj.apply()

        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.fcconsistgrp_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.get_existing_fcconsistgrp')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_deleting_existing_fcconsisgrp_with_force(self, svc_authorize_mock, svc_run_command_mock, gef, fd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
            'force': True
        })
        gef.return_value = {
            "id": "3", "name": "test_name", "status": "empty",
            "autodelete": "off", "start_time": "",
            "owner_id": "", "owner_name": "ownershipgroup_name"
        }
        fd.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyConsistgrp()
            obj.apply()

        self.assertEqual(True, exc.value.args[0]["changed"])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.fcconsistgrp_delete')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_manage_consistgrp_flashcopy.IBMSVCFlashcopyConsistgrp.get_existing_fcconsistgrp')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_deleting_nonexisting_fcconsisgrp(self, svc_authorize_mock, svc_run_command_mock, gef, fd):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'absent',
        })
        gef.return_value = {}
        fd.return_value = None
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCFlashcopyConsistgrp()
            obj.apply()

        self.assertEqual(False, exc.value.args[0]['changed'])


if __name__ == "__main__":
    unittest.main()
