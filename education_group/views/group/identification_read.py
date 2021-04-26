##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db.models import Case, When, Value, BooleanField, Q
from reversion.models import Version

from base.models.academic_year import AcademicYear
from base.models.entity_version import EntityVersion
from education_group.models.group_year import GroupYear
from education_group.views.group.common_read import Tab, GroupRead


class GroupReadIdentification(GroupRead):
    template_name = "education_group_app/group/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "history": self.get_related_history(),
            "active_management_entity": self.is_entity_active(self.get_group().management_entity.acronym),
        }

    def get_related_history(self):
        group_year = self.get_group_year()
        versions = Version.objects.get_for_object(
            group_year
        ).select_related('revision__user__person')

        related_models = [
            GroupYear,
        ]

        subversion = Version.objects.none()
        for model in related_models:
            subversion |= Version.objects.get_for_model(model).select_related('revision__user__person')

        versions |= subversion.filter(
            serialized_data__contains="\"group_year\": {}".format(group_year.pk)
        )

        return versions.order_by('-revision__date_created').distinct('revision__date_created')

    def is_entity_active(self, acronym_entity: str) -> bool:
        academic_year = AcademicYear.objects.get(year=self.get_group().year)
        current_clause = (
            Q(start_date__range=[academic_year.start_date, academic_year.end_date]) |
            Q(end_date__range=[academic_year.start_date, academic_year.end_date]) |
            (
                Q(start_date__lte=academic_year.start_date) &
                (
                    Q(end_date__isnull=True) |
                    Q(end_date__gte=academic_year.end_date)
                )
            )
        )
        entity = EntityVersion.objects.filter(
            acronym=acronym_entity,
        ).annotate(
            active_entity_version=Case(
                When(current_clause, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('-start_date').first()
        return entity.active_entity_version if entity else None
