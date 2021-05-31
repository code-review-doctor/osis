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
from django.db import models
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from base.models.entity import Entity
from education_group.models.enums.cohort_name import CohortName
from osis_common.models.osis_model_admin import OsisModelAdmin
from osis_common.models.serializable_model import SerializableModel, SerializableModelManager, SerializableQuerySet


class CohortYearAdmin(VersionAdmin, OsisModelAdmin):
    list_display = (
        'education_group_year',
        'administration_entity',
        'changed'
    )
    list_filter = ('education_group_year__academic_year',)
    search_fields = [
        'education_group_year__acronym',
        'education_group_year__partial_acronym'
    ]
    raw_id_fields = (
        'education_group_year', 'administration_entity'
    )


class CohortYearQueryset(SerializableQuerySet):
    def get_queryset(self):
        return self.get_queryset().select_related(
            'administration_entity',
            'education_group_year'
        ).prefetch_related(
            'administration_entity.entityversion_set'
        )


class CohortYearManager(SerializableModelManager):
    def get_queryset(self):
        return CohortYearQueryset(self.model, using=self._db)

    def get_first_year_bachelor(self, **kwargs):
        return self.get(name=CohortName.FIRST_YEAR.name, **kwargs)


class CohortYear(SerializableModel):
    objects = CohortYearManager()
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    education_group_year = models.ForeignKey(
        'base.EducationGroupYear',
        verbose_name=_("Training"),
        on_delete=models.PROTECT,
        db_index=True,
    )

    administration_entity = models.ForeignKey(
        Entity,
        null=True,
        blank=True,
        verbose_name=_("Administration entity"),
        related_name='cohort_year_administration_entity',
        on_delete=models.PROTECT
    )

    name = models.CharField(
        max_length=25,
        choices=CohortName.choices(),
        default=CohortName.FIRST_YEAR.name,
        verbose_name=_('Name'),
    )

    class Meta:
        verbose_name = _("Cohort year")
        constraints = [
            models.UniqueConstraint(fields=['education_group_year', 'name'], name='unique_education_group_year_cohort')
        ]
