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
from typing import Iterable, List

import attr
from django.db.models import Exists, OuterRef, Q
from django.utils.functional import cached_property
from django.views.generic import ListView

from base.forms.education_group.search_offers import OffersFilter
from base.models import academic_year
from base.models.education_group_year import EducationGroupYear, EducationGroupYearQueryset
from base.models.entity_version import EntityVersion
from base.models.enums.education_group_categories import Categories
from base.utils.cache import CacheFilterMixin
from education_group.models.cohort_year import CohortYear
from education_group.models.enums.cohort_name import CohortName
from osis_role.contrib.views import PermissionRequiredMixin


@attr.s(frozen=True, slots=True)
class OfferSearchDTO:
    acronym = attr.ib(type=str)
    title = attr.ib(type=str)
    management_entity_acronym = attr.ib(type=str)

    @property
    def is_first_year_bachelor(self):
        return "11BA" in self.acronym


class OffersSearch(PermissionRequiredMixin, CacheFilterMixin, ListView):
    model = EducationGroupYear
    template_name = "base/offers/list.html"
    permission_required = "base.can_access_offer"

    @cached_property
    def form(self):
        return OffersFilter(self.request.GET or None)

    def get_queryset(self):
        if self.form.is_valid() and self.request.GET:
            acronym = self.form.cleaned_data['acronym']
            management_entity = self.form.cleaned_data['management_entity']
            return convert_queryset_to_dto(get_queryset(acronym, management_entity))

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = self.form
        return context


def get_queryset(acronym: str, management_entity: str) -> Iterable[EducationGroupYear]:
    cte = EntityVersion.objects.with_parents(acronym__icontains=management_entity)
    entity_ids_with_children = cte.queryset().with_cte(cte).values_list('entity_id').distinct()

    cohort_11ba_qs = CohortYear.objects.filter(
        name=CohortName.FIRST_YEAR.name,
        education_group_year=OuterRef("id")
    )

    offer_years = EducationGroupYear.objects.filter(
        management_entity_id__in=entity_ids_with_children,
        acronym__icontains=acronym,
        education_group_type__category=Categories.TRAINING.name,
        academic_year=academic_year.current_academic_year()
    ).exclude(
        Q(acronym__icontains="common-") | Q(acronym__icontains="11BA"),
    ).select_related(
        'education_group',
        'management_entity',
        'academic_year',
    ).annotate(
        has_11ba=Exists(cohort_11ba_qs)
    ).order_by(
        'acronym'
    )
    return EducationGroupYearQueryset.annotate_entity_requirement_acronym(offer_years)


def convert_queryset_to_dto(qs) -> List[OfferSearchDTO]:
    result = []

    for egy_obj in qs:
        result.append(
            OfferSearchDTO(
                acronym=egy_obj.acronym,
                title=egy_obj.title,
                management_entity_acronym=egy_obj.management_entity_acronym
            )
        )
        if egy_obj.has_11ba:
            result.append(
                OfferSearchDTO(
                    acronym=egy_obj.acronym.replace("1BA", "11BA"),
                    title=convert_title_to_first_year_bachelor_title(egy_obj.title),
                    management_entity_acronym=egy_obj.management_entity_acronym
                )
            )

    return result


# fixme move to proper file
def convert_title_to_first_year_bachelor_title(title: str) -> str:
    uncapitalize_title = title[0].lower() + title[1:]
    return "Première année de {}".format(uncapitalize_title)
