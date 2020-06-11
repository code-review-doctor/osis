##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings
from django.test import TestCase, RequestFactory
from rest_framework.reverse import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory
from base.tests.factories.prerequisite import PrerequisiteFactory
from base.tests.factories.prerequisite_item import PrerequisiteItemFactory
from education_group.api.serializers.learning_unit import EducationGroupRootsListSerializer
from education_group.api.serializers.learning_unit import LearningUnitYearPrerequisitesListSerializer
from education_group.api.views.learning_unit import LearningUnitPrerequisitesList
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory


class EducationGroupRootsListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.training = TrainingFactory(
            acronym='BIR1BA',
            partial_acronym='LBIR1000I',
            academic_year=cls.academic_year,
        )
        cls.version = EducationGroupVersionFactory(offer=cls.training)
        url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': cls.training.acronym,
            'year': cls.academic_year.year
        })
        cls.serializer = EducationGroupRootsListSerializer(cls.version, context={
            'request': RequestFactory().get(url),
            'language': settings.LANGUAGE_CODE_EN
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'title',
            'url',
            'acronym',
            'code',
            'credits',
            'decree_category',
            'decree_category_text',
            'duration',
            'duration_unit',
            'duration_unit_text',
            'education_group_type',
            'education_group_type_text',
            'academic_year',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.academic_year.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_type'],
            self.training.education_group_type.name
        )


class LearningUnitYearPrerequisitesListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prerequisite = PrerequisiteFactory(learning_unit_year__acronym="LDROI1000")
        cls.prerequisite_item = PrerequisiteItemFactory(prerequisite=cls.prerequisite)
        url_kwargs = {
            'acronym': cls.prerequisite.learning_unit_year.acronym,
            'year': cls.prerequisite.learning_unit_year.academic_year.year
        }
        url = reverse('learning_unit_api_v1:' + LearningUnitPrerequisitesList.name, kwargs=url_kwargs)
        cls.serializer = LearningUnitYearPrerequisitesListSerializer(
            cls.prerequisite,
            context={
                'request': RequestFactory().get(url),
                'language': settings.LANGUAGE_CODE_EN
            },

        )

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'title',
            'acronym',
            'code',
            'academic_year',
            'education_group_type',
            'education_group_type_text',
            'prerequisites'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.prerequisite.education_group_year.academic_year.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_type'],
            self.prerequisite.education_group_year.education_group_type.name
        )
