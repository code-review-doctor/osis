# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import subprocess
from typing import List, Tuple
import pathlib

from django.conf import settings
from django.core.checks import register, Tags, CheckMessage, Info, Error

RETURN_CODE = int
OUTPUT_MESSAGE = str

SUCCESS_RETURN_CODE = 0


@register(Tags.translation)
def makemessages_check(app_configs, **kwargs) -> List[CheckMessage]:
    errors = []
    apps = app_configs or settings.INSTALLED_APPS
    apps_with_locale_directory = [app for app in apps if has_locale_directory(app)]

    for app in apps_with_locale_directory:
        output_message, return_code = check_messages_for_app(app)
        if return_code != SUCCESS_RETURN_CODE:
            error_message = "{app}\n{output}".format(app=app, output=output_message)
            errors.append(Error(error_message))

    if not errors:
        errors.append(Info("All good"))
    return errors


def has_locale_directory(app_name: str) -> bool:
    path = pathlib.Path(app_name) / "locale"
    return path.exists()


def check_messages_for_app(app_name: str) -> Tuple[OUTPUT_MESSAGE, RETURN_CODE]:

    completed_process = subprocess.run(
        ["../manage.py", "check_messages"],
        capture_output=True,
        universal_newlines=True,
        cwd=app_name
    )
    return completed_process.stderr, completed_process.returncode

