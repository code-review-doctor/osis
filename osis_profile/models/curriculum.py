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
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base.models.academic_year import AcademicYear
from base.models.person import Person
from osis_document.contrib.fields import FileField
from osis_profile.models.enums.curriculum import ExperienceType, StudySystem, Result, Grade, CreditType,\
    ActivityType, ForeignStudyCycleType
from osis_profile.models.enums.education import BelgianCommunitiesOfEducation
from reference.models.language import Language


def curriculum_directory_path(curriculum_experience: 'Experience', filename: str):
    """Return the file upload directory path."""
    return '{}/curriculum/{}'.format(
        curriculum_experience.curriculum_year.person.uuid,
        filename,
    )


class CurriculumYear(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        null=True,
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name=_("Academic year"),
        related_name="+",
    )

    class Meta:
        unique_together = ["person", "academic_year"]
        ordering = ["-academic_year__year"]


class Experience(models.Model):
    # Common
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )
    curriculum_year = models.ForeignKey(
        CurriculumYear,
        on_delete=models.CASCADE,
        related_name="experiences",
    )
    type = models.CharField(
        _("Type"),
        choices=ExperienceType.choices(),
        max_length=50,
    )
    country = models.ForeignKey(
        'reference.Country',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('Country'),
    )
    institute_name = models.CharField(
        _("Institute name"),
        blank=True,
        max_length=255,
        null=True,
    )
    institute_city = models.CharField(
        _("Institute city"),
        blank=True,
        null=True,
        max_length=255,
    )
    # Common university higher education
    institute = models.ForeignKey(
        'base.organization',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Institute"),
    )
    institute_postal_code = models.CharField(
        _("Institute postal code"),
        blank=True,
        max_length=20,
        null=True,
    )
    education_name = models.CharField(
        _("Education name"),
        blank=True,
        max_length=255,
        null=True,
    )
    result = models.CharField(
        _("Result"),
        blank=True,
        choices=Result.choices(),
        default="",
        max_length=50,
        null=True,
    )
    graduation_year = models.BooleanField(
        _('Is it your graduation year?'),
        blank=True,
        null=True,
    )
    obtained_grade = models.CharField(
        _('Obtained grade'),
        blank=True,
        choices=Grade.choices(),
        default="",
        max_length=50,
        null=True,
    )
    rank_in_diploma = models.CharField(
        _('Rank in diploma'),
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
        default="",
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
        blank=True,
        mimetypes=['application/pdf'],
        null=True,
        upload_to=curriculum_directory_path,
        verbose_name=_('Transcript'),
    )
    graduate_degree = FileField(
        blank=True,
        mimetypes=['application/pdf'],
        null=True,
        upload_to=curriculum_directory_path,
        verbose_name=_('Graduate degree'),
    )
    access_certificate_after_60_master = FileField(
        blank=True,
        mimetypes=['application/pdf'],
        null=True,
        upload_to=curriculum_directory_path,
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
        blank=True,
        mimetypes=['application/pdf'],
        null=True,
        upload_to=curriculum_directory_path,
        verbose_name=_('Dissertation summary'),
    )
    # Belgian higher education
    belgian_education_community = models.CharField(
        _("Education community"),
        blank=True,
        choices=BelgianCommunitiesOfEducation.choices(),
        default="",
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
        choices=StudySystem.choices(),
        default="",
        null=True,
        max_length=50,
    )
    # Foreign higher education
    study_cycle_type = models.CharField(
        _("Study cycle type"),
        blank=True,
        choices=ForeignStudyCycleType.choices(),
        default="",
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
        blank=True,
        mimetypes=['application/pdf'],
        null=True,
        upload_to=curriculum_directory_path,
        verbose_name=_('Transcript translation'),
    )
    graduate_degree_translation = FileField(
        blank=True,
        mimetypes=['application/pdf'],
        null=True,
        verbose_name=_('Graduate degree translation'),
    )
    # Other activity
    activity_type = models.CharField(
        _('Activity type'),
        blank=True,
        choices=ActivityType.choices(),
        default="",
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
        blank=True,
        mimetypes=['application/pdf'],
        null=True,
        upload_to=curriculum_directory_path,
        verbose_name=_('Activity certificate'),
    )
    activity_position = models.CharField(
        _('Activity position'),
        blank=True,
        max_length=255,
        null=True,
    )

    def save(self, *args, **kwargs):
        previous_curriculum_year = Experience.objects.get(pk=self.pk).curriculum_year if self.pk else None
        super().save(*args, **kwargs)
        if previous_curriculum_year and previous_curriculum_year.experiences.count() == 0:
            # Remove the empty curriculum year
            previous_curriculum_year.delete()


@receiver(models.signals.post_delete, sender=Experience)
def delete_empty_curriculum_year(sender, instance, **kwargs):
    if instance.curriculum_year and instance.curriculum_year.experiences.count() == 0:
        # Remove the curriculum year as the experience to delete was its last experience
        instance.curriculum_year.delete()
