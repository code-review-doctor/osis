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
from typing import List

from base.models.education_group_year import EducationGroupYear
from cms.contrib import utils
from cms.enums import entity_name
from education_group.models.group_year import GroupYear


def bulk_postpone_cms_for_education_group_year(education_group_years_from: List['EducationGroupYear']) -> None:
    for egy in education_group_years_from:
        _postpone_cms_for_education_group_year(egy)


def bulk_postpone_cms_for_group_year(group_years_from: List['GroupYear']) -> None:
    for gy in group_years_from:
        _postpone_cms_for_group_year(gy)


def _postpone_cms_for_education_group_year(education_group_year_from: 'EducationGroupYear') -> None:
    next_qs = EducationGroupYear.objects.filter(
        education_group=education_group_year_from.education_group,
        academic_year__year__gt=education_group_year_from.academic_year.year
    )
    for egy in next_qs:
        utils.postpone_cms(education_group_year_from.pk, egy.pk, entity_name.OFFER_YEAR)


def _postpone_cms_for_group_year(group_year_from: 'GroupYear') -> None:
    next_qs = GroupYear.objects.filter(
        group=group_year_from.group,
        academic_year__year__gt=group_year_from.academic_year.year
    )
    for gy in next_qs:
        utils.postpone_cms(group_year_from.pk, gy.pk, entity_name.GROUP_YEAR)
