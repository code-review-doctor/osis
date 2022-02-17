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
from datetime import datetime

from django.db.models import Q, F, Case, When, Value, CharField
from django.db.models.functions import Replace
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from base.auth.roles.program_manager import ProgramManager
from base.models.entity_version import EntityVersion
from base.models.enums.entity_type import FACULTY
from base.models.person import Person
from education_group.auth.roles.central_manager import CentralManager
from education_group.auth.roles.faculty_manager import FacultyManager
from education_group.auth.scope import Scope
from education_group.models.enums.cohort_name import CohortName
from osis_role.contrib.helper import EntityRoleHelper


class PersonDetailSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = Person
        fields = (
            'first_name',
            'last_name',
            'email',
            'gender',
            'uuid',
            'birth_date'
        )


class PersonRolesSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = (
            'global_id',
            'roles'
        )

    def get_roles(self, obj):
        roles = {
            'reddot': {
                'description': _('General information and Access requirements'),
                'scope': self.roles_for_reddot(obj)
            },
            'program_manager': {
                'description': _('Program manager'),
                'scope': self.roles_for_program_managers(obj)
            }
        }
        return roles

    @staticmethod
    def roles_for_reddot(obj):
        all_entities = EntityRoleHelper.get_all_entities(obj, {CentralManager.group_name, FacultyManager.group_name})
        all_faculties = set(
            row.acronym for row in EntityVersion.objects.current(datetime.now()).filter(
                entity_id__in=all_entities
            ).filter(
                Q(entity_type=FACULTY) | Q(acronym__iexact=Scope.IUFC.name)
            )
        )

        if CentralManager.objects.filter(person=obj, scopes__contains=[Scope.IUFC.name]).exists() | \
                FacultyManager.objects.filter(person=obj, scopes__contains=[Scope.IUFC.name]).exists():
            all_faculties.add(Scope.IUFC.name)
        return all_faculties

    @staticmethod
    def roles_for_program_managers(obj):
        return [
            {'acronym': program_manager.acronym}
            for program_manager in ProgramManager.objects.filter(person=obj).annotate(
                acronym=Case(
                    When(
                        Q(cohort=CohortName.FIRST_YEAR.name),
                        then=Replace('education_group__educationgroupyear__acronym', Value('1'), Value('11'))
                    ),
                    default=F('education_group__educationgroupyear__acronym'),
                    output_field=CharField()
                ),
            )
        ]
