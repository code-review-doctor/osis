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
from typing import Iterable, Optional

from django.db.models import Count, Q

from base.models.enums.education_group_types import GroupType
from base.models.group_element_year import GroupElementYear
from program_management.models.element import Element

YEAR_TO_CLEAN = 2021


def get_trainings_and_mini_trainings_with_multiple_common_core():
    return Element.objects.filter(
        group_year__education_group_type__category__in=["TRAINING", "MINI_TRAINING"],
        group_year__academic_year__year__gte=YEAR_TO_CLEAN
    ).annotate(
        number_common_core=Count(
            "parent_elements",
            filter=Q(parent_elements__child_element__group_year__education_group_type__name=GroupType.COMMON_CORE.name)
        )
    ).filter(
        number_common_core__gte=2
    ).select_related(
        "group_year",
        "group_year__academic_year"
    ).order_by(
        "group_year__partial_acronym",
        "group_year__academic_year__year"
    )


def remove_redundant_common_core(parent_element: Element):
    common_core_links = GroupElementYear.objects.filter(
        parent_element=parent_element,
        child_element__group_year__education_group_type__name=GroupType.COMMON_CORE.name
    ).select_related("child_element").order_by("child_element__id")

    link_to_delete = select_link_to_delete(common_core_links)
    if link_to_delete:
        link_to_delete.delete()


def select_link_to_delete(common_core_links: Iterable[GroupElementYear]) -> Optional[GroupElementYear]:
    is_empty_states = [_is_empty(link.child_element) for link in common_core_links]
    if not all(is_empty_states):
        return next(link for link in common_core_links if _is_empty(link.child_element))

    link_not_used_last_year = next((link for link in common_core_links if not _was_in_use_last_year(link)), None)
    return link_not_used_last_year


def _is_empty(element: Element) -> bool:
    return not GroupElementYear.objects.filter(parent_element=element).exists()


def _was_in_use_last_year(link: GroupElementYear) -> bool:
    return GroupElementYear.objects.filter(
        parent_element__group_year__group_id=link.parent_element.group_year.group_id,
        parent_element__group_year__academic_year__year=link.parent_element.group_year.academic_year.year-1,
        child_element__group_year__partial_acronym=link.child_element.group_year.partial_acronym,
    ).exists()


def main():
    qs = get_trainings_and_mini_trainings_with_multiple_common_core()
    print("Remove redundant common cores:")
    for el in qs:
        print("- {}".format(str(el)))
        remove_redundant_common_core(el)


main()
