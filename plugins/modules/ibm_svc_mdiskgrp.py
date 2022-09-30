#!/usr/bin/python
# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sanjaikumaar M <sanjaikumaar.m@ibm.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_svc_mdiskgrp
short_description: This module manages pools on IBM Spectrum Virtualize family storage systems
description:
  - Ansible interface to manage 'mkmdiskgrp' and 'rmmdiskgrp' pool commands.
version_added: "1.0.0"
options:
  name:
    description:
      - Specifies the name to assign to the new pool.
    required: true
    type: str
  state:
    description:
      - Creates (C(present)) or removes (C(absent)) an MDisk group.
    choices: [ absent, present ]
    required: true
    type: str
  clustername:
    description:
    - The hostname or management IP of the Spectrum Virtualize storage system.
    type: str
    required: true
  domain:
    description:
    - Domain for the Spectrum Virtualize storage system.
    - Valid when hostname is used for the parameter I(clustername).
    type: str
  username:
    description:
    - REST API username for the Spectrum Virtualize storage system.
    - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
    type: str
  password:
    description:
    - REST API password for the Spectrum Virtualize storage system.
    - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
    type: str
  token:
    description:
    - The authentication token to verify a user on the Spectrum Virtualize storage system.
    - To generate a token, use the M(ibm.spectrum_virtualize.ibm_svc_auth) module.
    type: str
    version_added: '1.5.0'
  datareduction:
    description:
    - Defines use of data reduction pools (DRPs) on the MDisk group.
    - Applies when I(state=present), to create a pool.
    type: str
    default: 'no'
    choices: ['yes', 'no']
  easytier:
    description:
    - Defines use of easytier with the MDisk group.
    - Applies when I(state=present), to create a pool.
    type: str
    default: 'off'
    choices: ['on', 'off', 'auto']
  encrypt:
    description:
    - Defines use of encryption with the MDisk group.
    - Applies when I(state=present), to create a pool.
    type: str
    default: 'no'
    choices: ['yes', 'no']
  ext:
    description:
    - Specifies the size of the extents for this group in MB.
    - Applies when I(state=present), to create a pool.
    type: int
  log_path:
    description:
    - Path of debug log file.
    type: str
  validate_certs:
    description:
      - Validates certification.
    default: false
    type: bool
  parentmdiskgrp:
    description:
      - Parentmdiskgrp for subpool.
      - Applies when I(state=present), to create a pool.
    type: str
  safeguarded:
    description:
      - Specify to create a safeguarded child pool.
      - Applicable only during child pool creation.
    type: bool
    version_added: 1.8.0
  noquota:
    description:
      - Specify to create a data reduction child pool.
      - I(noquota) and I(size) parameters are mutually exclusive.
      - I(noquota) parameter must be used with I(datareduction) set to yes to create a data reduction child pool.
      - I(noquota) parameter must be used with I(parentmdiskgrp) in a parent data reduction storage pool.
    type: bool
    version_added: 1.8.0
  unit:
    description:
      - Unit for subpool.
      - Applies when I(state=present), to create a pool.
    type: str
  provisioningpolicy:
    description:
      - Specify the name of the provisioning policy to map it with the pool.
      - Applies, when I(state=present).
    type: str
    version_added: 1.10.0
  noprovisioningpolicy:
    description:
      - Specify to unmap provisioning policy from the pool.
      - Applies, when I(state=present) to modify an existing pool.
    type: bool
    version_added: 1.10.0
  replicationpoollinkuid:
    description:
      - Specifies the replication pool unique identifier which should be same as the pool that present in the replication server.
      - Applies, when I(state=present).
      - Supported in SV build 8.5.2.1 or later.
    type: str
    version_added: 1.10.0
  resetreplicationpoollinkuid:
    description:
      - If set, any links between this pool on local system and pools on remote systems will be removed.
      - Applies, when I(state=present) to modify an existing pool.
      - Supported in SV build 8.5.2.1 or later.
    type: bool
    version_added: 1.10.0
  replication_partner_clusterid:
    description:
      - Specifies the id or name of the partner cluster which will be used for replication.
      - Applies, when I(state=present).
      - Supported in SV build 8.5.2.1 or later.
    type: str
    version_added: 1.10.0
  size:
    description:
      - Specifies the child pool capacity. The value must be
        a numeric value (and an integer multiple of the extent size).
      - Applies when I(state=present), to create a pool.
    type: int
author:
    - Peng Wang(@wangpww)
    - Sanjaikumaar M (@sanjaikumaar)
notes:
    - This module supports C(check_mode).
'''
EXAMPLES = '''
- name: Create mdisk group
  ibm.spectrum_virtualize.ibm_svc_mdiskgrp:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    name: pool1
    provisioningpolicy: pp0
    replicationpoollinkuid: 000000000000000
    replication_partner_clusterid: 000000000032432342
    state: present
    datareduction: no
    easytier: auto
    encrypt: no
    ext: 1024
- name: Create a safeguarded backup location
  ibm.spectrum_virtualize.ibm_svc_mdiskgrp:
    clustername: "{{clustername}}"
    token: "{{results.token}}"
    log_path: "{{log_path}}"
    parentmdiskgrp: Pool1
    name: Pool1child1
    datareduction: 'yes'
    safeguarded: True
    ext: 1024
    noquota: True
    state: present
- name: Delete mdisk group
  ibm.spectrum_virtualize.ibm_svc_mdiskgrp:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    name: pool1
    state: absent
- name: Delete a safeguarded backup location
  ibm.spectrum_virtualize.ibm_svc_mdiskgrp:
    clustername: "{{clustername}}"
    token: "{{results.token}}"
    log_path: "{{log_path}}"
    parentmdiskgrp: Pool1
    name: Pool1child1
    state: absent
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger


class IBMSVCmdiskgrp(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent',
                                                               'present']),
                datareduction=dict(type='str', default='no', choices=['yes',
                                                                      'no']),
                easytier=dict(type='str', default='off', choices=['on', 'off',
                                                                  'auto']),
                encrypt=dict(type='str', default='no', choices=['yes', 'no']),
                ext=dict(type='int'),
                parentmdiskgrp=dict(type='str'),
                safeguarded=dict(type='bool'),
                noquota=dict(type='bool'),
                size=dict(type='int'),
                unit=dict(type='str'),
                provisioningpolicy=dict(type='str'),
                noprovisioningpolicy=dict(type='bool'),
                replicationpoollinkuid=dict(type='str'),
                resetreplicationpoollinkuid=dict(type='bool'),
                replication_partner_clusterid=dict(type='str'),
            )
        )

        mutually_exclusive = []
        self.module = AnsibleModule(argument_spec=argument_spec,
                                    mutually_exclusive=mutually_exclusive,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Optional
        self.datareduction = self.module.params.get('datareduction', None)
        self.easytier = self.module.params.get('easytier', None)
        self.encrypt = self.module.params.get('encrypt', None)
        self.ext = self.module.params.get('ext', None)
        self.safeguarded = self.module.params.get('safeguarded', False)
        self.noquota = self.module.params.get('noquota', False)
        self.provisioningpolicy = self.module.params.get('provisioningpolicy', '')
        self.noprovisioningpolicy = self.module.params.get('noprovisioningpolicy', False)
        self.replicationpoollinkuid = self.module.params.get('replicationpoollinkuid', '')
        self.resetreplicationpoollinkuid = self.module.params.get('resetreplicationpoollinkuid', False)
        self.replication_partner_clusterid = self.module.params.get('replication_partner_clusterid', '')

        self.parentmdiskgrp = self.module.params.get('parentmdiskgrp', None)
        self.size = self.module.params.get('size', None)
        self.unit = self.module.params.get('unit', None)

        # Dynamic variable
        self.partnership_index = None

        self.basic_checks()

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path,
            token=self.module.params['token']
        )

    def basic_checks(self):
        if not self.name:
            self.module.fail_json(msg='Missing mandatory parameter: name')

        if self.state == 'present':
            message = 'Following parameters are required together: replicationpoollinkuid, replication_partner_clusterid'
            if self.replication_partner_clusterid:
                if not self.replicationpoollinkuid:
                    self.module.fail_json(msg=message)
            else:
                if self.replicationpoollinkuid:
                    self.module.fail_json(msg=message)

            if self.replicationpoollinkuid and self.resetreplicationpoollinkuid:
                self.module.fail_json(
                    msg='Mutually exclusive parameters: replicationpoollinkuid, resetreplicationpoollinkuid'
                )

    def mdiskgrp_exists(self):
        merged_result = {}
        data = self.restapi.svc_obj_info(
            cmd='lsmdiskgrp',
            cmdopts=None,
            cmdargs=['-gui', self.name]
        )

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    def mdiskgrp_create(self):
        # So ext is optional to mkmdiskgrp but make required in ansible
        # until all options for create are implemented.
        # if not self.ext:
        #    self.module.fail_json(msg="You must pass in ext to the module.")

        self.log("creating mdisk group '%s'", self.name)

        # Make command
        cmd = 'mkmdiskgrp'
        cmdopts = {}

        if not self.ext:
            self.module.fail_json(msg="You must pass the ext to the module.")

        if self.noquota or self.safeguarded:
            if not self.parentmdiskgrp:
                self.module.fail_json(msg='Required parameter missing: parentmdiskgrp')

        self.check_partnership()

        if self.module.check_mode:
            self.changed = True
            return

        if self.parentmdiskgrp:
            cmdopts['parentmdiskgrp'] = self.parentmdiskgrp
            if self.size:
                cmdopts['size'] = self.size
            if self.unit:
                cmdopts['unit'] = self.unit
            if self.safeguarded:
                cmdopts['safeguarded'] = self.safeguarded
            if self.noquota:
                cmdopts['noquota'] = self.noquota
        else:
            if self.easytier:
                cmdopts['easytier'] = self.easytier
            if self.encrypt:
                cmdopts['encrypt'] = self.encrypt
            if self.ext:
                cmdopts['ext'] = str(self.ext)
        if self.provisioningpolicy:
            cmdopts['provisioningpolicy'] = self.provisioningpolicy
        if self.datareduction:
            cmdopts['datareduction'] = self.datareduction
        if self.replicationpoollinkuid:
            cmdopts['replicationpoollinkuid'] = self.replicationpoollinkuid
        cmdopts['name'] = self.name
        self.log("creating mdisk group command %s opts %s", cmd, cmdopts)

        # Run command
        result = self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log("creating mdisk group result %s", result)

        if self.replication_partner_clusterid:
            self.set_bit_mask()

        if 'message' in result:
            self.changed = True
            self.log("creating mdisk group command result message %s",
                     result['message'])
        else:
            self.module.fail_json(
                msg="Failed to create mdisk group [%s]" % (self.name))

    def check_partnership(self):
        if self.replication_partner_clusterid:
            merged_result = {}
            result = self.restapi.svc_obj_info(
                cmd='lspartnership',
                cmdopts=None,
                cmdargs=['-gui', self.replication_partner_clusterid]
            )

            if isinstance(result, list):
                for res in result:
                    merged_result = res
            else:
                merged_result = result

            if merged_result:
                self.partnership_index = merged_result.get('partnership_index')
            else:
                self.module.fail_json(
                    msg='Partnership does not exist for the given cluster ({0}).'.format(self.replication_partner_clusterid)
                )

    def set_bit_mask(self, systemmask=None):
        cmd = 'chmdiskgrp'
        bit_mask = '1'.ljust(int(self.partnership_index) + 1, '0') if not systemmask else systemmask
        cmdopts = {'replicationpoollinkedsystemsmask': bit_mask}
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])

    def mdiskgrp_delete(self):
        if self.module.check_mode:
            self.changed = True
            return

        self.log("deleting mdiskgrp '%s'", self.name)

        cmd = 'rmmdiskgrp'
        cmdopts = None
        cmdargs = [self.name]

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)

        # Any error will have been raised in svc_run_command
        # chmkdiskgrp does not output anything when successful.
        self.changed = True

    def mdiskgrp_update(self, modify):
        # updte the mdisk group
        self.log("updating mdiskgrp '%s'", self.name)

        systemmask = None
        cmd = 'chmdiskgrp'

        if 'replicationpoollinkedsystemsmask' in modify:
            systemmask = modify.pop('replicationpoollinkedsystemsmask')

        if modify:
            cmdopts = modify
            self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])

        if systemmask or 'replicationpoollinkuid' in modify:
            self.set_bit_mask(systemmask)

        self.changed = True

    # TBD: Implement a more generic way to check for properties to modify.
    def mdiskgrp_probe(self, data):
        props = {}

        if self.noprovisioningpolicy and data.get('provisioning_policy_name', ''):
            props['noprovisioningpolicy'] = self.noprovisioningpolicy
        if self.provisioningpolicy and self.provisioningpolicy != data.get('provisioning_policy_name', ''):
            props['provisioningpolicy'] = self.provisioningpolicy
        if self.replicationpoollinkuid and self.replicationpoollinkuid != data.get('replication_pool_link_uid', ''):
            props['replicationpoollinkuid'] = self.replicationpoollinkuid
        if self.resetreplicationpoollinkuid:
            props['resetreplicationpoollinkuid'] = self.resetreplicationpoollinkuid
        if self.replication_partner_clusterid:
            self.check_partnership()
            bit_mask = '1'.ljust(int(self.partnership_index) + 1, '0')
            if bit_mask.zfill(64) != data.get('replication_pool_linked_systems_mask', ''):
                props['replicationpoollinkedsystemsmask'] = bit_mask

        self.log("mdiskgrp_probe props='%s'", props)
        return props

    def apply(self):
        changed = False
        msg = None
        modify = []

        mdiskgrp_data = self.mdiskgrp_exists()

        if mdiskgrp_data:
            if self.state == 'absent':
                self.log("CHANGED: mdisk group exists, "
                         "but requested state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chmdiskgrp should be called.
                modify = self.mdiskgrp_probe(mdiskgrp_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: mdisk group does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.state == 'present':
                if not mdiskgrp_data:
                    self.mdiskgrp_create()
                    msg = "Mdisk group [%s] has been created." % self.name
                else:
                    # This is where we would modify
                    self.mdiskgrp_update(modify)
                    msg = "Mdisk group [%s] has been modified." % self.name

            elif self.state == 'absent':
                self.mdiskgrp_delete()
                msg = "Volume [%s] has been deleted." % self.name

            if self.module.check_mode:
                msg = 'skipping changes due to check mode'
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "Mdisk group [%s] did not exist." % self.name
            else:
                msg = "Mdisk group [%s] already exists. No modifications done" % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVCmdiskgrp()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
