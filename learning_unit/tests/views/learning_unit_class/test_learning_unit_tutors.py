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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase
import mock

from attribution.models.enums.function import HOLDER
from base.models.enums.component_type import LECTURING, PRACTICAL_EXERCISES
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.tests.factory.effective_class import LecturingEffectiveClassFactory
from learning_unit.views.learning_unit_class.learning_unit_tutors import _filter_tutors_by_class_type


class LearningUnitTutors(TestCase):

    def setUp(self):
        self.lecturing_effective_class = LecturingEffectiveClassFactory()

    @mock.patch("ddd.logic.attribution.use_case.read.search_attributions_to_learning_unit_service."
                "search_attributions_to_learning_unit")
    def test_filter_tutors_by_class_type(self, mock_tutors):
        tutor_attribution_to_learning_unit_dto_lecturing = self._build_tutor_attribution_to_learning_unit_DTO(
            LECTURING,
            "1"
        )
        tutor_attribution_to_learning_unit_dto_practical = self._build_tutor_attribution_to_learning_unit_DTO(
            PRACTICAL_EXERCISES,
            "2"
        )

        mock_tutors.return_value = [
            tutor_attribution_to_learning_unit_dto_lecturing,
            tutor_attribution_to_learning_unit_dto_practical
        ]

        tutors_result_for_view = _filter_tutors_by_class_type(self.lecturing_effective_class, mock_tutors.return_value)
        self.assertCountEqual(tutors_result_for_view, [tutor_attribution_to_learning_unit_dto_lecturing])

    def _build_tutor_attribution_to_learning_unit_DTO(self, component_type: str, attribution_uuid: str):
        return TutorAttributionToLearningUnitDTO(
            learning_unit_code=self.lecturing_effective_class.entity_id.learning_unit_identity.code,
            learning_unit_year=self.lecturing_effective_class.entity_id.learning_unit_identity.academic_year.year,
            attribution_uuid=attribution_uuid,
            last_name="Martin",
            first_name="Tom",
            personal_id_number="0123",
            function=HOLDER,
            attributed_volume_to_learning_unit=10,
            component_type=component_type,
            classes=[]
        )


