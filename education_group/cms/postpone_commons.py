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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import copy
import uuid

from django.db.models import OuterRef, Max, Subquery

from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear


def postpone_to_year(to_year: int):
    subquery_max_existing_year = EducationGroupYear.objects.filter(
        education_group=OuterRef("education_group")
    ).values(
        "education_group"
    ).annotate(
        max_year=Max("academic_year__year")
    ).order_by(
        "education_group"
    ).values("max_year")

    qs = EducationGroupYear.objects.look_for_common(
        academic_year__year=Subquery(subquery_max_existing_year[:1])
    ).select_related(
        'academic_year'
    )

    for egy in qs:
        _postpone_to_year(egy, to_year)


def _postpone_to_year(base_egy: EducationGroupYear, to_year: int):
    for year in range(base_egy.academic_year.year, to_year):
        new_egy = copy.copy(base_egy)
        new_egy.id = None
        new_egy.uuid = uuid.uuid4()
        new_egy.academic_year = AcademicYear.objects.get(year=year+1)
        new_egy.save()
