#!/usr/bin/python
# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_svc_info
short_description: This module gathers various information from the IBM Spectrum Virtualize family storage systems
version_added: "1.0.0"
description:
- Gathers the list of specified IBM Spectrum Virtualize family storage system
  entities. These include the list of nodes, pools, volumes, hosts,
  host clusters, FC ports, iSCSI ports, target port FC, FC consistgrp,
  vdiskcopy, I/O groups, FC map, FC connectivity, NVMe fabric,
  array, and system.
author:
- Peng Wang (@wangpww)
options:
  clustername:
    description:
    - The hostname or management IP of the
      Spectrum Virtualize storage system.
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
    - To generate a token, use the ibm_svc_auth module.
    type: str
    version_added: '1.5.0'
  log_path:
    description:
    - Path of debug log file.
    type: str
  validate_certs:
    description:
    - Validates certification.
    default: false
    type: bool
  objectname:
    description:
    - If specified, only the instance with the I(objectname) is returned. If not specified, all the instances are returned.
    type: str
  gather_subset:
    type: list
    elements: str
    description:
    - List of string variables to specify the Spectrum Virtualize entities
      for which information is required.
    - all - list of all Spectrum Virtualize entities
            supported by the module.
    - vol - lists information for VDisks.
    - pool - lists information for mdiskgrps.
    - node - lists information for nodes.
    - iog - lists information for I/O groups.
    - host - lists information for hosts.
    - hostvdiskmap - lists all vdisks mapped to host 'objectname'
    - vdiskhostmap - lists all hosts vdisk 'objectname' is mapped to
    - hc - lists information for host clusters.
    - fc - lists information for FC connectivity.
    - fcport - lists information for FC ports.
    - targetportfc - lists information for WWPN which is required to set up
                     FC zoning and to display the current failover status
                     of host I/O ports.
    - fcmap - lists information for FC maps.
    - rcrelationship - lists information for remote copy relationships.
    - fcconsistgrp - displays a concise list or a detailed
                     view of flash copy consistency groups.
    - rcconsistgrp - displays a concise list or a detailed
                     view of remote copy consistency groups.
    - iscsiport - lists information for iSCSI ports.
    - vdiskcopy - lists information for volume copy.
    - array - lists information for array MDisks.
    - system - displays the storage system information.
    choices: [vol, pool, node, iog, host, hostvdiskmap, vdiskhostmap, hc, fcport
              , iscsiport, fc, fcmap, fcconsistgrp, rcrelationship, rcconsistgrp
              , vdiskcopy, targetportfc, array, system, all]
    default: "all"
notes:
    - This module supports C(check_mode).
'''

EXAMPLES = '''
- name: Get volume info
  ibm.spectrum_virtualize.ibm_svc_info:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    log_path: /tmp/ansible.log
    gather_subset: vol
- name: Get volume info
  ibm.spectrum_virtualize.ibm_svc_info:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    log_path: /tmp/ansible.log
    objectname: volumename
    gather_subset: vol
- name: Get pool info
  ibm.spectrum_virtualize.ibm_svc_info:
    clustername: "{{clustername}}"
    domain: "{{domain}}"
    username: "{{username}}"
    password: "{{password}}"
    log_path: /tmp/ansible.log
    gather_subset: pool
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCGatherInfo(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                objectname=dict(type='str'),
                gather_subset=dict(type='list', elements='str', required=False,
                                   default=['all'],
                                   choices=['vol',
                                            'pool',
                                            'node',
                                            'iog',
                                            'host',
                                            'hostvdiskmap',
                                            'vdiskhostmap',
                                            'hc',
                                            'fc',
                                            'fcport',
                                            'targetportfc',
                                            'iscsiport',
                                            'fcmap',
                                            'rcrelationship',
                                            'fcconsistgrp',
                                            'rcconsistgrp',
                                            'vdiskcopy',
                                            'array',
                                            'system',
                                            'all'
                                            ]),
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        self.log = get_logger(self.__class__.__name__, log_path)
        self.objectname = self.module.params['objectname']

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

    def get_volumes_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            vols = self.restapi.svc_obj_info(cmd='lsvdisk', cmdopts=None,
                                             cmdargs=cmdargs)
            self.log.info("Successfully listed %d volumes from array %s",
                          len(vols), self.module.params['clustername'])
            return vols
        except Exception as e:
            msg = ('Get Volumes from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_pools_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            pools = self.restapi.svc_obj_info(cmd='lsmdiskgrp', cmdopts=None,
                                              cmdargs=cmdargs)
            self.log.info('Successfully listed %d pools from array '
                          '%s', len(pools), self.module.params['clustername'])
            return pools
        except Exception as e:
            msg = ('Get Pools from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_nodes_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            nodes = self.restapi.svc_obj_info(cmd='lsnode', cmdopts=None,
                                              cmdargs=cmdargs)
            self.log.info('Successfully listed %d pools from array %s',
                          len(nodes), self.module.params['clustername'])
            return nodes
        except Exception as e:
            msg = ('Get Nodes from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_hosts_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            hosts = self.restapi.svc_obj_info(cmd='lshost', cmdopts=None,
                                              cmdargs=cmdargs)
            self.log.info('Successfully listed %d hosts from array '
                          '%s', len(hosts), self.module.params['clustername'])
            return hosts
        except Exception as e:
            msg = ('Get Hosts from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_vdisk_host_map(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            vhmaps = self.restapi.svc_obj_info(cmd='lsvdiskhostmap', cmdopts=None,
                                               cmdargs=cmdargs)
            self.log.info('Successfully listed %d vdisk host maps from array '
                          '%s', len(vhmaps), self.module.params['clustername'])
            return vhmaps
        except Exception as e:
            msg = ('Get Vdisk Host Maps from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_host_vdisk_map(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            hvmaps = self.restapi.svc_obj_info(cmd='lshostvdiskmap', cmdopts=None,
                                               cmdargs=cmdargs)
            self.log.info('Successfully listed %d host vdisk maps from array '
                          '%s', len(hvmaps), self.module.params['clustername'])
            return hvmaps
        except Exception as e:
            msg = ('Get Host Vdisk Maps from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_iogroups_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            iogrps = self.restapi.svc_obj_info(cmd='lsiogrp', cmdopts=None,
                                               cmdargs=cmdargs)
            self.log.info('Successfully listed %d hosts from array '
                          '%s', len(iogrps), self.module.params['clustername'])
            return iogrps
        except Exception as e:
            msg = ('Get IO Groups from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_host_clusters_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            hcs = self.restapi.svc_obj_info(cmd='lshostcluster', cmdopts=None,
                                            cmdargs=cmdargs)
            self.log.info('Successfully listed %d host clusters from array '
                          '%s', len(hcs), self.module.params['clustername'])
            return hcs
        except Exception as e:
            msg = ('Get Host Cluster from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fc_connectivity_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            fc = self.restapi.svc_obj_info(cmd='lsfabric', cmdopts=None,
                                           cmdargs=cmdargs)
            self.log.info('Successfully listed %d fc connectivity from array '
                          '%s', len(fc), self.module.params['clustername'])
            return fc
        except Exception as e:
            msg = ('Get FC Connectivity from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fc_ports_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            fcports = self.restapi.svc_obj_info(cmd='lsportfc', cmdopts=None,
                                                cmdargs=cmdargs)
            self.log.info('Successfully listed %d fc ports from array %s',
                          len(fcports), self.module.params['clustername'])
            return fcports
        except Exception as e:
            msg = ('Get fc ports from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_target_port_fc_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            targetportfc = self.restapi.svc_obj_info(cmd='lstargetportfc',
                                                     cmdopts=None,
                                                     cmdargs=cmdargs)
            self.log.info('Successfully listed %d target port fc '
                          'from array %s', len(targetportfc),
                          self.module.params['clustername'])
            return targetportfc
        except Exception as e:
            msg = ('Get target port fc from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_iscsi_ports_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            ipports = self.restapi.svc_obj_info(cmd='lsportip', cmdopts=None,
                                                cmdargs=cmdargs)
            self.log.info('Successfully listed %d iscsi ports from array %s',
                          len(ipports), self.module.params['clustername'])
            return ipports
        except Exception as e:
            msg = ('Get iscsi ports from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fc_map_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            fcmaps = self.restapi.svc_obj_info(cmd='lsfcmap', cmdopts=None,
                                               cmdargs=cmdargs)
            self.log.info('Successfully listed %d fc maps from array %s',
                          len(fcmaps), self.module.params['clustername'])
            return fcmaps
        except Exception as e:
            msg = ('Get fc maps from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_rcrel_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            rcrel = self.restapi.svc_obj_info(cmd='lsrcrelationship',
                                              cmdopts=None,
                                              cmdargs=cmdargs)
            self.log.info('Successfully listed %d remotecopy from array %s',
                          len(rcrel), self.module.params['clustername'])
            return rcrel
        except Exception as e:
            msg = ('Get remotecopies from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_array_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            array = self.restapi.svc_obj_info(cmd='lsarray', cmdopts=None,
                                              cmdargs=cmdargs)
            self.log.info('Successfully listed %d array info from array %s',
                          len(array), self.module.params['clustername'])
            return array
        except Exception as e:
            msg = ('Get Array info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_system_list(self):
        try:
            if self.objectname:
                self.log.warn('The objectname %s is ignored when retrieving '
                              'the system information', self.objectname)
            system = self.restapi.svc_obj_info(cmd='lssystem', cmdopts=None,
                                               cmdargs=None)
            self.log.info('Successfully listed %d system info from array %s',
                          len(system), self.module.params['clustername'])
            return system
        except Exception as e:
            msg = ('Get System info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fcconsistgrp_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            fcconsistgrp = self.restapi.svc_obj_info(cmd='lsfcconsistgrp',
                                                     cmdopts=None,
                                                     cmdargs=cmdargs)
            self.log.info('Successfully listed %d fcconsistgrp info '
                          'from array %s', len(fcconsistgrp),
                          self.module.params['clustername'])
            return fcconsistgrp
        except Exception as e:
            msg = ('Get fcconsistgrp info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_rcconsistgrp_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            rcconsistgrp = self.restapi.svc_obj_info(cmd='lsrcconsistgrp',
                                                     cmdopts=None,
                                                     cmdargs=cmdargs)
            self.log.info('Successfully listed %d rcconsistgrp info '
                          'from array %s', len(rcconsistgrp),
                          self.module.params['clustername'])
            return rcconsistgrp
        except Exception as e:
            msg = ('Get rcconsistgrp info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_vdiskcopy_list(self):
        try:
            cmdargs = [self.objectname] if self.objectname else None
            vdiskcopy = self.restapi.svc_obj_info(cmd='lsvdiskcopy',
                                                  cmdopts=None,
                                                  cmdargs=cmdargs)
            self.log.info('Successfully listed %d vdiskcopy info '
                          'from array %s', len(vdiskcopy),
                          self.module.params['clustername'])
            return vdiskcopy
        except Exception as e:
            msg = ('Get vdiskcopy info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def apply(self):
        all = ['vol', 'pool', 'node', 'iog', 'host', 'hc', 'fc',
               'fcport', 'iscsiport', 'fcmap', 'rcrelationship',
               'fcconsistgrp', 'rcconsistgrp', 'vdiskcopy',
               'targetportfc', 'array', 'system']

        # host/vdiskmap not added to all as they require an objectname
        # in order to run, so only use these as gather_subset

        subset = self.module.params['gather_subset']
        if self.objectname and len(subset) != 1:
            msg = ("objectname(%s) is specified while gather_subset(%s) is not "
                   "one of %s" % (self.objectname, self.subset, all))
            self.module.fail_json(msg=msg)
        if len(subset) == 0 or 'all' in subset:
            self.log.info("The default value for gather_subset is all")
            subset = all

        vol = []
        pool = []
        node = []
        iog = []
        host = []
        hostvdiskmap = []
        vdiskhostmap = []
        hc = []
        fc = []
        fcport = []
        targetportfc = []
        iscsiport = []
        fcmap = []
        fcconsistgrp = []
        rcrelationship = []
        rcconsistgrp = []
        vdiskcopy = []
        array = []
        system = []

        if 'vol' in subset:
            vol = self.get_volumes_list()
        if 'pool' in subset:
            pool = self.get_pools_list()
        if 'node' in subset:
            node = self.get_nodes_list()
        if 'iog' in subset:
            iog = self.get_iogroups_list()
        if 'host' in subset:
            host = self.get_hosts_list()
        if 'hostvdiskmap' in subset:
            hostvdiskmap = self.get_host_vdisk_map()
        if 'vdiskhostmap' in subset:
            vdiskhostmap = self.get_vdisk_host_map()
        if 'hc' in subset:
            hc = self.get_host_clusters_list()
        if 'fc' in subset:
            fc = self.get_fc_connectivity_list()
        if 'targetportfc' in subset:
            targetportfc = self.get_target_port_fc_list()
        if 'fcport' in subset:
            fcport = self.get_fc_ports_list()
        if 'iscsiport' in subset:
            iscsiport = self.get_iscsi_ports_list()
        if 'fcmap' in subset:
            fcmap = self.get_fc_map_list()
        if 'fcconsistgrp' in subset:
            fcconsistgrp = self.get_fcconsistgrp_list()
        if 'rcrelationship' in subset:
            rcrelationship = self.get_rcrel_list()
        if 'rcconsistgrp' in subset:
            rcconsistgrp = self.get_rcconsistgrp_list()
        if 'vdiskcopy' in subset:
            vdiskcopy = self.get_vdiskcopy_list()
        if 'array' in subset:
            array = self.get_array_list()
        if 'system' in subset:
            system = self.get_system_list()

        self.module.exit_json(
            Volume=vol,
            Pool=pool,
            Node=node,
            IOGroup=iog,
            Host=host,
            HostVdiskMap=hostvdiskmap,
            VdiskHostMap=vdiskhostmap,
            HostCluster=hc,
            FCConnectivitie=fc,
            FCConsistgrp=fcconsistgrp,
            RCConsistgrp=rcconsistgrp,
            VdiskCopy=vdiskcopy,
            FCPort=fcport,
            TargetPortFC=targetportfc,
            iSCSIPort=iscsiport,
            FCMap=fcmap,
            RemoteCopy=rcrelationship,
            Array=array,
            System=system)


def main():
    v = IBMSVCGatherInfo()
    try:
        v.apply()
    except Exception as e:
        v.log.debug("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
