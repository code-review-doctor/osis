##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List, Dict

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from openpyxl.styles import Font

from base.business.xls import get_name_or_username
from osis_common.document import xls_build

BOLD_FONT = Font(bold=True)


def create_class_copy_report(user: User, copy_classes_report: List[Dict]):
    working_sheets_data = []

    for line in copy_classes_report:
        working_sheets_data.append([line.get('source'), line.get('result'), line.get('exception')])
    parameters = {
        xls_build.DESCRIPTION: _('Classes copy report'),
        xls_build.USER: get_name_or_username(user),
        xls_build.FILENAME: "classes_copy_report",
        xls_build.WS_TITLE: _('Classes copy report'),
        xls_build.HEADER_TITLES: [
            str(_('Copy source')),
            str(_('Copy result')),
            str(_('Error')),
        ],
        xls_build.FONT_ROWS: {
            BOLD_FONT: [0]
        }
    }

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters))
