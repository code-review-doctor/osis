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
import uuid as uuid

from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from attribution.models.enums.decision_making import DecisionMakings
from attribution.models.enums.function import Functions


class AttributionNewAdmin(admin.ModelAdmin):

    list_display = ('tutor', 'score_responsible', 'function', 'learning_container_year', 'start_year', 'end_year',
                    'changed', 'substitute', 'decision_making')
    list_filter = ('learning_container_year__academic_year', 'score_responsible')
    fieldsets = ((None, {'fields': ('learning_container_year', 'tutor', 'function', 'score_responsible',
                                    'start_year', 'end_year', 'substitute', 'decision_making')}),)
    raw_id_fields = ('learning_container_year', 'tutor', 'substitute')
    search_fields = ['tutor__person__first_name', 'tutor__person__last_name', 'learning_container_year__acronym',
                     'tutor__person__global_id', 'function']


class AttributionNew(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    learning_container_year = models.ForeignKey('base.LearningContainerYear', on_delete=models.CASCADE)
    tutor = models.ForeignKey('base.Tutor', on_delete=models.CASCADE)
    function = models.CharField(max_length=35, choices=Functions.choices(), db_index=True, verbose_name=_("Function"))
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    start_year = models.IntegerField(blank=True, null=True, verbose_name=_("Start"))
    end_year = models.IntegerField(blank=True, null=True)
    score_responsible = models.BooleanField(default=False)
    substitute = models.ForeignKey('base.Person', blank=True, null=True, on_delete=models.CASCADE)
    decision_making = models.CharField(max_length=40, blank=True, null=False, choices=DecisionMakings.choices(),
                                       default='')

    def __str__(self):
        return u"%s - %s" % (self.tutor.person, self.function)

    @property
    def duration(self):
        if self.start_year and self.end_year:
            return (self.end_year - self.start_year) + 1
        return None
