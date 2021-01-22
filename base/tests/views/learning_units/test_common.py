############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
############################################################################
from django.test import TestCase

from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import TrainingType, GroupType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory, MiniTrainingType
from base.tests.factories.group_element_year import GroupElementYearChildLeafFactory
from base.views.learning_units.common import _find_root_trainings_using_ue
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.ddd.domain.program_tree_version import STANDARD
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from program_management.tests.factories.element import ElementGroupYearFactory
from program_management.tests.factories.element import ElementLearningUnitYearFactory

LUY_ACRONYM = 'LECRI1508'


class TestLearningUnitCommonView(TestCase):

    def setUp(self):
        self.academic_year = AcademicYearFactory(current=True)
        self.element_learning_unit_year = ElementLearningUnitYearFactory(
            learning_unit_year__acronym=LUY_ACRONYM,
            learning_unit_year__academic_year=self.academic_year,
            learning_unit_year__learning_container_year__academic_year=self.academic_year,
        )

    def test_ue_used_in_one_training(self):
        build_training_tree('DROI2M', 'Bachelier droit', self.academic_year, self.element_learning_unit_year, TrainingType.BACHELOR, Categories.TRAINING)
        res = _find_root_trainings_using_ue(LUY_ACRONYM,
                                            self.academic_year.year)
        expected = ['DROI2M - Bachelier droit']
        self.assertListEqual(res, expected)

    def test_ue_used_in_two_trainings(self):
        build_training_tree('DROI2M', 'Bachelier droit', self.academic_year, self.element_learning_unit_year, TrainingType.BACHELOR,Categories.TRAINING)
        build_training_tree('ARK1BA', 'Bachelier archi', self.academic_year, self.element_learning_unit_year, TrainingType.BACHELOR, Categories.TRAINING)
        res = _find_root_trainings_using_ue(LUY_ACRONYM,
                                            self.academic_year.year)
        expected = ['ARK1BA - Bachelier archi',
                    'DROI2M - Bachelier droit']
        self.assertListEqual(res, expected)

    def test_ue_used_in_a_finality(self):
        training_root = build_training_tree('EDPH2M', 'Bachelier droit', self.academic_year, None,
                            TrainingType.BACHELOR, Categories.TRAINING)
        finality_root = build_training_tree('EDPH2MD', 'Bachelier droit', self.academic_year, self.element_learning_unit_year, TrainingType.MASTER_MA_120, Categories.TRAINING)
        GroupElementYearChildLeafFactory(parent_element=training_root,
                                         child_element=finality_root)
        res = _find_root_trainings_using_ue(LUY_ACRONYM,
                                            self.academic_year.year)
        expected = ['EDPH2M - Bachelier droit']
        self.assertListEqual(res, expected)

    def test_ue_used_in_a_minor_or_deepening(self):
        training_root = build_training_tree('EDPH2M', 'Bachelier droit', self.academic_year,
                                            None,
                                            TrainingType.BACHELOR, Categories.TRAINING)
        minor_root = build_training_tree('MINEDPH', 'Mineure en droit', self.academic_year,
                                            self.element_learning_unit_year, MiniTrainingType.SOCIETY_MINOR,
                                         Categories.MINI_TRAINING)
        GroupElementYearChildLeafFactory(parent_element=training_root,
                                         child_element=minor_root)
        res = _find_root_trainings_using_ue(LUY_ACRONYM,
                                            self.academic_year.year)
        expected = ['MINEDPH - Mineure en droit']
        self.assertListEqual(res, expected)


def build_training_tree(acronym, title, academic_year, element_learning_unit_year, type, category):
    # """
    #    |DROI2M
    #    |----COMMON
    #         |----LECRI1508
    # """
    offer = TrainingFactory(academic_year=academic_year,
                            title=title)
    root_group = GroupYearFactory(
        academic_year=academic_year,
        education_group_type__category=category.name,
        education_group_type__name=type.name,
        acronym=acronym
    )
    root_element = ElementGroupYearFactory(group_year=root_group)

    common_group = GroupYearFactory(
        academic_year=academic_year,
        education_group_type__category=Categories.GROUP.name,
        education_group_type__name=GroupType.COMMON_CORE.name,
        acronym='COMMON'
    )
    common_group_element = ElementGroupYearFactory(group_year=common_group)
    GroupElementYearChildLeafFactory(parent_element=root_element,
                                     child_element=common_group_element)
    if element_learning_unit_year:
        GroupElementYearChildLeafFactory(parent_element=common_group_element,
                                         child_element=element_learning_unit_year)
    education_group_version = EducationGroupVersionFactory(
        offer=offer,
        root_group=root_group,
        version_name=STANDARD,
        title_fr=None
    )
    return root_element
