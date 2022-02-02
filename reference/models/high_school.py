##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid

from django.db import models
from django.utils import timezone

from osis_common.models import osis_model_admin


class HighSchoolAdmin(osis_model_admin.OsisModelAdmin):
    list_display = ('organization', 'zip_code', 'start_year', 'end_year',)
    list_filter = ('zip_code', 'linguistic_regime',)
    ordering = ('organization__name', 'zip_code', 'start_year', 'end_year',)
    search_fields = ['organization', 'zip_code']


class HighSchool(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    organization = models.OneToOneField('base.Organization', blank=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=255, default='')
    start_year = models.IntegerField()
    end_year = models.IntegerField(blank=True, null=True)
    linguistic_regime = models.ForeignKey(
        'Language',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to={'code__in': ['FR', 'NL']}
    )
    # TODO: if zipcode table is not complete, use char field for zip code and locality
    zip_code = models.ForeignKey('ZipCode', on_delete=models.CASCADE, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True)
    street_number = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=30, blank=True, choices=[], default='')

    changed = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return str(self.organization)

    class Meta:
        ordering = ('organization__name',)

    @property
    def active(self):
        current_year = timezone.now().year
        return current_year <= self.end_year or self.end_year is None
