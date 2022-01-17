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
from django.utils.translation import gettext_lazy as _

from base.models.academic_year import AcademicYear
from base.models.person import Person
from osis_profile.models.enums.education import (
    BelgianCommunitiesOfEducation,
    DiplomaResults,
    EducationalType,
    Equivalence,
    ForeignDiplomaTypes,
    LanguageKnowledgeGrade,
)
from reference.models.country import Country
from reference.models.language import Language


class Schedule(models.Model):
    # ancient language
    latin = models.PositiveIntegerField(_("Latin"), default=0)
    greek = models.PositiveIntegerField(_("Greek"), default=0)
    # sciences
    chemistry = models.PositiveIntegerField(_("Chemistry"), default=0)
    physic = models.PositiveIntegerField(_("Physic"), default=0)
    biology = models.PositiveIntegerField(_("Biology"), default=0)
    # modern languages
    german = models.PositiveIntegerField(_("German"), default=0)
    dutch = models.PositiveIntegerField(_("Dutch"), default=0)
    english = models.PositiveIntegerField(_("English"), default=0)
    french = models.PositiveIntegerField(_("french"), default=0)
    modern_languages_other_label = models.CharField(
        _("Other"),
        max_length=25,
        default="",
        help_text=_("If other language, please specify"),
        blank=True,
    )
    modern_languages_other_hours = models.PositiveIntegerField(null=True, blank=True)
    # other disciplines
    mathematics = models.PositiveIntegerField(_("Mathematics"), default=0)
    it = models.PositiveIntegerField(_("IT"), default=0)
    social_sciences = models.PositiveIntegerField(_("Social sciences"), default=0)
    economic_sciences = models.PositiveIntegerField(_("Economic sciences"), default=0)
    other_label = models.CharField(
        _("Other"),
        max_length=25,
        default="",
        help_text=_("If other optional domains, please specify"),
        blank=True,
    )
    other_hours = models.PositiveIntegerField(null=True, blank=True)


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
    educational_type = models.CharField(
        _("What type of education did (do) you follow?"),
        choices=EducationalType.choices(),
        max_length=50,
        null=True,
        blank=True,
    )
    educational_other = models.CharField(
        _("Other education, to specify"),
        max_length=50,
        default="",
        blank=True,
    )
    course_repeat = models.BooleanField(
        _("Did you repeat certain study years during your studies?"), default=False
    )
    course_orientation = models.BooleanField(
        _("Did you change of orientation during your studies?"), default=False
    )
    # TODO change by a FK when we got the related service to look for institutes
    institute = models.CharField(_("Institute"), default="", blank=True, max_length=25)
    other_institute = models.CharField(
        _("Another institute"),
        max_length=500,
        default="",
        help_text=_(
            "In case you could not find your institute in the list, please mention it "
            "below. "
        ),
        blank=True,
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
        max_length=50,
        null=True,
    )
    linguistic_regime = models.ForeignKey(
        Language,
        verbose_name=_("Linguistic regime"),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    other_linguistic_regime = models.CharField(
        _("If other linguistic regime, please clarify"),
        max_length=25,
        default="",
        blank=True,
    )
    country = models.ForeignKey(
        Country,
        verbose_name=_("Organizing country"),
        on_delete=models.CASCADE,
        related_name="+",
    )
    equivalence = models.CharField(
        _("Is this diploma subject to an equivalence decision by the services of the French community of Belgium?"),
        choices=Equivalence.choices(),
        max_length=25,
        null=True,
    )


class LanguageKnowledge(models.Model):
    person = models.ForeignKey(
        Person,
        verbose_name=_("Person"),
        on_delete=models.CASCADE,
        related_name="languages_knowledge",
        null=True,
    )
    language = models.ForeignKey(
        Language,
        verbose_name=_("Language"),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    listening_comprehension = models.CharField(
        _("Please rate your listening comprehension"),
        choices=LanguageKnowledgeGrade.choices(),
        max_length=25,
        null=True,
    )
    speaking_ability = models.CharField(
        _("Please rate your speaking ability"),
        choices=LanguageKnowledgeGrade.choices(),
        max_length=25,
        null=True,
    )
    writing_ability = models.CharField(
        _("Please rate your writing ability"),
        choices=LanguageKnowledgeGrade.choices(),
        max_length=25,
        null=True,
    )

    class Meta:
        unique_together = ("person", "language")
