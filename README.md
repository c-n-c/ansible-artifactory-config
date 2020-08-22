#### Ansible Playbook for migration of Artifatory Repos

Artifactory repos can be backed up using REST APIs and then restored from it.

##### Usage:
```$ ansible-playbook playbook.yml -e "{"ignored_files": ["<filename1>", "<filename2>"]}" ```
