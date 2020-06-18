# Ansible Collection - ibm.spectrum_virtualize

[![Doc](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://docs.ansible.com/ansible/latest/modules/list_of_cloud_modules.html#azure)
[![Code of conduct](https://img.shields.io/badge/code%20of%20conduct-Ansible-silver.svg)](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
[![License](https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg)](LICENSE)

This collection provides a series of Ansible modules and plugins for interacting with the IBM Spectrum Virtualize Family. These products include the IBM SAN Volume Controller, IBM FlashSystem family members built with IBM Spectrum Virtualize (FlashSystem 5010, 5030, 5100, 7200, 9100, 9200, 9200R, and V9000), IBM Storwize family, and IBM Spectrum Virtualize for Public Cloud. For more information regarding these products see the [IBM Knowledge Center](https://www.ibm.com/support/knowledgecenter/en/) .

## Requirements

- Ansible version 2.9 or higher

## Installation

To install the IBM Spectrum Virtualize collection hosted in Galaxy:

```bash
ansible-galaxy collection install ibm.spectrum_virtualize
```

To upgrade to the latest version of the IBM Spectrum Virtualize collection:

```bash
ansible-galaxy collection install ibm.spectrum_virtualize --force
```

## Usage

### Playbooks

To use a module from the IBM Spectrum Virtualize collection, please reference the full namespace, collection name, and module name that you want to use:

```yaml
---
- name: Using the IBM Spectrum Virtualize collection
  hosts: localhost
  tasks:
    - name: Gather info from storage
      ibm.spectrum_virtualize.ibm_svc_info:
        clustername: x.x.x.x
        domain:
        username: username
        password: password
        log_path: /tmp/playbook.debug
        name: gather_info
        state: info
        gather_subset: all
```

Alternatively, you can add a full namepsace and collection name in the `collections` element:

```yaml
---
- name: Using the IBM Spectrum Virtualize collection
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  hosts: localhost
  tasks:
    - name: Gather info from storage
      ibm_svc_info:
        clustername: x.x.x.x
        domain:
        username: username
        password: password
        log_path: /tmp/playbook.debug
        name: gather_info
        state: info
        gather_subset: all
```

## Supported Resources

### Modules

- ibm_svc_info - Collects information on the IBM Spectrum Virtualize system
- ibm_svc_host - Host management for IBM Spectrum Virtualize
- ibm_svc_mdisk - MDisk managment for IBM Spectrum Virtualize
- ibm_svc_mdiskgrp - Pool management for IBM Spectrum Virtualize
- ibm_svc_vdisk - Volume management for IBM Spectrum Virtualize
- ibm_svc_vol_map - Volume mapping management for IBM Spectrum Virtualize
- ibm_svc_volume_clone - Volume clone management for IBM Spectrum Virtualize
- ibm_svc_volume_snapshot - Volume snapshot management for IBM Spectrum Virtualize
- ibm_svc_volume_fcconsistgrp - FlashCopy consistency groups management for IBM Spectrum Virtualize

## Limitation

The IBM Spectrum Virtualize Ansible collections leverage REST APIs to connect to the  IBM Spectrum Virtualize storage system. This creates the following limitations:
1. Using the REST API to list more than 2000 objects may create a loss of service from the API side, as it automatically restarts due to memory constraints.
2. It is not possible to access the REST API using an IPv6 address on a cluster.
3. To run the Ansible collections, Spectrum Virtualize storage system must be at Version 8.1.3 or higher.

## Contributing

Currently we are not accepting community contributions.
Though, you may periodically review this content to learn when and how contributions can be made in the future.

## License

GNU General Public License v3.0

See [LICENSE](LICENSE) to see the full text.
