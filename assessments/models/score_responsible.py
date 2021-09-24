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

from osis_common.models.osis_model_admin import OsisModelAdmin


class ScoreResponsibleAdmin(OsisModelAdmin):
    list_display = ('learning_unit_year', 'learning_class_year', 'tutor')
    search_fields = [
        'learning_unit_year__acronym',
        'learning_class_year__acronym',
    ]
    list_filter = (
        'learning_unit_year__academic_year',
    )


class ScoreResponsible(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    tutor = models.ForeignKey('base.Tutor', on_delete=models.PROTECT)
    learning_unit_year = models.ForeignKey('base.LearningUnitYear', on_delete=models.CASCADE)
    learning_class_year = models.ForeignKey(
        'learning_unit.LearningClassYear',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    objects = models.Manager()

    def __str__(self):
        return "{}{} - {}".format(self.learning_unit_year, self.learning_class_year or "", self.tutor)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['learning_unit_year', 'learning_class_year'],
                name='unique_score_responsible'
            )
        ]
