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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.shortcuts import get_object_or_404

from base.models.admission_condition import AdmissionCondition
from base.models.education_group_year import EducationGroupYear


class AccessRequirementsMixin:
    def get_permission_required(self):
        if self.get_permission_object().is_common:
            return ('base.change_commonadmissioncondition',)
        return ('base.change_admissioncondition',)

    def get_admission_condition_object(self) -> 'AdmissionCondition':
        try:
            return AdmissionCondition.objects.get(
                education_group_year__partial_acronym=self.kwargs["code"],
                education_group_year__academic_year__year=self.kwargs['year']
            )
        except AdmissionCondition.DoesNotExist:
            egy = get_object_or_404(
                EducationGroupYear,
                partial_acronym=self.kwargs["code"],
                academic_year__year=self.kwargs["year"],
            )

            obj, created = AdmissionCondition.objects.get_or_create(
                education_group_year=egy
            )
            return obj
