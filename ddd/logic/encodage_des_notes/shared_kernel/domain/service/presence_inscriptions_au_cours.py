##############################################################################
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
##############################################################################

from django.db.models import Case, When, Q, F
from django.db.models.functions import Concat

from base.models.enums.offer_enrollment_state import SUBSCRIBED, PROVISORY
from base.models.learning_unit_enrollment import LearningUnitEnrollment
from ddd.logic.encodage_des_notes.shared_kernel.validator.exceptions import AucuneInscriptionAuCoursException
from osis_common.ddd import interface


class PresenceInscriptionsAuCours(interface.DomainService):

    @classmethod
    def verifier(
            cls,
            year: int,
            learning_unit_code: str
    ) -> None:
        enrollments_existence = LearningUnitEnrollment.objects.filter(
            learning_unit_year__academic_year__year=year,
            learning_unit_year__acronym__contains=learning_unit_code[:-1],
            offer_enrollment__enrollment_state__in=[SUBSCRIBED, PROVISORY]
        ).annotate(
            learning_unit_acronym=Case(
                When(
                    Q(learning_class_year__isnull=False),
                    then=Concat(F('learning_unit_year__acronym'), F('learning_class_year__acronym'))
                ),
                default=F('learning_unit_year__acronym')
            )
        ).filter(
            learning_unit_acronym=learning_unit_code,
        ).select_related(
            'learning_unit_year__academic_year',
        ).exists()

        if not enrollments_existence:
            raise AucuneInscriptionAuCoursException()
