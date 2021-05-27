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
from osis_common.models.osis_model_admin import OsisModelAdmin


class FirstYearBachelorAdmin(VersionAdmin, OsisModelAdmin):
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


class FirstYearBachelor(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    education_group_year = models.OneToOneField(
        'base.EducationGroupYear',
        verbose_name=_("Training"),
        on_delete=models.CASCADE,
        db_index=True,
        primary_key=True
    )

    administration_entity = models.ForeignKey(
        Entity,
        null=True,
        blank=True,
        verbose_name=_("Administration entity"),
        related_name='first_year_administration_entity',
        on_delete=models.PROTECT
    )
