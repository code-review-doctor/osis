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

from base.models.entity_version import EntityVersion
from base.models.enums.education_group_types import TrainingType
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.business.entities import EntitiesHierarchyFactory
from base.tests.factories.entity_version import EntityVersionFactory, MainEntityVersionFactory
from base.tests.factories.group_element_year import GroupElementYearFactory, GroupElementYearChildLeafFactory
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
        cls.url = reverse("learning_units_borrowed_course")
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

        cls.url = reverse("learning_units_borrowed_course")

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_should_not_return_learning_unit_having_same_requirement_entity_than_offer_management_entity(self):
        gey = self.generate_group_element_year(
            self.entities_hierarchy.faculty_1_1.entity,
            self.entities_hierarchy.faculty_1_1.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [],
        )

    def test_should_not_return_learning_unit_having_requirement_entity_and_offer_management_in_same_faculty(self):
        gey = self.generate_group_element_year(
            self.entities_hierarchy.school_1_1_1.entity,
            self.entities_hierarchy.faculty_1_1.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [],
        )

    def test_should_return_learning_unit_having_requirement__and_offer_management_in_different_faculty(self):
        gey = self.generate_group_element_year(
            self.entities_hierarchy.school_1_1_1.entity,
            self.entities_hierarchy.school_2_1_1.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [gey.child_element.learning_unit_year],
            transform=lambda obj: obj
        )

    def test_should_consider_entities_not_contained_inside_faculties_as_a_faculty(self):
        gey = self.generate_group_element_year(
            self.entities_hierarchy.sector_1.entity,
            self.entities_hierarchy.sector_2.entity
        )

        response = self.client.get(self.url, self.generate_get_data())
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [gey.child_element.learning_unit_year],
            transform=lambda obj: obj
        )

    def test_should_not_return_any_learning_unit_when_no_learning_unit_is_borrowed_by_specific_entity(self):
        gey = self.generate_group_element_year(
            self.entities_hierarchy.school_1_1_1.entity,
            self.entities_hierarchy.school_2_1_1.entity
        )
        response = self.client.get(
            self.url,
            self.generate_get_data(borrowing_faculty=self.entities_hierarchy.faculty_1_2)
        )
        self.assertQuerysetEqual(
            response.context["page_obj"].object_list,
            [],
        )

    def generate_get_data(self, borrowing_faculty: EntityVersion = None):
        data = {"academic_year": self.academic_year.id}
        if borrowing_faculty:
            data["faculty_borrowing_acronym"] = borrowing_faculty.acronym
        return data

    def generate_group_element_year(self, root_entity, luy_entity):
        return GroupElementYearChildLeafFactory(
            parent_element__group_year__education_group_type__name=TrainingType.BACHELOR.name,
            parent_element__group_year__academic_year=self.academic_year,
            parent_element__group_year__management_entity=root_entity,
            child_element__learning_unit_year__academic_year=self.academic_year,
            child_element__learning_unit_year__learning_container_year__requirement_entity=luy_entity
        )
