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
from django.core import validators
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from assessments.models.score_responsible import ScoreResponsible
from osis_common.models.osis_model_admin import OsisModelAdmin

MIN_ALLOCATION_CHARGE = 0


class AttributionClassAdmin(OsisModelAdmin):
    list_display = ('attribution_charge', 'learning_class_year', 'allocation_charge')
    search_fields = ['attribution_charge__attribution__tutor__person__first_name',
                     'attribution_charge__attribution__tutor__person__last_name',
                     'attribution_charge__attribution__tutor__person__global_id',
                     'learning_class_year__learning_component_year__learning_unit_year__acronym',
                     'attribution_charge__attribution__function']
    list_filter = (
        'learning_class_year__learning_component_year__type',
        'attribution_charge__attribution__learning_container_year__academic_year'
    )


class AttributionClass(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    attribution_charge = models.ForeignKey('AttributionChargeNew', on_delete=models.CASCADE)
    learning_class_year = models.ForeignKey('learning_unit.LearningClassYear', on_delete=models.CASCADE)
    allocation_charge = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[validators.MinValueValidator(MIN_ALLOCATION_CHARGE)]
    )
    objects = models.Manager()

    def __str__(self):
        return "{} - {}".format(
            self.attribution_charge,
            self.learning_class_year
        )


@receiver(post_delete, sender=AttributionClass)
def _attribution_class_delete(sender, instance, **kwargs):
    if AttributionClass.objects.filter(
            attribution_charge__attribution__tutor=instance.attribution_charge.attribution.tutor,
            learning_class_year=instance.learning_class_year
    ).count() == 0:
        ScoreResponsible.objects.filter(
            learning_class_year=instance.learning_class_year,
            tutor=instance.attribution_charge.attribution.tutor).delete()
