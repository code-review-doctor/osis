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


class CurriculumYear(models.Model):
    person = models.ForeignKey('base.Person', on_delete=models.CASCADE)
    year_type = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    belgian_community = models.CharField(null=True, max_length=250)
    domain = models.ForeignKey('reference.DomainIsced', on_delete=models.SET_NULL, null=True)
    studies = models.ForeignKey('base.EducationGroupType', on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey('base.EducationGroup', on_delete=models.SET_NULL, null=True)
    other_program = models.CharField(default='', max_length=250)
    result = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    obtained_diploma = models.BooleanField(default=False)
    grade = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    rank = models.CharField(default='', max_length=250)

    marks_file = FileField(
        mimetypes=['application/pdf'],
        max_size=FILE_MAX_SIZE,

    )

    diploma_title = models.CharField(default='', max_length=250)

    essay_title = models.CharField(default='', max_length=250)
    essay_summary = models.CharField(default='', max_length=250)
    essay_mark = models.DecimalField(decimal_places=2, max_digits=5)
    credits_type = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    credits_registered = models.PositiveSmallIntegerField(default=0)
    credits_acquired = models.PositiveSmallIntegerField(default=0)
    belgian_school = models.ForeignKey('base.Entity', on_delete=models.SET_NULL, null=True)

    # Foreign-specific higher education
    cycle = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    school_country = models.ForeignKey('reference.Country', on_delete=models.SET_NULL, null=True)
    school_locality = models.CharField(default='', max_length=250)
    school_zipcode = models.CharField(default='', max_length=250)
    other_school = models.CharField(default='', max_length=250)
    delivery_date = models.DateField(null=True)
    attestation = FileField(
        mimetypes=['application/pdf'],
        max_size=FILE_MAX_SIZE,

    )

    # Belgian non-higher education
    studies_type = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    studies_system = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)

    # Other types
    activity_type = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    other_activity_type = models.CharField(default='', max_length=250)
    activity_location = models.CharField(default='', max_length=250)
