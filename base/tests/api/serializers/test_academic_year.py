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
import datetime
from unittest.mock import Mock

from django.test import TestCase
from rest_framework import serializers

from base.api.serializers.academic_year import RelatedAcademicYearField
from base.tests.factories.academic_year import AcademicYearFactory


class AcademicYearSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.academic_year = AcademicYearFactory(year=2021)

        class TestSerializer(serializers.Serializer):
            academic_year = RelatedAcademicYearField()

        self.serializer_class = TestSerializer

    def test_to_representation(self):
        serializer = self.serializer_class(instance=Mock(academic_year=self.academic_year))

        self.assertEqual(serializer.data, {'academic_year': 2021})

    def test_to_internal_value(self):
        data = {'academic_year': 2021}
        serializer = self.serializer_class(data=data)

        serializer.is_valid()
        self.assertEqual(serializer.validated_data.get("academic_year"), self.academic_year)
