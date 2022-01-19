# ##############################################################################
#
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from admission.contrib.models import DoctorateAdmission
from base.models.academic_year import AcademicYear
from base.models.person import Person
from osis_document.contrib.fields import FileField
from osis_profile.models.enums.curriculum import ExperienceTypes, StudySystems, Result, Grade, CreditType, \
    ForeignStudyCycle, ActivityTypes
from osis_profile.models.enums.education import BelgianCommunitiesOfEducation
from reference.models.language import Language


class CurriculumYear(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        null=True,
    )
    academic_graduation_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name=_("Academic graduation year"),
        related_name="+",
    )

    class Meta:
        unique_together = ["person", "academic_graduation_year"]
        ordering = ["-academic_graduation_year__year"]


class ExperienceManager(models.Manager):
    def get_queryset(self):
        """An experience is 'valuated' after an admission has been accepted."""
        return super().get_queryset().annotate(
            is_valuated=models.ExpressionWrapper(
                models.Q(valuated_from__isnull=False),
                output_field=models.BooleanField(),
            )
        )


class Experience(models.Model):
    # Common
    curriculum_year = models.ForeignKey(
        CurriculumYear,
        on_delete=models.CASCADE,
        related_name="experiences",
    )
    valuated_from = models.ForeignKey(
        DoctorateAdmission,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Experience valuated from this accepted admission."),
    )
    type = models.CharField(
        _("Type"),
        choices=ExperienceTypes.choices(),
        max_length=50,
    )
    country = models.ForeignKey(
        'reference.Country',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('Country'),
    )
    other_institute_name = models.CharField(
        _("Other institute name"),
        blank=True,
        max_length=255,
        null=True,
    )
    other_institute_city = models.CharField(
        _("Other institute city"),
        blank=True,
        null=True,
        max_length=255,
    )
    # Common university higher education
    institute = models.ForeignKey(
        'partnership.Partnership',  # TODO base.EntityVersion for belgian studies ?
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Institute"),
    )
    other_institute_postal_code = models.CharField(
        _("Other institute postal code"),
        blank=True,
        max_length=20,
        null=True,
    )
    program_name = models.CharField(
        _("Program name"),
        blank=True,
        max_length=255,
        null=True,
    )
    result = models.CharField(
        _("Result"),
        blank=True,
        choices=Result.choices(),
        max_length=50,
        null=True,
    )
    graduation_year = models.BooleanField(
        _('Is it the graduation year?'),
        blank=True,
        null=True,
    )
    obtained_grade = models.CharField(
        _('Obtained grade'),
        blank=True,
        choices=Grade.choices(),
        max_length=50,
        null=True,
    )
    diploma_ranked = models.CharField(
        _('Diploma ranked'),
        blank=True,
        max_length=255,
        null=True,
    )
    issue_diploma_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Issue diploma date'),
    )
    credit_type = models.CharField(
        _('Credit type'),
        blank=True,
        choices=CreditType.choices(),
        max_length=50,
        null=True,
    )
    entered_credits_number = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
        ],
        verbose_name=_('Entered credit number'),
    )
    acquired_credits_number = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
        ],
        verbose_name=_('Acquired credit number'),
    )
    transcript = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Transcript'),
    )
    graduate_degree = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Graduate degree'),
    )
    access_certificate_after_60_master = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Access certificate after a 60 master'),
    )
    dissertation_title = models.CharField(
        _('Dissertation title'),
        blank=True,
        max_length=255,
        null=True,
    )
    dissertation_score = models.DecimalField(
        decimal_places=2,
        blank=True,
        max_digits=4,
        null=True,
        verbose_name=_('Dissertation score'),
    )
    dissertation_summary = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Dissertation summary'),
    )
    # Belgian higher education
    belgian_education_community = models.CharField(
        _("Education community"),
        blank=True,
        choices=BelgianCommunitiesOfEducation.choices(),
        max_length=50,
        null=True,
    )
    program = models.ForeignKey(
        "base.EducationGroupYear",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Program"),
    )
    study_system = models.CharField(
        _("Study system"),
        blank=True,
        choices=StudySystems.choices(),
        null=True,
        max_length=50,
    )
    curriculum = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Curriculum'),
    )
    # Foreign higher education
    foreign_study_cycle = models.CharField(
        _("Foreign study cycle"),
        blank=True,
        choices=ForeignStudyCycle.choices(),
        max_length=50,
        null=True,
    )
    linguistic_regime = models.ForeignKey(
        Language,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Linguistic regime"),
    )
    transcript_translation = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Transcript translation'),
    )
    graduate_degree_translation = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Graduate degree translation'),
    )
    # Other occupation
    activity_type = models.CharField(
        _('Activity type'),
        blank=True,
        choices=ActivityTypes.choices(),
        max_length=50,
        null=True,
    )
    other_activity_type = models.CharField(
        _('Other activity type'),
        blank=True,
        max_length=255,
        null=True,
    )
    activity_certificate = FileField(
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Activity certificate'),
    )
    activity_position = models.CharField(
        _('Position'),
        blank=True,
        max_length=255,
        null=True,
    )
    objects = ExperienceManager()
