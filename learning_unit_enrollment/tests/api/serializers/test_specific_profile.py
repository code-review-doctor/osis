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

from django.test import TestCase

from base.models.enums.peps_type import PepsTypes, SportSubtypes, HtmSubtypes
from base.tests.factories.student_specific_profile import StudentSpecificProfileFactory
from learning_unit_enrollment.api.serializers.specific_profile import StudentSpecificProfileSerializer


class StudentSpecificProfileSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.profile = StudentSpecificProfileFactory(type=PepsTypes.ARTIST.name)

        cls.serializer = StudentSpecificProfileSerializer(cls.profile)

    def test_contains_expected_fields(self):
        expected_fields = [
            'type',
            'type_text',
            'subtype',
            'subtype_text',
            'guide',
            'arrangement_additional_time',
            'arrangement_appropriate_copy',
            'arrangement_other',
            'arrangement_specific_locale',
            'arrangement_comment'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_type_text_computed(self):
        self.assertEqual(self.serializer.data['type_text'], PepsTypes.get_value(self.profile.type))

    def test_ensure_subtype_computed_for_sport(self):
        profile = StudentSpecificProfileFactory(
            type=PepsTypes.SPORT.name,
            subtype_sport=SportSubtypes.PROMISING_ATHLETE.name
        )
        serializer = StudentSpecificProfileSerializer(profile)
        self.assertEqual(serializer.data['subtype'], profile.subtype_sport)
        self.assertEqual(serializer.data['subtype_text'], SportSubtypes.get_value(profile.subtype_sport))

    def test_ensure_subtype_computed_for_disability(self):
        profile = StudentSpecificProfileFactory(
            type=PepsTypes.DISABILITY.name,
            subtype_disability=HtmSubtypes.REDUCED_MOBILITY.name
        )
        serializer = StudentSpecificProfileSerializer(profile)
        self.assertEqual(serializer.data['subtype'], profile.subtype_disability)
        self.assertEqual(serializer.data['subtype_text'], HtmSubtypes.get_value(profile.subtype_disability))
