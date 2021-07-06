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

from osis_common.models.osis_model_admin import OsisModelAdmin


class ScoreResponsibleAdmin(OsisModelAdmin):
    list_display = ('learning_unit_year', 'attribution_class', 'attribution_charge')
    search_fields = [
        'learning_unit_year__acronym',
        'attribution_charge__attribution__tutor__person__last_name',
        'attribution_charge__attribution__tutor__person__global_id',
        'attribution_charge__attribution__function'
    ]
    list_filter = (
        'attribution_charge__attribution__learning_container_year__academic_year',
    )


class ScoreResponsible(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    learning_unit_year = models.ForeignKey('base.LearningUnitYear', on_delete=models.CASCADE)
    attribution_charge = models.ForeignKey(
        'attribution.AttributionChargeNew',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    attribution_class = models.ForeignKey(
        'attribution.AttributionClass',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    objects = models.Manager()

    def __str__(self):
        return "{} - {}".format(
            self.learning_unit_year,
            self.attribution_charge
        )

    def save(self, *args, **kwargs):
        self.__should_have_minimum_one_attribution()
        super().save(*args, **kwargs)

    def __should_have_minimum_one_attribution(self):
        #  TODO :: Question : est-ce correct?
        #  Pourrait-il y avoir une fk attributionchargenew et une fk attributionclass???
        if self.attribution_charge is None and self.attribution_class is None:
            raise AttributeError(_('Score responsible should be link to an attribution'))
