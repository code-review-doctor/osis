##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-202 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest.mock import patch

from django.test import TestCase

from base.models.education_group_year import EducationGroupYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_type import TrainingEducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from education_group.ddd.domain.exception import TrainingNotFoundException
from education_group.models.group_year import GroupYear
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.program_tree_version import NOT_A_TRANSITION, ProgramTreeVersion
from program_management.ddd.dtos import ProgrammeDeFormationDTO, ContenuNoeudDTO
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory, \
    ProgramTreeVersionIdentityFactory
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from program_management.tests.factories.element import ElementFactory


class TestVersionRepositoryUtils:
    @classmethod
    def create_necessary_data(cls, for_tree_version: 'ProgramTreeVersion'):
        end_year = None
        if for_tree_version.end_year_of_existence:
            end_year = AcademicYearFactory(year=for_tree_version.end_year_of_existence)

        education_group_type = TrainingEducationGroupTypeFactory(
            name=for_tree_version.get_tree().root_node.node_type.name
        )
        EducationGroupYearFactory(
            education_group__start_year__year=for_tree_version.start_year,
            education_group__end_year=end_year,
            academic_year__year=for_tree_version.academic_year.year,
            education_group_type=education_group_type,
            acronym=for_tree_version.entity_id.offer_acronym,
        )
        GroupYearFactory(
            group__start_year__year=for_tree_version.start_year,
            group__end_year=end_year,
            academic_year__year=for_tree_version.academic_year.year,
            partial_acronym=for_tree_version.program_tree_identity.code
        )

    def assert_ddd_object_equal_database(self, tree_version: 'ProgramTreeVersion'):
        education_group_year_db_objects = EducationGroupYear.objects.filter(
            acronym=tree_version.entity_id.offer_acronym,
            academic_year__year=tree_version.entity_id.year,
        )

        education_group_version_db_object = EducationGroupVersion.objects.get(
            offer__acronym=tree_version.entity_id.offer_acronym,
            offer__academic_year__year=tree_version.entity_id.year,
            version_name=tree_version.entity_id.version_name,
            transition_name=tree_version.entity_id.transition_name,
        )

        group_year_db_object = GroupYear.objects.get(
            partial_acronym=tree_version.get_tree().root_node.code,
            academic_year__year=tree_version.get_tree().root_node.year,
        )

        self.assertEqual(len(education_group_year_db_objects), 1)
        self.assertEqual(education_group_version_db_object.root_group, group_year_db_object)
        self.assertEqual(education_group_version_db_object.transition_name, tree_version.transition_name)
        self.assertEqual(education_group_version_db_object.version_name, tree_version.version_name)
        self.assertEqual(education_group_version_db_object.title_fr, tree_version.title_fr)
        self.assertEqual(education_group_version_db_object.title_en, tree_version.title_en)
        self.assertEqual(
            education_group_version_db_object.root_group.group.end_year.year,
            tree_version.end_year_of_existence
        )


class TestVersionRepositoryCreateMethod(TestCase, TestVersionRepositoryUtils):

    def setUp(self) -> None:
        self.repository = ProgramTreeVersionRepository()

        self.new_program_tree_version = ProgramTreeVersionFactory()
        self.new_program_tree = self.new_program_tree_version.get_tree()

        self.create_necessary_data(self.new_program_tree_version)

    @patch.object(Node, '_has_changed', return_value=True)
    def test_simple_case_creation(self, *mocks):
        self.repository.create(self.new_program_tree_version)

        self.assert_ddd_object_equal_database(self.new_program_tree_version)

    def test_assert_raises_training_not_found_exception(self):
        tree_version = ProgramTreeVersionFactory(entity_id__offer_acronym='INEXISTING')
        with self.assertRaises(TrainingNotFoundException):
            self.repository.create(tree_version)


class TestProgramTreeVersionRepositoryUpdateMethod(TestCase, TestVersionRepositoryUtils):
    def setUp(self) -> None:
        self.repository = ProgramTreeVersionRepository()

        self.new_program_tree_version = ProgramTreeVersionFactory()

        self.create_necessary_data(self.new_program_tree_version)

    def test_should_update(self):
        self.repository.create(self.new_program_tree_version)

        self.new_program_tree_version.title_fr = "Hello new title"
        self.new_program_tree_version.title_en = "Hello hello"

        self.repository.update(self.new_program_tree_version)

        self.assert_ddd_object_equal_database(self.new_program_tree_version)


class TestProgramTreeVersionRepositoryGetMethod(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.year = AcademicYearFactory(current=True).year
        cls.repository = ProgramTreeVersionRepository()

    def test_field_mapping_with_specific_version_not_transition(self):
        entity_id = ProgramTreeVersionIdentityFactory(year=self.year, transition_name=NOT_A_TRANSITION)
        root_group = ElementFactory(
            group_year=GroupYearFactory(
                academic_year__year=entity_id.year,
                group__end_year=AcademicYearFactory(current=True),
            )
        ).group_year

        education_group_version_model_obj = EducationGroupVersionFactory(
            offer__acronym=entity_id.offer_acronym,
            offer__academic_year__year=entity_id.year,
            version_name=entity_id.version_name,
            transition_name=entity_id.transition_name,
            root_group=root_group,
        )

        version_tree_domain_obj = self.repository.get(entity_id)

        self.assertEqual(version_tree_domain_obj.entity_id, entity_id)
        self.assertEqual(
            version_tree_domain_obj.entity_id.offer_acronym, education_group_version_model_obj.offer.acronym
        )
        self.assertEqual(
            version_tree_domain_obj.entity_id.year, education_group_version_model_obj.offer.academic_year.year
        )
        self.assertEqual(
            version_tree_domain_obj.entity_id.version_name, education_group_version_model_obj.version_name
        )
        self.assertEqual(
            version_tree_domain_obj.entity_id.transition_name, education_group_version_model_obj.transition_name
        )
        self.assertEqual(
            version_tree_domain_obj.end_year_of_existence, root_group.group.end_year.year
        )
        self.assertEqual(
            version_tree_domain_obj.start_year, root_group.group.start_year.year
        )

    def test_field_mapping_with_transition_version(self):
        entity_id = ProgramTreeVersionIdentityFactory(year=self.year, transition_name='Transition')
        root_group = ElementFactory(
            group_year=GroupYearFactory(
                academic_year__year=entity_id.year,
                group__end_year=AcademicYearFactory(current=True),
            )
        ).group_year

        education_group_version_model_obj = EducationGroupVersionFactory(
            offer__acronym=entity_id.offer_acronym,
            offer__academic_year__year=entity_id.year,
            version_name=entity_id.version_name,
            transition_name=entity_id.transition_name,
            root_group=root_group,
        )

        version_tree_domain_obj = self.repository.get(entity_id)

        self.assertEqual(version_tree_domain_obj.entity_id, entity_id)
        self.assertEqual(
            version_tree_domain_obj.entity_id.offer_acronym, education_group_version_model_obj.offer.acronym
        )
        self.assertEqual(
            version_tree_domain_obj.entity_id.year, education_group_version_model_obj.offer.academic_year.year
        )
        self.assertEqual(
            version_tree_domain_obj.entity_id.version_name, education_group_version_model_obj.version_name
        )
        self.assertEqual(
            version_tree_domain_obj.entity_id.transition_name, education_group_version_model_obj.transition_name
        )
        self.assertEqual(
            version_tree_domain_obj.end_year_of_existence, root_group.group.end_year.year
        )
        self.assertEqual(
            version_tree_domain_obj.start_year, root_group.group.start_year.year
        )


class TestProgramTreeVersionRepositoryGetDtoMethod(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.year = AcademicYearFactory(current=True).year
        cls.repository = ProgramTreeVersionRepository()

    def test_field_mapping_with_education_group_version(self):
        entity_id = ProgramTreeVersionIdentityFactory(year=self.year, transition_name=NOT_A_TRANSITION)
        root_group = ElementFactory(
            group_year=GroupYearFactory(
                academic_year__year=entity_id.year,
                group__end_year=AcademicYearFactory(current=True),
            )
        ).group_year

        education_group_version_model_obj = EducationGroupVersionFactory(
            offer__acronym=entity_id.offer_acronym,
            offer__academic_year__year=entity_id.year,
            version_name=entity_id.version_name,
            transition_name=entity_id.transition_name,
            root_group=root_group
        )

        programme_de_formation_dto = self.repository.get_dto(entity_id)

        self.assertIsInstance(programme_de_formation_dto, ProgrammeDeFormationDTO)

        self.assertEqual(programme_de_formation_dto.sigle, education_group_version_model_obj.offer.acronym)
        self.assertEqual(programme_de_formation_dto.annee, education_group_version_model_obj.offer.academic_year.year)
        self.assertEqual(programme_de_formation_dto.version, education_group_version_model_obj.version_name)
        self.assertEqual(programme_de_formation_dto.intitule_formation,
                         "{}{}".format(
                             education_group_version_model_obj.offer.title,
                             "{}".format(
                                "[ {} ]".format(education_group_version_model_obj.title_fr) if education_group_version_model_obj.title_fr else '')
                         )
                         )

        self.assertIsInstance(programme_de_formation_dto.racine, ContenuNoeudDTO)
        self.assertEqual(programme_de_formation_dto.racine.groupement_contenant.intitule, root_group.acronym)
        self.assertEqual(programme_de_formation_dto.racine.groupements_contenus, [])
        self.assertEqual(programme_de_formation_dto.racine.unites_enseignement_contenues, [])
