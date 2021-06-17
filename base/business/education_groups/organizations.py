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

from base.models.education_group_organization import EducationGroupOrganization
from base.models.education_group_year import EducationGroupYear


def bulk_postpone_organizations(education_group_years_from: List['EducationGroupYear']) -> None:
    for egy in education_group_years_from:
        postpone_organizations(egy)


def postpone_organizations(education_group_year_from: "EducationGroupYear") -> None:
    next_qs = EducationGroupYear.objects.filter(
        education_group=education_group_year_from.education_group,
        academic_year__year__gt=education_group_year_from.academic_year.year
    )

    organizations_to_postpone = EducationGroupOrganization.objects.filter(
        education_group_year=education_group_year_from
    )

    for egy in next_qs:
        for organization in organizations_to_postpone:
            _postpone_organization(egy, organization)


def _postpone_organization(egy: 'EducationGroupYear', organization_to_postpone: 'EducationGroupOrganization') -> None:
    organization_to_postpone.pk = None
    organization_to_postpone.id = None
    organization_to_postpone.external_id = None
    organization_to_postpone.changed = None
    organization_to_postpone.education_group_year = egy
    organization_to_postpone.save()
