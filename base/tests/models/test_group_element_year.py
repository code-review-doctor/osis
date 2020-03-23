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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import random

from django.core.exceptions import ValidationError
from django.test import TestCase

from base.models.enums.education_group_types import GroupType, MiniTrainingType
from base.models.enums.link_type import LinkTypes
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory, GroupFactory, MiniTrainingFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class TestManager(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year_1 = LearningUnitYearFactory()

        cls.learning_unit_year_without_container = LearningUnitYearFactory(
            learning_container_year=None
        )

        cls.group_element_year_1 = GroupElementYearFactory(
            child_branch=None,
            child_leaf=cls.learning_unit_year_1
        )

        cls.group_element_year_without_container = GroupElementYearFactory(
            child_branch=None,
            child_leaf=cls.learning_unit_year_without_container
        )

    def test_objects_without_container(self):
        self.assertNotIn(self.group_element_year_without_container, GroupElementYear.objects.all())
        self.assertIn(self.group_element_year_1, GroupElementYear.objects.all())


class TestSaveGroupElementYear(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()

    def test_simple_saves_ok(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year)
        egy2 = EducationGroupYearFactory(academic_year=self.academic_year)
        egy3 = EducationGroupYearFactory(academic_year=self.academic_year)

        GroupElementYearFactory(
            parent=egy2,
            child_branch=egy1,
        )
        GroupElementYearFactory(
            parent=egy3,
            child_branch=egy2,
        )

    def test_loop_save_on_itself_ko(self):
        egy = EducationGroupYearFactory()
        with self.assertRaises(ValidationError):
            GroupElementYearFactory(
                parent=egy,
                child_branch=egy,
            )

    def test_loop_save_ko(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year)
        egy2 = EducationGroupYearFactory(academic_year=self.academic_year)
        egy3 = EducationGroupYearFactory(academic_year=self.academic_year)

        GroupElementYearFactory(
            parent=egy2,
            child_branch=egy1,
        )
        GroupElementYearFactory(
            parent=egy3,
            child_branch=egy2,
        )

        with self.assertRaises(ValidationError):
            GroupElementYearFactory(
                parent=egy1,
                child_branch=egy3,
            )

    def test_save_with_child_branch_and_child_leaf_ko(self):
        egy = EducationGroupYearFactory(academic_year=self.academic_year)
        luy = LearningUnitYearFactory()
        with self.assertRaises(ValidationError):
            GroupElementYearFactory(
                parent=egy,
                child_branch=egy,
                child_leaf=luy,
            )


class TestValidationOnEducationGroupYearBlockField(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()

    def setUp(self):
        self.group_element_year = GroupElementYearFactory(parent__academic_year=self.academic_year,
                                                          child_branch__academic_year=self.academic_year)

    def test_when_value_is_higher_than_max_authorized(self):
        self.group_element_year.block = 7
        with self.assertRaises(ValidationError):
            self.group_element_year.full_clean()

    def test_when_more_than_6_digits_are_submitted(self):
        self.group_element_year.block = 1234567
        with self.assertRaises(ValidationError):
            self.group_element_year.full_clean()

    def test_when_values_are_duplicated(self):
        self.group_element_year.block = 1446
        with self.assertRaises(ValidationError):
            self.group_element_year.full_clean()

    def test_when_values_are_not_ordered(self):
        self.group_element_year.block = 54
        with self.assertRaises(ValidationError):
            self.group_element_year.full_clean()

    def test_when_0(self):
        self.group_element_year.block = 0
        with self.assertRaises(ValidationError):
            self.group_element_year.full_clean()

    def test_when_value_is_negative(self):
        self.group_element_year.block = -124
        with self.assertRaises(ValidationError):
            self.group_element_year.full_clean()

    def test_when_academic_year_diff_of_2_education_group(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year)
        egy2 = EducationGroupYearFactory(academic_year__year=self.academic_year.year + 1)
        with self.assertRaises(ValidationError):
            GroupElementYearFactory(
                parent=egy1,
                child_branch=egy2,
                child_leaf=None,
            )


class TestLinkTypeGroupElementYear(TestCase):
    def test_when_link_minor_to_minor_list_choice(self):
        minor_list_choice = GroupFactory(education_group_type__name=GroupType.MINOR_LIST_CHOICE.name)
        minor = MiniTrainingFactory(education_group_type__name=random.choice(MiniTrainingType.minors()))

        link = GroupElementYear(parent=minor_list_choice, child_branch=minor, link_type=None)
        link._clean_link_type()
        self.assertEqual(link.link_type, LinkTypes.REFERENCE.name)

    def test_when_link_deepening_to_minor_list_choice(self):
        minor_list_choice = GroupFactory(education_group_type__name=GroupType.MINOR_LIST_CHOICE.name)
        deepening = MiniTrainingFactory(education_group_type__name=MiniTrainingType.DEEPENING.name)

        link = GroupElementYear(parent=minor_list_choice, child_branch=deepening, link_type=None)
        link._clean_link_type()
        self.assertEqual(link.link_type, LinkTypes.REFERENCE.name)

    def test_when_link_major_to_major_list_choice(self):
        major_list_choice = GroupFactory(education_group_type__name=GroupType.MAJOR_LIST_CHOICE.name)
        major = MiniTrainingFactory(education_group_type__name=MiniTrainingType.FSA_SPECIALITY.name)

        link = GroupElementYear(parent=major_list_choice, child_branch=major, link_type=None)
        link._clean_link_type()
        self.assertEqual(link.link_type, LinkTypes.REFERENCE.name)


class TestManagerGetAdjacencyList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_element_a = EducationGroupYearFactory()
        cls.level_1 = GroupElementYearFactory(parent=cls.root_element_a, order=0)
        cls.level_11 = GroupElementYearFactory(parent=cls.level_1.child_branch, order=0)
        cls.level_2 = GroupElementYearFactory(parent=cls.root_element_a, order=1)

        cls.root_element_b = EducationGroupYearFactory()
        GroupElementYearFactory(parent=cls.root_element_b, order=0)

    def test_case_root_elements_ids_args_is_not_a_correct_instance(self):
        with self.assertRaises(Exception):
            GroupElementYear.objects.get_adjacency_list('bad_args')

    def test_case_root_elements_ids_is_empty(self):
        adjacency_list = GroupElementYear.objects.get_adjacency_list(root_elements_ids=[])
        self.assertEqual(len(adjacency_list), 0)

    def test_case_filter_by_root_elements_ids(self):
        adjacency_list = GroupElementYear.objects.get_adjacency_list([self.root_element_a.pk])
        self.assertEqual(len(adjacency_list), 3)

        expected_first_elem = {
            'starting_node_id': self.root_element_a.pk,
            'id': self.level_1.pk,
            'child_branch_id':  self.level_1.child_branch_id,
            'child_leaf_id': None,
            'parent_id': self.level_1.parent_id,
            'child_id': self.level_1.child_branch_id,
            'order': 0,
            'level': 0,
            'path': "|".join([str(self.level_1.parent_id), str(self.level_1.child_branch_id)])
        }
        self.assertDictEqual(adjacency_list[0], expected_first_elem)

    def test_case_multiple_root_elements_ids(self):
        adjacency_list = GroupElementYear.objects.get_adjacency_list([self.root_element_a.pk, self.root_element_b.pk])
        self.assertEqual(len(adjacency_list), 4)


class TestManagerGetReverseAdjacencyList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_element_a = EducationGroupYearFactory()
        cls.level_1 = GroupElementYearFactory(parent=cls.root_element_a)
        cls.level_11 = GroupElementYearFactory(parent=cls.level_1.child_branch)
        cls.level_111 = GroupElementYearFactory(
            parent=cls.level_11.child_branch,
            child_branch=None,
            child_leaf=LearningUnitYearFactory(),
        )
        cls.level_2 = GroupElementYearFactory(
            parent=cls.root_element_a,
            child_branch=None,
            child_leaf=LearningUnitYearFactory(),
            order=5
        )

    def test_case_root_elements_ids_args_is_not_a_correct_instance(self):
        with self.assertRaises(Exception):
            GroupElementYear.objects.get_reverse_adjacency_list(child_leaf_ids='bad_args')

    def test_case_root_elements_ids_is_empty(self):
        reverse_adjacency_list = GroupElementYear.objects.get_reverse_adjacency_list(child_leaf_ids=[])
        self.assertEqual(len(reverse_adjacency_list), 0)

    def test_case_filter_by_child_ids(self):
        reverse_adjacency_list = GroupElementYear.objects.get_reverse_adjacency_list(
            child_leaf_ids=[self.level_2.child_leaf_id]
        )
        self.assertEqual(len(reverse_adjacency_list), 1)

        expected_first_elem = {
            'starting_node_id': self.level_2.child_leaf_id,
            'id': self.level_2.pk,
            'child_branch_id': None,
            'child_leaf_id': self.level_2.child_leaf_id,
            'parent_id': self.level_2.parent_id,
            'child_id': self.level_2.child_leaf_id,
            'order': self.level_2.order,
            'level': 0,
        }
        self.assertDictEqual(reverse_adjacency_list[0], expected_first_elem)

    def test_case_multiple_child_ids(self):
        adjacency_list = GroupElementYear.objects.get_reverse_adjacency_list(child_leaf_ids=[
            self.level_2.child_leaf_id,
            self.level_111.child_leaf_id
        ])
        self.assertEqual(len(adjacency_list), 4)

    def test_case_child_is_education_group_instance(self):
        level_2bis = GroupElementYearFactory(
            parent=self.root_element_a,
            order=6
        )
        reverse_adjacency_list = GroupElementYear.objects.get_reverse_adjacency_list(
            child_branch_ids=[level_2bis.child_branch.id]
        )
        self.assertEqual(len(reverse_adjacency_list), 1)

    def test_case_child_leaf_and_child_branch_have_same_id(self):
        common_id = 123456
        # with parent
        link_with_leaf = GroupElementYearFactory(
            child_branch=None,
            child_leaf=LearningUnitYearFactory(id=common_id),
            parent=self.root_element_a,
        )
        # Without parent
        link_with_branch = GroupElementYearFactory(
            child_branch__id=common_id,
        )
        reverse_adjacency_list = GroupElementYear.objects.get_reverse_adjacency_list(
            child_branch_ids=[link_with_leaf.child_leaf.id, link_with_branch.child_branch.id]
        )
        self.assertEqual(len(reverse_adjacency_list), 1)
        self.assertNotEqual(len(reverse_adjacency_list), 2)

    def test_case_filter_link_type(self):
        link_reference = GroupElementYearFactory(
            parent__academic_year=self.level_1.child_branch.academic_year,
            child_branch=self.level_1.child_branch,
            order=6,
            link_type=LinkTypes.REFERENCE.name
        )
        link_not_reference = GroupElementYearFactory(
            parent__academic_year=self.level_1.child_branch.academic_year,
            child_branch=self.level_1.child_branch,
            order=6,
            link_type=None
        )
        reverse_adjacency_list = GroupElementYear.objects.get_reverse_adjacency_list(
            child_branch_ids=[self.level_1.child_branch.id],
            link_type=LinkTypes.REFERENCE,
        )
        result_parent_ids = [rec['parent_id'] for rec in reverse_adjacency_list]
        self.assertIn(link_reference.parent.id, result_parent_ids)
        self.assertNotIn(link_not_reference.parent.id, result_parent_ids)
