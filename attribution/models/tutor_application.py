##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from attribution.models.enums.function import Functions


class TutorApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'tutor',
        'function',
        'learning_container_year',
        'volume_lecturing',
        'volume_pratical_exercice',
        'changed',
    )
    list_filter = ('learning_container_year__academic_year', )
    fieldsets = ((None, {'fields': ('last_changed', 'learning_container_year',
                                    'tutor', 'function', 'volume_lecturing', 'volume_pratical_exercice',
                                    'remark', 'course_summary')}),)
    raw_id_fields = ('learning_container_year', 'tutor')
    search_fields = ['tutor__person__first_name', 'tutor__person__last_name', 'learning_container_year__acronym',
                     'tutor__person__global_id', 'function']


class TutorApplication(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    learning_container_year = models.ForeignKey('base.LearningContainerYear', on_delete=models.PROTECT)
    tutor = models.ForeignKey('base.Tutor', on_delete=models.CASCADE)
    function = models.CharField(max_length=35, blank=True, null=True, choices=Functions.choices(), db_index=True)
    volume_lecturing = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    volume_pratical_exercice = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    course_summary = models.TextField(blank=True, null=True)
    last_changed = models.DateTimeField(null=True)

    def __str__(self):
        return u"%s - %s" % (self.tutor, self.function)
