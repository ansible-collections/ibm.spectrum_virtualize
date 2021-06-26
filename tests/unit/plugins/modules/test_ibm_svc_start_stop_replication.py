# Copyright (C) 2020 IBM CORPORATION
# Author(s):
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_manage_replication """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_start_stop_replication import IBMSVCStartStopReplication


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


class TestIBMSVCStartStopReplication(unittest.TestCase):
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
            IBMSVCStartStopReplication()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true'
        })
        svc_run_command_mock.return_value = ''
        obj = IBMSVCStartStopReplication()
        return_data = obj.start()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_when_isgroup(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true',
            'isgroup': 'true'
        })
        svc_run_command_mock.return_value = ''
        obj = IBMSVCStartStopReplication()
        return_data = obj.start()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_rcrelationship(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true',
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.start()
        self.assertEqual('Failed to start the rcrelationship [test_name]', exc.value.args[0]['msg'])
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_starting_rcrelationship(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true',
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.start()
        self.assertEqual('Failed to start the rcrelationship [test_name]', exc.value.args[0]['msg'])
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_starting_when_isgroup(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true',
            'isgroup': 'true'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.start()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
            'clean': 'true'
        })
        svc_run_command_mock.return_value = ''
        obj = IBMSVCStartStopReplication()
        return_data = obj.stop()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_when_isgroup(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
            'isgroup': 'true'
        })
        svc_run_command_mock.return_value = ''
        obj = IBMSVCStartStopReplication()
        return_data = obj.stop()
        self.assertEqual(None, return_data)

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_stopping_rcrelationship(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.stop()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_stopping_when_isgroup(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
            'isgroup': 'true'
        })
        svc_run_command_mock.return_value = {}
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.stop()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_for_failure_with_activeactive(self, svc_authorize_mock, svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_replication.IBMSVCStartStopReplication.start')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_remotecopy(self, svc_authorize_mock, svc_run_command_mock, start_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true'
        })
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_replication.IBMSVCStartStopReplication.start')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_remotecopy_when_isgroup(self, svc_authorize_mock, svc_run_command_mock, start_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'started',
            'clean': 'true',
            'isgroup': 'true'
        })
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_replication.IBMSVCStartStopReplication.stop')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_remotecopy(self, svc_authorize_mock, svc_run_command_mock, start_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
        })
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_replication.IBMSVCStartStopReplication.stop')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_remotecopy_when_isgroup(self, svc_authorize_mock, svc_run_command_mock, start_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'stopped',
            'clean': 'true',
            'isgroup': 'true'
        })
        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_start_stop_replication.IBMSVCStartStopReplication.stop')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_for_failure_with_unsupported_state(self, svc_authorize_mock, svc_run_command_mock, start_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_name',
            'state': 'wrong_state',
            'clean': 'true',
        })
        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCStartStopReplication()
            obj.apply()
        self.assertEqual(True, exc.value.args[0]["failed"])


if __name__ == '__main__':
    unittest.main()
