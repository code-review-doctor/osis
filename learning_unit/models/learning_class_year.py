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
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models.enums import quadrimesters, learning_unit_year_session
from osis_common.models import osis_model_admin


class LearningClassYearAdmin(osis_model_admin.OsisModelAdmin):
    list_display = ('learning_component_year', 'acronym')
    search_fields = ['acronym', 'learning_component_year__learning_unit_year__acronym']


class LearningClassYearManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'learning_component_year',
            'learning_component_year__learning_unit_year'
        )


ALPHANUMERIC_REGEX = r'^[a-zA-Z0-9]$'
only_alphanumeric_validator = RegexValidator(ALPHANUMERIC_REGEX, _('Only alphanumeric characters are allowed.'))


class LearningClassYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    learning_component_year = models.ForeignKey(
        'base.LearningComponentYear',
        on_delete=models.CASCADE
    )
    acronym = models.CharField(max_length=1, validators=[only_alphanumeric_validator])
    description = models.CharField(max_length=100, blank=True)  # FIXME: to delete when classes development finished

    title_fr = models.CharField(max_length=255, blank=True, verbose_name=_('Title in French'))
    title_en = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Title in English'))

    hourly_volume_partial_q1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                                                   verbose_name=_("hourly volume partial q1"))
    hourly_volume_partial_q2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                                                   verbose_name=_("hourly volume partial q2"))
    quadrimester = models.CharField(max_length=9, blank=True, verbose_name=_('Quadrimester'), null=True,
                                    choices=quadrimesters.DerogationQuadrimester.choices())
    session = models.CharField(max_length=50, blank=True, null=True,
                               choices=learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION,
                               verbose_name=_('Session derogation'))

    campus = models.ForeignKey('base.Campus', verbose_name=_("Learning location"), on_delete=models.PROTECT)

    objects = LearningClassYearManager()

    def __str__(self):
        return u'{}{}-{}'.format(
            self.learning_component_year.learning_unit_year.acronym,
            self.acronym,
            self.learning_component_year.get_type_display()
        )

    @property
    def volume_annual(self):
        volume_total_of_classes = 0
        volume_total_of_classes += self.hourly_volume_partial_q1 or 0
        volume_total_of_classes += self.hourly_volume_partial_q2 or 0
        return volume_total_of_classes
