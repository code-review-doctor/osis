##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.business.entities import EntitiesHierarchyFactory
from base.tests.factories.entity_version import MainEntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.views.learning_units.search.search_test_mixin import TestRenderToExcelMixin


class TestExcelGeneration(TestRenderToExcelMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_years = AcademicYearFactory.produce()
        main_entity = MainEntityVersionFactory(parent=None)
        cls.luys = LearningUnitYearFactory.create_batch(
            4,
            academic_year__current=True,
            learning_container_year__requirement_entity=main_entity.entity
        )
        cls.url = reverse("learning_units_service_course")
        cls.get_data = {
            "academic_year": str(cls.luys[0].academic_year.id),
        }
        cls.tuples_xls_status_value_with_xls_method_function = (
            ("xls", "base.views.learning_units.search.common.create_xls"),
            ("xls_with_parameters", "base.views.learning_units.search.common.create_xls_with_parameters"),
            ("xls_attributions", "base.views.learning_units.search.common.create_xls_attributions"),
            ("xls_comparison", "base.views.learning_units.search.common.create_xls_comparison"),
            ("xls_educational_specifications",
             "base.views.learning_units.search.common.create_xls_educational_information_and_specifications"),
        )

        cls.person = PersonWithPermissionsFactory("can_access_learningunit")

    def setUp(self):
        self.client.force_login(self.person.user)


class TestFilter(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_years = AcademicYearFactory.produce()
        cls.academic_year = AcademicYearFactory(current=True)
        cls.entities_hierarchy = EntitiesHierarchyFactory()

        cls.person = PersonWithPermissionsFactory("can_access_learningunit")

        cls.url = reverse("learning_units_service_course")

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_should_not_return_learning_having_requirement_and_allocation_contained_in_same_faculty(self):
        luy = LearningUnitYearFactory(
            academic_year=self.academic_year,
            learning_container_year__requirement_entity=self.entities_hierarchy.faculty_1_1.entity,
            learning_container_year__allocation_entity=self.entities_hierarchy.school_1_1_1.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [],
        )

    def test_should_not_return_learning_having_same_requirement_and_allocation_entities(self):
        luy = LearningUnitYearFactory(
            academic_year=self.academic_year,
            learning_container_year__requirement_entity=self.entities_hierarchy.sector_1.entity,
            learning_container_year__allocation_entity=self.entities_hierarchy.sector_1.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [],
        )

    def test_should_return_learning_unit_having_different_faculties_for_requirement_and_allocation_entities(self):
        luy = LearningUnitYearFactory(
            academic_year=self.academic_year,
            learning_container_year__requirement_entity=self.entities_hierarchy.faculty_1_1.entity,
            learning_container_year__allocation_entity=self.entities_hierarchy.faculty_1_2.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [luy],
            transform=lambda obj: obj
        )

    def test_should_return_learning_unit_having_requirement_and_allocation_contained_in_different_faculties(self):
        luy = LearningUnitYearFactory(
            academic_year=self.academic_year,
            learning_container_year__requirement_entity=self.entities_hierarchy.school_1_1_1.entity,
            learning_container_year__allocation_entity=self.entities_hierarchy.school_2_1_1.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [luy],
            transform=lambda obj: obj
        )

    def test_should_consider_entity_not_contained_inside_faculty_nor_faculty_as_a_faculty(self):
        luy = LearningUnitYearFactory(
            academic_year=self.academic_year,
            learning_container_year__requirement_entity=self.entities_hierarchy.school_1_1_1.entity,
            learning_container_year__allocation_entity=self.entities_hierarchy.sector_1.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [luy],
            transform=lambda obj: obj
        )

    def generate_get_data(self):
        return {"academic_year__year": self.academic_year.year}
