##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from base.business.education_groups.reporting import EducationGroupYearLearningUnitsPrerequisitesToExcel, XLS_FILENAME
from base.models.education_group_year import EducationGroupYear
from osis_common.document.xls_build import CONTENT_TYPE_XLS


@login_required
def get_learning_unit_prerequisites_excel(request, education_group_year_pk):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_pk)
    excel = EducationGroupYearLearningUnitsPrerequisitesToExcel(education_group_year).to_excel()
    response = HttpResponse(excel, content_type=CONTENT_TYPE_XLS)
    filename = "{workbook_name}.xlsx".format(workbook_name=str(_(XLS_FILENAME)).replace(" ", "_"))
    response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
    return response
