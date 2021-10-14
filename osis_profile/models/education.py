# ##############################################################################
#
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
#
# ##############################################################################
from django.db import models
from django.utils.translation import gettext as _

from base.models.academic_year import AcademicYear
from base.models.person import Person
from osis_profile.models.enums.education import (
    DiplomaResults,
    BelgianCommunitiesOfEducation,
    EducationalTransition,
    EducationalQualification,
    ForeignDiplomaTypes,
)
from reference.models.country import Country


class Schedule(models.Model):
    # ancient language
    latin = models.PositiveIntegerField(_("Latin"))
    greek = models.PositiveIntegerField(_("Greek"))
    # sciences
    chemistry = models.PositiveIntegerField(_("Chemistry"))
    physic = models.PositiveIntegerField(_("Physic"))
    biology = models.PositiveIntegerField(_("Biology"))
    # modern languages
    german = models.PositiveIntegerField(_("German"))
    dutch = models.PositiveIntegerField(_("Dutch"))
    english = models.PositiveIntegerField(_("English"))
    french = models.PositiveIntegerField(_("french"))
    modern_languages_other_label = models.CharField(
        _("Other"),
        max_length=25,
        default="",
        help_text=_("If other language, please specify"),
    )
    modern_languages_other_hours = models.PositiveIntegerField(null=True)
    # other disciplines
    mathematics = models.PositiveIntegerField(_("Mathematics"))
    it = models.PositiveIntegerField(_("IT"))
    social_sciences = models.PositiveIntegerField(_("Social sciences"))
    economic_sciences = models.PositiveIntegerField(_("Economic sciences"))
    other_label = models.CharField(
        _("Other"),
        max_length=25,
        default="",
        help_text=_("If other optional domains, please specify"),
    )
    other_hours = models.PositiveIntegerField(null=True)


class HighSchoolDiploma(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, null=True)
    academic_graduation_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name=_("Please mention the academic graduation year"),
        related_name="+",
    )
    result = models.CharField(
        _("At which result level do you consider yourself?"),
        choices=DiplomaResults.choices(),
        max_length=25,
        null=True,
    )

    class Meta:
        abstract = True


class BelgianHighSchoolDiploma(HighSchoolDiploma):
    community = models.CharField(
        _("In what Community did (do) you follow last year of high school?"),
        choices=BelgianCommunitiesOfEducation.choices(),
        max_length=25,
        null=True,
    )
    educational_transition = models.CharField(
        _("Educational transition"),
        choices=EducationalTransition.choices(),
        max_length=50,
        null=True,
    )
    educational_qualification = models.CharField(
        _("Educational qualification"),
        choices=EducationalQualification.choices(),
        max_length=50,
        null=True,
    )
    educational_other = models.CharField(
        _("Other education, to specify"),
        max_length=50,
        default="",
    )
    course_repeat = models.BooleanField(
        _("Did you repeat certain study years during your studies?"), null=True
    )
    course_orientation = models.BooleanField(
        _("Did you change of orientation during your studies?"), null=True
    )
    # TODO Does all of the institute details come from an other table?
    institute_community = models.CharField(_("Community"), max_length=25, null=True)
    institute_postal_code = models.CharField(_("Postal code"), max_length=25, null=True)
    institute_name = models.CharField(_("Institute"), max_length=25, null=True)
    other_institute_name = models.CharField(
        _("Another institute"),
        max_length=500,
        default="",
        help_text=_(
            "In case you could not find your institute in the list, please mention it "
            "below. "
        ),
    )
    schedule = models.OneToOneField(
        Schedule,
        on_delete=models.CASCADE,
        help_text=_(
            "Please complete here below the schedule of your last year of high "
            "school, indicating for each domain the number of hours of education "
            "followed per week (h/w). "
        ),
        null=True,
    )


class ForeignHighSchoolDiploma(HighSchoolDiploma):
    foreign_diploma_type = models.CharField(
        _("What diploma did you get (or will you get)?"),
        choices=ForeignDiplomaTypes.choices(),
        max_length=25,
        null=True,
    )
    linguistic_regime = models.CharField(
        _("Linguistic regime"), max_length=25, default=""
    )
    other_linguistic_regime = models.CharField(
        _("If other linguistic regime, please clarify"),
        max_length=25,
        default="",
    )
    country = models.ForeignKey(
        Country,
        verbose_name=_("Organizing country"),
        on_delete=models.CASCADE,
        related_name="+",
    )
