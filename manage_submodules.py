#!/usr/bin/python

import os.path
from os import path

branch = "dev"
# acces_rights = 0o764
project_dir = os.getcwd()

print('Project Dir : {}'.format(project_dir))
print('Branch : {}'.format(branch))
print('')

modules = {
    "admission": "https://github.com/uclouvain/osis-admission.git",
    "assistant": "https://github.com/uclouvain/osis-assistant.git",
    "continuing_education": "https://github.com/uclouvain/osis-continuing-education.git",
    "dissertation": "https://github.com/uclouvain/osis-dissertation.git",
    "internship": "https://github.com/uclouvain/osis-internship.git",
    "osis_common": "https://github.com/uclouvain/osis-common.git",
    "osis_history": "https://github.com/uclouvain/osis-history.git",
    "osis_mail_template": "https://github.com/uclouvain/osis-mail-template.git",
    "partnership": "https://github.com/uclouvain/osis-partnership.git"
}

for module, git_url in modules.items():
    module_dir = os.path.join(project_dir, module)
    if path.exists(module_dir) and path.isdir(module_dir):
        print('Module {} exists in project directory'.format(module))
        print('Updating module {} from branch {}'.format(module, branch))
        print('')
        checkout_command = 'git checkout {branch}'.format(branch=branch)
        pull_command = 'git pull'
        os.chdir(module_dir)
        os.system(checkout_command)
        os.system(pull_command)
        os.chdir(project_dir)
    else:
        print('Module {} not exists in project directory'.format(module))
        print('Cloning module {} from branch {} in directory {}'.format(module, branch, module_dir))
        print('')
        command = 'git clone {git_url} -b {branch} --single-branch {directory}'.format(branch=branch,
                                                                                    git_url=git_url,
                                                                                    directory=module_dir)
        # os.mkdir(module_dir, acces_rights)
        os.system(command)
