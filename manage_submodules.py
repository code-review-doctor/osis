#!/usr/bin/python

import os.path
from os import path
import subprocess
import sys

project_dir = os.getcwd()
project_branch = subprocess.check_output('git branch --show-current', shell=True).decode(sys.stdout.encoding)
module_branch = 'dev'
arguments = len(sys.argv) - 1
if arguments > 0:
    module_branch = sys.argv[1]
elif project_branch in ['dev', 'test', 'qa', 'master']:
    module_branch = project_branch
print('Project Dir : {}'.format(project_dir))
print('Project Branch : {}'.format(project_branch))
print('Module Branch : {}'.format(module_branch))
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
        print('')
        print('Module {} exists in project directory'.format(module))
        print('Updating module {} from branch {}'.format(module, module_branch))
        fetch_command = 'git fetch origin {branch}'.format(branch=module_branch)
        switch_branch_command = 'git checkout {branch}'.format(branch=module_branch)
        new_branch_command = 'git checkout -b {branch} origin/{branch}'.format(branch=module_branch)
        check_branch_exists_locally_command = ' git rev-parse --verify {branch}'.format(branch=module_branch)
        pull_command = 'git pull'
        os.chdir(module_dir)
        os.system(fetch_command)
        try:
            command_status = subprocess.check_call(check_branch_exists_locally_command.split())
            os.system(switch_branch_command)
        except subprocess.CalledProcessError:
            os.system(new_branch_command)
        os.system(pull_command)
        os.chdir(project_dir)
    else:
        print('')
        print('Module {} not exists in project directory'.format(module))
        print('Cloning module {} from branch {} in directory {}'.format(module, module_branch, module_dir))
        command = 'git clone {git_url} -b {branch} {directory}'.format(branch=module_branch,
                                                                       git_url=git_url,
                                                                       directory=module_dir)
        os.system(command)
