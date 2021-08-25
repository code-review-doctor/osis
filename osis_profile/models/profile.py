# ##############################################################################
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
# ##############################################################################

from django.db import models

from osis_document.contrib import FileField
from osis_profile.models import FILE_MAX_SIZE


class Profile(models.Model):
    person = models.OneToOneField('base.Person', on_delete=models.CASCADE)

    id_photo = FileField(
        mimetypes=['image/jpeg', 'image/png'],
        max_size=FILE_MAX_SIZE,
        max_files=1,
        min_files=1,
    )
    birth_year = models.IntegerField(null=True)
    birth_place = models.CharField(max_length=255, default='')
    national_number = models.CharField(max_length=255, default='')
    id_card_number = models.CharField(max_length=255, default='')
    passport_number = models.CharField(max_length=255, default='')
    passport_expiration_date = models.DateField(null=True)

    id_card = FileField(
        mimetypes=['image/jpeg', 'image/png', 'application/pdf'],
        max_size=FILE_MAX_SIZE,
        max_files=2,
        min_files=1,
    )
    passport = FileField(
        mimetypes=['image/jpeg', 'image/png', 'application/pdf'],
        max_size=FILE_MAX_SIZE,
        max_files=2,
        min_files=1,
    )

    iban = models.CharField(max_length=255, default='')
    bic_swift = models.CharField(max_length=255, default='')
    bank_holder_name = models.CharField(max_length=255, default='')

    last_registration_year = models.ForeignKey(
        'base.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
