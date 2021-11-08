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

from admission.contrib.models import DoctorateAdmission
from base.models.academic_year import AcademicYear
from base.models.person import Person
from osis_profile.models.enums.curriculum import CourseTypes


class CurriculumYear(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
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
    curriculum_year = models.ForeignKey(CurriculumYear, on_delete=models.CASCADE, related_name="experiences")
    valuated_from = models.ForeignKey(
        DoctorateAdmission,
        verbose_name=_("Experience valuated from this accepted admission."),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    course_type = models.CharField(_("Course types"), max_length=50, choices=CourseTypes.choices())

    objects = ExperienceManager()
