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
from django.db import models

from osis_common.models import osis_model_admin


class ZipCodeAdmin(osis_model_admin.OsisModelAdmin):
    list_display = ('zip_code', 'municipality', 'country')
    list_filter = ('country',)
    ordering = ('zip_code',)
    search_fields = ['municipality']


class ZipCode(models.Model):
    zip_code = models.CharField(max_length=4)
    municipality = models.CharField(max_length=80, unique=True)
    country = models.ForeignKey('Country', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.zip_code, self.municipality)

    class Meta:
        ordering = ('zip_code',)
