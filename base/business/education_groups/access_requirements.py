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
from typing import List, Optional

from django.core.exceptions import PermissionDenied

from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine
from base.models.education_group_year import EducationGroupYear


def can_postpone_access_requirements(education_group_year: 'EducationGroupYear') -> bool:
    return not education_group_year.academic_year.is_past


def bulk_postpone_access_requirements(education_group_years_from: List['EducationGroupYear']) -> None:
    fields = [field.name for field in AdmissionCondition._meta.get_fields(include_parents=False)]
    for egy in education_group_years_from:
        try:
            postpone_access_requirements(egy, fields)
        except AdmissionCondition.DoesNotExist:
            pass


def postpone_access_requirements(education_group_year_from: "EducationGroupYear", fields: List[str]) -> None:
    if not can_postpone_access_requirements(education_group_year_from):
        raise PermissionDenied

    next_qs = EducationGroupYear.objects.filter(
        education_group=education_group_year_from.education_group,
        academic_year__year__gt=education_group_year_from.academic_year.year
    )

    admission_condition_to_postpone = AdmissionCondition.objects.get(education_group_year=education_group_year_from)

    for egy in next_qs:
        _postpone_admission_condition(egy, admission_condition_to_postpone, fields)


def _postpone_admission_condition(
        egy: 'EducationGroupYear',
        admission_condition_to_postpone: 'AdmissionCondition',
        fields: List[str]
) -> None:
    values_to_upsert = {
        field: getattr(admission_condition_to_postpone, field) for field in fields
        if field not in ("education_group_year", "education_group_year_id", "admissionconditionline", "id")
    }
    obj, created = AdmissionCondition.objects.update_or_create(
        education_group_year=egy,
        defaults=values_to_upsert
    )


def bulk_postpone_access_requirements_line(education_group_years_from: List['EducationGroupYear']) -> None:
    for egy in education_group_years_from:
        try:
            postpone_access_requirements_line(egy, None)
        except AdmissionConditionLine.DoesNotExist:
            pass


def postpone_access_requirements_line(
        education_group_year_from: 'EducationGroupYear',
        section: Optional['str']
) -> None:
    if not can_postpone_access_requirements(education_group_year_from):
        raise PermissionDenied

    next_qs = EducationGroupYear.objects.filter(
        education_group=education_group_year_from.education_group,
        academic_year__year__gt=education_group_year_from.academic_year.year
    ).select_related("admissioncondition")

    admission_condition_lines_to_postpone = AdmissionConditionLine.objects.filter(
        admission_condition__education_group_year=education_group_year_from,
    )
    if section:
        admission_condition_lines_to_postpone = admission_condition_lines_to_postpone.filter(section=section)
    admission_condition_lines_to_postpone = list(admission_condition_lines_to_postpone)

    for egy in next_qs:
        _purge_admission_lines(egy, section)
        _postpone_admission_condition_line(egy, admission_condition_lines_to_postpone)


def _purge_admission_lines(egy: 'EducationGroupYear', section: Optional[str]):
    qs = AdmissionConditionLine.objects.filter(
        admission_condition__education_group_year=egy,
    )
    if section:
        qs = qs.filter(section=section)
    for line in qs:
        line.delete()


def _postpone_admission_condition_line(
        egy: 'EducationGroupYear',
        admission_condition_lines_to_postpone: List['AdmissionConditionLine']
) -> None:
    if not admission_condition_lines_to_postpone:
        return

    egy_admission_condition, created = AdmissionCondition.objects.get_or_create(
        education_group_year=egy
    )
    for line_to_postpone in admission_condition_lines_to_postpone:
        line_to_postpone.pk = None
        line_to_postpone.id = None
        line_to_postpone.external_id = None
        line_to_postpone.admission_condition = egy_admission_condition
        line_to_postpone.save()
