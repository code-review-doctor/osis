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
import random
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

from django.db import models
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from base.business.learning_units.quadrimester_strategy import LearningComponentYearQ1Strategy, \
    LearningComponentYearQ2Strategy, LearningComponentYearQ1and2Strategy, LearningComponentYearQ1or2Strategy, \
    LearningComponentYearQuadriStrategy, LearningComponentYearQuadriNoStrategy
from base.models import learning_unit_year
from base.models.enums import learning_unit_year_periodicity, entity_container_year_link_type, quadrimesters, \
    learning_unit_year_session, learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.learning_component_year import LearningComponentYear
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.business.learning_units import GenerateAcademicYear, GenerateContainer
from base.tests.factories.entity import EntityFactory
from base.tests.factories.external_learning_unit_year import ExternalLearningUnitYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory, \
    LecturingLearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory, \
    LearningContainerYearNotInChargeFactory, LearningContainerYearInChargeFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory, create_learning_units_year
from base.tests.factories.tutor import TutorFactory
from cms.models.translated_text import TranslatedText
from cms.tests.factories.translated_text import LearningUnitYearTranslatedTextFactory
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory

ALL_SESSION_VALUES = [
    learning_unit_year_session.SESSION_P23,
    learning_unit_year_session.SESSION_XX3,
    learning_unit_year_session.SESSION_X2X,
    learning_unit_year_session.SESSION_X23,
    learning_unit_year_session.SESSION_1XX,
    learning_unit_year_session.SESSION_1X3,
    learning_unit_year_session.SESSION_12X,
    learning_unit_year_session.SESSION_123,

]

ALL_QUADRIMESTER_VALUES = [
    quadrimesters.LearningUnitYearQuadrimester.Q1.name,
    quadrimesters.LearningUnitYearQuadrimester.Q2.name,
    quadrimesters.LearningUnitYearQuadrimester.Q3.name,
    quadrimesters.LearningUnitYearQuadrimester.Q1and2.name,
    quadrimesters.LearningUnitYearQuadrimester.Q1or2.name
]


class LearningUnitYearTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = create_current_academic_year()
        learning_container_yr = LearningContainerYearNotInChargeFactory()
        cls.learning_unit_year = LearningUnitYearFactory(
            acronym="LDROI1004",
            specific_title="Juridic law courses",
            academic_year=cls.academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year=learning_container_yr
        )

    def test_subdivision_computation(self):
        l_container_year = LearningContainerYearFactory(acronym="LBIR1212", academic_year=self.academic_year)
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year)
        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212A", learning_container_year=l_container_year,
                                           academic_year=self.academic_year)
        l_unit_3 = LearningUnitYearFactory(acronym="LBIR1212B", learning_container_year=l_container_year,
                                           academic_year=self.academic_year)

        self.assertFalse(l_unit_1.subdivision)
        self.assertEqual(l_unit_2.subdivision, 'A')
        self.assertEqual(l_unit_3.subdivision, 'B')

    def test_search_acronym_by_regex(self):
        regex_valid = '^LD.+1+'
        query_result_valid = learning_unit_year.search(acronym=regex_valid)
        self.assertEqual(len(query_result_valid), 1)
        self.assertEqual(self.learning_unit_year.acronym, query_result_valid[0].acronym)

    def test_property_in_charge(self):
        self.assertFalse(self.learning_unit_year.in_charge)

        a_container_year = LearningContainerYearInChargeFactory(acronym=self.learning_unit_year.acronym,
                                                                academic_year=self.academic_year)
        self.learning_unit_year.learning_container_year = a_container_year

        self.assertTrue(self.learning_unit_year.in_charge)

    def test_find_gt_learning_unit_year(self):
        learning_unit = LearningUnitFactory()
        dict_learning_unit_year = create_learning_units_year(2000, 2017, learning_unit)

        selected_learning_unit_year = dict_learning_unit_year[2007]

        result = list(selected_learning_unit_year.find_gt_learning_units_year().values_list('academic_year__year',
                                                                                            flat=True))
        self.assertListEqual(result, list(range(2008, 2018)))

    def test_find_gt_learning_units_year_case_no_future(self):
        learning_unit = LearningUnitFactory()
        dict_learning_unit_year = create_learning_units_year(2000, 2017, learning_unit)

        selected_learning_unit_year = dict_learning_unit_year[2017]

        result = list(selected_learning_unit_year.find_gt_learning_units_year().values_list('academic_year__year',
                                                                                            flat=True))
        self.assertEqual(result, [])

    def test_get_learning_unit_parent(self):
        lunit_container_year = LearningContainerYearFactory(academic_year=self.academic_year, acronym='LBIR1230')
        luy_parent = LearningUnitYearFactory(academic_year=self.academic_year, acronym='LBIR1230',
                                             learning_container_year=lunit_container_year,
                                             subtype=learning_unit_year_subtypes.FULL)
        luy_partim = LearningUnitYearFactory(academic_year=self.academic_year, acronym='LBIR1230B',
                                             learning_container_year=lunit_container_year,
                                             subtype=learning_unit_year_subtypes.PARTIM)
        self.assertEqual(luy_partim.parent, luy_parent)

    def test_get_learning_unit_parent_without_parent(self):
        lunit_container_year = LearningContainerYearFactory(academic_year=self.academic_year, acronym='LBIR1230')
        luy_parent = LearningUnitYearFactory(academic_year=self.academic_year, acronym='LBIR1230',
                                             learning_container_year=lunit_container_year,
                                             subtype=learning_unit_year_subtypes.FULL)
        self.assertIsNone(luy_parent.parent)

    def test_search_by_title(self):
        common_part = "commun"
        a_common_title = "Titre {}".format(common_part)
        a_specific_title = "Specific title {}".format(common_part)
        lunit_container_yr = LearningContainerYearFactory(academic_year=self.academic_year,
                                                          common_title=a_common_title)
        luy = LearningUnitYearFactory(academic_year=self.academic_year,
                                      specific_title=a_specific_title,
                                      learning_container_year=lunit_container_yr)

        self.assertEqual(learning_unit_year.search(title="{} en plus".format(a_common_title)).count(), 0)
        self.assertEqual(learning_unit_year.search(title=a_common_title)[0], luy)
        self.assertEqual(learning_unit_year.search(title=common_part)[0], luy)
        self.assertEqual(learning_unit_year.search(title=a_specific_title)[0], luy)

    def test_complete_title_when_no_learning_container_year(self):
        specific_title = 'part 1: Vertebrate'

        luy = LearningUnitYearFactory(specific_title=specific_title, learning_container_year=None)
        self.assertEqual(luy.complete_title, specific_title)

    def test_complete_title_property_case_common_title_is_empty(self):
        specific_title = 'part 1: Vertebrate'

        luy = LearningUnitYearFactory(specific_title=specific_title, learning_container_year__common_title="")
        self.assertEqual(luy.complete_title, specific_title)

        luy = LearningUnitYearFactory(specific_title=specific_title, learning_container_year__common_title=None)
        self.assertEqual(luy.complete_title, specific_title)

    def test_complete_title_property_case_common_and_specific_title_are_set(self):
        specific_title = 'part 1: Vertebrate'
        common_title = 'Zoology'

        luy = LearningUnitYearFactory(specific_title=specific_title, learning_container_year__common_title=common_title)
        self.assertEqual(luy.complete_title, '{} - {}'.format(common_title, specific_title))

    def test_common_title_property(self):
        self.assertEqual(self.learning_unit_year.container_common_title,
                         self.learning_unit_year.learning_container_year.common_title)

    def test_common_title_property_no_container(self):
        self.learning_unit_year.learning_container_year = None
        self.assertEqual(self.learning_unit_year.container_common_title, '')

    def test_is_external(self):
        luy = LearningUnitYearFactory()
        ExternalLearningUnitYearFactory(learning_unit_year=luy)
        self.assertTrue(luy.is_external())

    def test_is_not_external(self):
        luy = LearningUnitYearFactory()
        self.assertFalse(luy.is_external())

    def test_get_learning_unit_previous_year(self):
        learning_unit = LearningUnitFactory()
        dict_learning_unit_year = create_learning_units_year(2000, 2017, learning_unit)
        cases = [
            {'expected_result': dict_learning_unit_year[2006],
             'result': dict_learning_unit_year[2007].get_learning_unit_previous_year(),
             'name': "When there is a previous year of luy"},
            {'expected_result': None,
             'result': dict_learning_unit_year[2000].get_learning_unit_previous_year(),
             'name': "When there is NOT a previous year of luy"}
        ]
        for case in cases:
            with self.subTest(case['name']):
                self.assertEqual(case['expected_result'], case['result'])


class LearningUnitYearGetEntityTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory(
            learning_container_year__requirement_entity=EntityFactory()
        )
        cls.requirement_entity = cls.learning_unit_year.learning_container_year.requirement_entity

    def test_get_entity_case_found_entity_type(self):
        result = self.learning_unit_year.get_entity(entity_type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        self.assertEqual(result, self.requirement_entity)

    def test_get_entity_case_no_learning_container_year(self):
        self.learning_unit_year.learning_container_year = None
        self.learning_unit_year.save()

        result = self.learning_unit_year.get_entity(entity_type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        self.assertIsNone(result)


class LearningUnitYearWarningsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.start_year = AcademicYearFactory(year=2010)
        cls.end_year = AcademicYearFactory(year=2020)
        cls.generated_ac_years = GenerateAcademicYear(cls.start_year, cls.end_year)

    def setUp(self):
        self.generated_container = GenerateContainer(self.start_year, self.end_year)
        self.luy_full = self.generated_container.generated_container_years[0].learning_unit_year_full
        self.component_full_lecturing = LearningComponentYear.objects.filter(
            type=LECTURING,
            learning_unit_year=self.luy_full
        ).first()
        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim

        learning_component_year_partim_lecturing = LearningComponentYear.objects.filter(
            type=LECTURING,
            learning_unit_year=luy_partim
        ).first()
        learning_component_year_partim_lecturing.planned_classes = 0
        learning_component_year_partim_lecturing.hourly_volume_partial_q1 = 0
        learning_component_year_partim_lecturing.hourly_volume_partial_q2 = 0
        learning_component_year_partim_lecturing.hourly_volume_total_annual = 0
        learning_component_year_partim_lecturing.repartition_volume_requirement_entity = 0
        learning_component_year_partim_lecturing.save()

        self.luy_full.quadrimester = None
        self.luy_full.save()
        self.luy_full.get_partims_related().update(quadrimester=None)

    def test_warning_volumes_vol_tot(self):
        self.component_full_lecturing.hourly_volume_partial_q1 = Decimal(15)
        self.component_full_lecturing.hourly_volume_partial_q2 = Decimal(15)
        self.component_full_lecturing.hourly_volume_total_annual = Decimal(40)
        self.component_full_lecturing.planned_classes = 1
        self.component_full_lecturing.repartition_volume_requirement_entity = Decimal(30)
        self.component_full_lecturing.save()

        complete_acronym = self.component_full_lecturing.complete_acronym
        excepted_error = "{} ({})".format(_('Volumes of {} are inconsistent').format(complete_acronym),
                                          _('The annual volume must be equal to the sum of the volumes Q1 and Q2'))
        self.assertIn(excepted_error, self.component_full_lecturing.warnings)
        self.assertIn(excepted_error, self.luy_full.warnings)

    def test_warning_volumes_vol_global(self):
        self.component_full_lecturing.hourly_volume_partial_q1 = Decimal(15)
        self.component_full_lecturing.hourly_volume_partial_q2 = Decimal(15)
        self.component_full_lecturing.hourly_volume_total_annual = Decimal(30)
        self.component_full_lecturing.planned_classes = 1
        self.component_full_lecturing.repartition_volume_requirement_entity = Decimal(40)
        self.component_full_lecturing.save()

        complete_acronym = self.component_full_lecturing.complete_acronym
        excepted_error = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(complete_acronym),
            _('the sum of repartition volumes must be equal to the global volume'))
        self.assertIn(excepted_error, self.component_full_lecturing.warnings)
        self.assertIn(excepted_error, self.luy_full.warnings)

    def test_warning_volumes_vol_global_and_total(self):
        self.component_full_lecturing.repartition_volume_requirement_entity = Decimal(42)
        self.component_full_lecturing.hourly_volume_partial_q1 = Decimal(10)
        self.component_full_lecturing.hourly_volume_partial_q2 = Decimal(15)
        self.component_full_lecturing.hourly_volume_total_annual = Decimal(36)
        self.component_full_lecturing.planned_classes = 2
        self.component_full_lecturing.save()

        complete_acronym = self.component_full_lecturing.complete_acronym
        excepted_error_1 = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(complete_acronym),
            _('the sum of repartition volumes must be equal to the global volume'))
        self.assertIn(excepted_error_1, self.component_full_lecturing.warnings)
        self.assertIn(excepted_error_1, self.luy_full.warnings)

        complete_component_acronym = self.component_full_lecturing.complete_acronym
        excepted_error_2 = "{} ({})".format(_('Volumes of {} are inconsistent').format(complete_component_acronym),
                                            _('The annual volume must be equal to the sum of the volumes Q1 and Q2'))
        self.assertIn(excepted_error_2, self.component_full_lecturing.warnings)
        self.assertIn(excepted_error_2, self.luy_full.warnings)

    @mock.patch('base.models.learning_unit_year.LearningUnitYear._check_classes')
    def test_warning_volumes_no_warning(self, mock_check_classes_warnings=[]):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.save()

        test_cases = [
            {
                'vol_q1': 15, 'vol_q2': 15, 'vol_tot_annual': 30, 'planned_classes': 1, 'vol_tot_global': 30,
                'requirement_entity': 20, 'additional_entity_1': 5, 'additional_entity_2': 5
            },
            {
                'vol_q1': 10, 'vol_q2': 20, 'vol_tot_annual': 30, 'planned_classes': 2, 'vol_tot_global': 60,
                'requirement_entity': 30, 'additional_entity_1': 20, 'additional_entity_2': 10
            }
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.component_full_lecturing.hourly_volume_partial_q1 = case.get('vol_q1')
                self.component_full_lecturing.hourly_volume_partial_q2 = case.get('vol_q2')
                self.component_full_lecturing.hourly_volume_total_annual = case.get('vol_tot_annual')
                self.component_full_lecturing.planned_classes = case.get('planned_classes')
                self.component_full_lecturing.repartition_volume_requirement_entity = case.get('requirement_entity')
                self.component_full_lecturing.repartition_volume_additional_entity_1 = case.get('additional_entity_1')
                self.component_full_lecturing.repartition_volume_additional_entity_2 = case.get('additional_entity_2')
                self.component_full_lecturing.save()

                self.assertFalse(self.component_full_lecturing.warnings)
                self.assertFalse(self.luy_full.warnings)

    def test_warning_all_volumes_partim_greater_than_full(self):
        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim
        learning_component_year_partim_lecturing = LearningComponentYear.objects.filter(
            type=LECTURING,
            learning_unit_year=luy_partim
        ).first()

        self.component_full_lecturing.hourly_volume_partial_q1 = 15.0
        self.component_full_lecturing.hourly_volume_partial_q2 = 15.0
        self.component_full_lecturing.hourly_volume_total_annual = 30.0
        self.component_full_lecturing.planned_classes = 1
        self.component_full_lecturing.repartition_volume_requirement_entity = 30.0
        self.component_full_lecturing.save()

        learning_component_year_partim_lecturing.hourly_volume_partial_q1 = 20.0
        learning_component_year_partim_lecturing.hourly_volume_partial_q2 = 20.0
        learning_component_year_partim_lecturing.hourly_volume_total_annual = 40.0
        learning_component_year_partim_lecturing.planned_classes = 2
        learning_component_year_partim_lecturing.repartition_volume_requirement_entity = 80.0
        learning_component_year_partim_lecturing.save()

        excepted_error = "{} ({})".format(
            _('Volumes are inconsistent'),
            _('At least a partim volume value is greater than corresponding volume of full UE'))
        self.assertIn(excepted_error, self.luy_full.learning_container_year.warnings)
        self.assertIn(excepted_error, self.luy_full.warnings)
        excepted_error = "{} ({})".format(
            _('Volumes are inconsistent'),
            _('a partim volume value is greater than corresponding volume of parent'))

        self.assertIn(excepted_error, luy_partim.warnings)

    def test_warning_one_volume_partim_greater_than_full(self):
        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim
        learning_component_year_partim_lecturing = LearningComponentYear.objects.filter(
            type=LECTURING,
            learning_unit_year=luy_partim
        ).first()

        self.component_full_lecturing.hourly_volume_partial_q1 = 15.0
        self.component_full_lecturing.hourly_volume_partial_q2 = 15.0
        self.component_full_lecturing.hourly_volume_total_annual = 30.0
        self.component_full_lecturing.planned_classes = 1
        self.component_full_lecturing.save()
        self.component_full_lecturing.repartition_volume_requirement_entity = 30.0
        self.component_full_lecturing.save()

        learning_component_year_partim_lecturing.hourly_volume_partial_q1 = 10.0
        learning_component_year_partim_lecturing.hourly_volume_partial_q2 = 10.0
        learning_component_year_partim_lecturing.hourly_volume_total_annual = 20.0
        learning_component_year_partim_lecturing.planned_classes = 1
        learning_component_year_partim_lecturing.save()
        learning_component_year_partim_lecturing.repartition_volume_requirement_entity = 80.0
        learning_component_year_partim_lecturing.save()

        excepted_error = "{} ({})".format(
            _('Volumes are inconsistent'),
            _('At least a partim volume value is greater than corresponding volume of full UE'))
        self.assertIn(excepted_error, self.luy_full.learning_container_year.warnings)
        self.assertIn(excepted_error, self.luy_full.warnings)
        excepted_error = "{} ({})".format(
            _('Volumes are inconsistent'),
            _('a partim volume value is greater than corresponding volume of parent'))
        self.assertIn(excepted_error, luy_partim.warnings)

    @mock.patch('base.models.learning_unit_year.LearningUnitYear._check_classes')
    def test_warning_when_volumes_ok_but_other_component_of_partim_has_higher_values(
            self,
            mock_check_classes_warnings=[]
    ):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.save()

        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim

        learning_component_year_partim_lecturing = LearningComponentYear.objects.filter(
            type=LECTURING,
            learning_unit_year=luy_partim
        ).first()

        learning_component_year_partim_practical = LearningComponentYear.objects.filter(
            type=PRACTICAL_EXERCISES,
            learning_unit_year=luy_partim
        ).first()

        learning_component_year_full_practical = LearningComponentYear.objects.filter(
            type=PRACTICAL_EXERCISES,
            learning_unit_year=self.luy_full
        ).first()

        self.component_full_lecturing.hourly_volume_partial_q1 = 15.0
        self.component_full_lecturing.hourly_volume_partial_q2 = 15.0
        self.component_full_lecturing.hourly_volume_total_annual = 30.0
        self.component_full_lecturing.planned_classes = 1
        self.component_full_lecturing.repartition_volume_requirement_entity = 30.0
        self.component_full_lecturing.save()

        learning_component_year_partim_lecturing.hourly_volume_partial_q1 = 10.0
        learning_component_year_partim_lecturing.hourly_volume_partial_q2 = 10.0
        learning_component_year_partim_lecturing.hourly_volume_total_annual = 20.0
        learning_component_year_partim_lecturing.planned_classes = 1
        learning_component_year_partim_lecturing.repartition_volume_requirement_entity = 20.0
        learning_component_year_partim_lecturing.save()

        learning_component_year_full_practical.hourly_volume_partial_q1 = 10.0
        learning_component_year_full_practical.hourly_volume_partial_q2 = 15.0
        learning_component_year_full_practical.hourly_volume_total_annual = 25.0
        learning_component_year_full_practical.planned_classes = 1
        learning_component_year_full_practical.repartition_volume_requirement_entity = 25.0
        learning_component_year_full_practical.save()

        learning_component_year_partim_practical.hourly_volume_partial_q1 = 10.0
        learning_component_year_partim_practical.hourly_volume_partial_q2 = 10.0
        learning_component_year_partim_practical.hourly_volume_total_annual = 20.0
        learning_component_year_partim_practical.planned_classes = 1
        learning_component_year_partim_practical.repartition_volume_requirement_entity = 25.0  # wrong repartition
        learning_component_year_partim_practical.save()

        self.assertFalse(self.luy_full.learning_container_year.warnings)
        warnings = self.luy_full.warnings
        self.assertEqual(len(warnings), 1)
        self.assertIn(str(_('the sum of repartition volumes must be equal to the global volume')), warnings[0])

    def test_warning_when_partim_parent_periodicity_different_from_parent(self):
        # Set Parent UE to biannual odd
        self.luy_full.periodicity = learning_unit_year_periodicity.BIENNIAL_ODD
        self.luy_full.save()
        # Set Partim UE to annual
        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim
        luy_partim.periodicity = learning_unit_year_periodicity.ANNUAL
        luy_partim.save()

        expected_result = [
            _("The parent is %(parent_periodicty)s and there is at least one partim which is not "
              "%(parent_periodicty)s") % {'parent_periodicty': self.luy_full.periodicity_verbose}
        ]
        result = self.luy_full._check_partim_parent_periodicity()
        self.assertEqual(result, expected_result)

    def test_warning_when_partim_parent_periodicity_different_from_partim(self):
        # Set Parent UE to biannual even
        self.luy_full.periodicity = learning_unit_year_periodicity.BIENNIAL_EVEN
        self.luy_full.save()
        # Set Partim UE to biannual odd
        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim
        luy_partim.periodicity = learning_unit_year_periodicity.BIENNIAL_ODD
        luy_partim.save()

        expected_result = [
            _("This partim is %(partim_periodicity)s and the parent is %(parent_periodicty)s") % {
                'partim_periodicity': luy_partim.periodicity_verbose,
                'parent_periodicty': self.luy_full.periodicity_verbose
            }
        ]
        result = luy_partim._check_partim_parent_periodicity()
        self.assertEqual(result, expected_result)

    def test_no_warning_when_partim_parent_periodicity_different(self):
        """In this test, we ensure that if parent is annual, the partim can be annual/bi-annual"""
        self.luy_full.periodicity = learning_unit_year_periodicity.ANNUAL
        self.luy_full.save()
        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim
        luy_partim.periodicity = learning_unit_year_periodicity.BIENNIAL_ODD
        result = luy_partim._check_partim_parent_periodicity()
        self.assertFalse(result)

    def test_warning_when_credits_is_not_an_interger(self):
        """In this test, we ensure that the warning of credits is not integer"""
        self.luy_full.credits = Decimal(5.5)
        self.luy_full.save()
        expected_result = [
            _("The credits value should be an integer")
        ]
        result = self.luy_full._check_credits_is_integer()
        self.assertEqual(result, expected_result)

    def test_no_warning_when_credits_is_an_interger(self):
        """In this test, we ensure that the warning is not displayed when of credits is an integer"""
        self.luy_full.credits = Decimal(5)
        self.luy_full.save()
        self.assertFalse(self.luy_full._check_credits_is_integer())

    @mock.patch('base.models.learning_unit_year.LearningUnitYear._check_classes')
    def test_warning_planned_classes_zero_and_volume(self, mock_check_classes_warnings=[]):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.save()

        luy_partim = self.generated_container.generated_container_years[0].learning_unit_year_partim

        learning_component_year_partim_lecturing = LearningComponentYear.objects.filter(
            type=LECTURING,
            learning_unit_year=luy_partim
        ).first()

        learning_component_year_partim_lecturing.planned_classes = 0
        learning_component_year_partim_lecturing.hourly_volume_partial_q1 = 0
        learning_component_year_partim_lecturing.hourly_volume_partial_q2 = 0
        learning_component_year_partim_lecturing.hourly_volume_total_annual = 0
        learning_component_year_partim_lecturing.repartition_volume_requirement_entity = 0
        learning_component_year_partim_lecturing.save()

        self.component_full_lecturing.hourly_volume_partial_q1 = 30
        self.component_full_lecturing.hourly_volume_partial_q2 = 20
        self.component_full_lecturing.hourly_volume_total_annual = 50
        self.component_full_lecturing.planned_classes = 0
        self.component_full_lecturing.repartition_volume_requirement_entity = 0
        self.component_full_lecturing.save()

        excepted_error = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(self.component_full_lecturing.complete_acronym),
            _('planned classes cannot be 0 while volume is greater than 0'))

        self.assertCountEqual(
            self.luy_full.warnings,
            [excepted_error])
        self.assertIn(excepted_error, self.luy_full.warnings)

    @mock.patch('base.models.learning_unit_year.LearningUnitYear._check_classes')
    def test_warning_planned_classes_and_volume_zero(self, mock_check_classes_warnings=[]):
        self.luy_full.credits = Decimal(5)
        self.luy_full.save()
        self.component_full_lecturing.hourly_volume_partial_q1 = 0
        self.component_full_lecturing.hourly_volume_partial_q2 = 0
        self.component_full_lecturing.hourly_volume_total_annual = 0
        self.component_full_lecturing.repartition_volume_requirement_entity = 0
        self.component_full_lecturing.planned_classes = 1
        self.component_full_lecturing.save()

        excepted_error = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(self.component_full_lecturing.complete_acronym),
            _('planned classes cannot be greather than 0 while volume is equal to 0'))
        self.assertCountEqual(
            self.luy_full._check_learning_component_year_warnings(),
            [excepted_error])
        self.assertIn(excepted_error, self.luy_full._check_learning_component_year_warnings())

    @mock.patch('base.models.learning_unit_year.LearningUnitYear._check_classes')
    def test_warning_multiple_partims(self, mock_check_classes_warnings=[]):
        """
            In this test, we ensure that the warnings of partim_b doesn't show up while
            viewing partim_a identification information
        """

        learning_unit_container_year = LearningContainerYearFactory(
            academic_year=self.generated_ac_years[0]
        )
        LearningUnitYearFactory(
            acronym="LCHIM1210",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.FULL,
            academic_year=self.generated_ac_years[0]
        )
        partim_a_with_warnings = LearningUnitYearFactory(
            acronym="LCHIM1210A",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.generated_ac_years[0]
        )
        LecturingLearningComponentYearFactory(learning_unit_year=partim_a_with_warnings,
                                              hourly_volume_partial_q1=10,
                                              hourly_volume_partial_q2=10,
                                              hourly_volume_total_annual=10)
        partim_b_with_warnings = LearningUnitYearFactory(
            acronym="LCHIM1210B",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.generated_ac_years[0]
        )
        LecturingLearningComponentYearFactory(learning_unit_year=partim_b_with_warnings,
                                              hourly_volume_partial_q1=10,
                                              hourly_volume_partial_q2=10,
                                              hourly_volume_total_annual=10)

        warning_messages = ''.join(str(e) for e in partim_a_with_warnings._check_learning_component_year_warnings())
        self.assertIn(partim_a_with_warnings.acronym, warning_messages)
        self.assertNotIn(partim_b_with_warnings.acronym, warning_messages)

    def test_warning_no_stage_dimona_with_internship(self):
        """In this test, we ensure that the warning is displayed when internship is set and not stage_dimona"""
        self.luy_full.stage_dimona = False
        self.luy_full.learning_container_year.container_type = learning_container_year_types.INTERNSHIP
        self.luy_full.save()
        excepted_error = _('The learning unit is not a Stage-Dimona activity although it is an internship type.')
        self.assertIn(excepted_error, self.luy_full._check_stage_dimona())


class TestQuadriConsistency(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ay = create_current_academic_year()

    def setUp(self):
        self.luy_full = LearningUnitYearFactory(academic_year=self.ay,
                                                subtype=learning_unit_year_subtypes.FULL,
                                                quadrimester=None)
        self.learning_component_year_full_lecturing = LearningComponentYearFactory(learning_unit_year=self.luy_full)

    @patch.multiple(LearningComponentYearQuadriStrategy, __abstractmethods__=set())
    def test_is_valid_present(self):
        instance = LearningComponentYearQuadriStrategy(lcy=self.learning_component_year_full_lecturing)
        with self.assertRaises(NotImplementedError):
            self.assertRaises(NotImplementedError, instance.is_valid())

    def test_no_strategy(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.save()

        test_cases = [
            {'vol_q1': 20, 'vol_q2': None, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
            {'vol_q1': None, 'vol_q2': 20, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
            {'vol_q1': 10, 'vol_q2': 10, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
            {'vol_q1': None, 'vol_q2': None, 'vol_tot_annual': None, 'planned_classes': None, 'vol_tot_global': None},
        ]

        for case in test_cases:
            self._update_lecturing_component_volumes(case)

        self.assertTrue(
            LearningComponentYearQuadriNoStrategy(lcy=self.learning_component_year_full_lecturing).is_valid())

    def test_ok_volumes_for_Q1(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q1.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': 20, 'vol_q2': None, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
        ]

        self._update_lecturing_component_volumes(test_cases[0])

        self.assertTrue(LearningComponentYearQ1Strategy(lcy=self.learning_component_year_full_lecturing).is_valid())

    def test_warning_volumes_for_Q1(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q1.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': None, 'vol_q2': 20, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
        ]

        for case in test_cases:
            self._update_lecturing_component_volumes(case)

        excepted_error = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(
                self.learning_component_year_full_lecturing.complete_acronym),
            _('Only the volume Q1 must have a value'))

        self.assertIn(excepted_error, self.luy_full.warnings)

    def _update_lecturing_component_volumes(self, case):
        with self.subTest(case=case):
            self.learning_component_year_full_lecturing.hourly_volume_partial_q1 = case.get('vol_q1')
            self.learning_component_year_full_lecturing.hourly_volume_partial_q2 = case.get('vol_q2')
            self.learning_component_year_full_lecturing.hourly_volume_total_annual = case.get('vol_tot_annual')
            self.learning_component_year_full_lecturing.planned_classes = case.get('planned_classes')
            self.learning_component_year_full_lecturing.repartition_volume_requirement_entity = case.get(
                'vol_tot_global')
            self.learning_component_year_full_lecturing.save()

    def test_ok_volumes_for_Q2(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q2.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': None, 'vol_q2': 20, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
        ]

        self._update_lecturing_component_volumes(test_cases[0])

        self.assertTrue(LearningComponentYearQ2Strategy(lcy=self.learning_component_year_full_lecturing).is_valid())

    def test_warning_volumes_for_Q2(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q2.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': 20, 'vol_q2': None, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20}
        ]

        for case in test_cases:
            self._update_lecturing_component_volumes(case)

        excepted_error = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(
                self.learning_component_year_full_lecturing.complete_acronym),
            _('Only the volume Q2 must have a value'))

        self.assertIn(excepted_error, self.luy_full.warnings)

    def test_ok_volumes_for_Q1and2(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q1and2.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': 10, 'vol_q2': 10, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
        ]

        self._update_lecturing_component_volumes(test_cases[0])

        self.assertTrue(LearningComponentYearQ1and2Strategy(lcy=self.learning_component_year_full_lecturing).is_valid())

    def test_warning_volumes_for_Q1and2(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q1and2.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': 20, 'vol_q2': None, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
            {'vol_q1': None, 'vol_q2': 20, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
            {'vol_q1': None, 'vol_q2': None, 'vol_tot_annual': None, 'planned_classes': None, 'vol_tot_global': None}
        ]

        for case in test_cases:
            self._update_lecturing_component_volumes(case)

        excepted_error = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(
                self.learning_component_year_full_lecturing.complete_acronym),
            _('The volumes Q1 and Q2 must have a value'))

        self.assertIn(excepted_error, self.luy_full.warnings)

    def test_ok_volumes_for_Q1or2(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q1or2.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': 20, 'vol_q2': None, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
            {'vol_q1': None, 'vol_q2': 20, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
        ]

        for case in test_cases:
            self._update_lecturing_component_volumes(case)

        self.assertTrue(LearningComponentYearQ1or2Strategy(lcy=self.learning_component_year_full_lecturing).is_valid())

    def test_warning_volumes_for_Q1or2(self):
        self.luy_full.credits = self.luy_full.credits + 1
        self.luy_full.quadrimester = quadrimesters.LearningUnitYearQuadrimester.Q1or2.name
        self.luy_full.save()

        test_cases = [
            {'vol_q1': 10, 'vol_q2': 10, 'vol_tot_annual': 20, 'planned_classes': 1, 'vol_tot_global': 20},
            {'vol_q1': None, 'vol_q2': None, 'vol_tot_annual': None, 'planned_classes': None, 'vol_tot_global': None}
        ]

        for case in test_cases:
            self._update_lecturing_component_volumes(case)

        excepted_error = "{} ({})".format(
            _('Volumes of {} are inconsistent').format(
                self.learning_component_year_full_lecturing.complete_acronym),
            _('The volume Q1 or Q2 must have a value but not both'))

        self.assertIn(excepted_error, self.luy_full.warnings)


class ContainerTypeVerboseTest(TestCase):
    """Unit tests on container_type_verbose()"""

    def test_normal_case(self):
        external_learning_unit = ExternalLearningUnitYearFactory(
            learning_unit_year__learning_container_year__container_type=LearningContainerYearType.OTHER_INDIVIDUAL.name,
            co_graduation=False
        )
        result = external_learning_unit.learning_unit_year.container_type_verbose
        expected_result = external_learning_unit.learning_unit_year.learning_container_year.get_container_type_display()
        self.assertEqual(result, expected_result)

    def test_when_is_external_of_mobility(self):
        external_learning_unit = ExternalLearningUnitYearFactory(
            learning_unit_year__learning_container_year__container_type=LearningContainerYearType.EXTERNAL.name,
            mobility=True,
            co_graduation=False
        )
        result = external_learning_unit.learning_unit_year.container_type_verbose
        self.assertEqual(result, _("Mobility"))

    def test_when_is_course(self):
        external_learning_unit = ExternalLearningUnitYearFactory(
            learning_unit_year__learning_container_year__container_type=LearningContainerYearType.COURSE.name,
        )
        luy = external_learning_unit.learning_unit_year
        result = luy.container_type_verbose
        expected_result = '{} ({})'.format(
            luy.learning_container_year.get_container_type_display(),
            luy.get_subtype_display()
        )
        self.assertEqual(result, expected_result)

    def test_when_is_internship(self):
        external_learning_unit = ExternalLearningUnitYearFactory(
            learning_unit_year__learning_container_year__container_type=LearningContainerYearType.INTERNSHIP.name,
            learning_unit_year__subtype=learning_unit_year_subtypes.FULL,
        )
        luy = external_learning_unit.learning_unit_year
        result = luy.container_type_verbose
        expected_result = '{} ({})'.format(
            luy.learning_container_year.get_container_type_display(),
            luy.get_subtype_display()
        )
        self.assertEqual(result, expected_result)


class LearningUnitYearDeleteCms(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.translated_text = LearningUnitYearTranslatedTextFactory(reference=cls.learning_unit_year.id)

        cls.learning_unit_year_no_cms = LearningUnitYearFactory()

    def test_delete_learning_unit_yr_and_cms(self):
        luy_id = self.learning_unit_year.id
        self.learning_unit_year.delete()
        self.assertCountEqual(list(TranslatedText.objects.filter(id=self.translated_text.id)), [])
        self.assertCountEqual(list(TranslatedText.objects.filter(reference=luy_id)), [])

    def test_delete_learning_unit_yr_without_cms(self):
        luy_id = self.learning_unit_year_no_cms.id
        self.learning_unit_year_no_cms.delete()
        self.assertCountEqual(list(TranslatedText.objects.filter(reference=luy_id)), [])


class LearningUnitYearCheckVolumeConsistencyWithUeWarnings(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.lecturing_component = LecturingLearningComponentYearFactory(
            learning_unit_year=cls.learning_unit_year,
            planned_classes=1
        )

    def test_check_with_no_classes(self):
        LearningUnitYearFactory()
        query_components = _get_components_with_classes()
        messages = learning_unit_year._check_volume_consistency_with_ue(list(query_components))
        self.assertEqual(len(messages), 0)

    def test_check_with_class_volume_inconsistent(self):
        learning_class = LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_total_annual + 1
        )
        query_components = _get_components_with_classes()
        messages = learning_unit_year._check_volume_consistency_with_ue(list(query_components))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            self._build_check_consistency_volume_message(learning_class)
        )

    def test_check_with_class_volume_consistent(self):
        LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_total_annual,
            hourly_volume_partial_q2=0
        )
        query_components = _get_components_with_classes()
        messages = learning_unit_year._check_volume_consistency_with_ue(list(query_components))
        self.assertEqual(len(messages), 0)

    def _build_check_consistency_volume_message(self, learning_class):
        return _(
            'Class volumes of class %(code_ue)s%(separator)s%(code_class)s are inconsistent '
            '(Annual volume must be equal to the sum of volume Q1 and Q2)'
        ) % {
            'code_ue': self.learning_unit_year.acronym,
            'separator': '-' if learning_class.learning_component_year.type == LECTURING else '_',
            'code_class': learning_class.acronym
        }

    def test_check_number_of_classes_correct(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(
            component=self.lecturing_component,
            number_of_occurence=self.lecturing_component.planned_classes
        )
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 0)

    def test_check_number_of_classes_inconsistent(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(
            component=self.lecturing_component,
            number_of_occurence=self.lecturing_component.planned_classes + 1
        )
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _(
                'The planned classes number and the effective classes number of %(code_ue)s/%(component_code)s '
                'is not consistent'
            ) % {
                'code_ue': self.learning_unit_year.acronym,
                'component_code': 'PM'
            }
        )


class LearningUnitYearCheckNumberOfClassesWarnings(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.lecturing_component = LecturingLearningComponentYearFactory(
            learning_unit_year=cls.learning_unit_year,
            planned_classes=2
        )

    def test_check_number_of_classes_not_enough(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(component=self.lecturing_component, number_of_occurence=1)
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            self._build_check_number_of_classes_message()
        )

    def test_check_number_of_classes_too_much(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(component=self.lecturing_component, number_of_occurence=3)
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            self._build_check_number_of_classes_message()
        )

    def _build_check_number_of_classes_message(self):
        return _('The planned classes number and the effective classes number of %(code_ue)s/%(component_code)s '
                 'is not consistent') % \
               {
                   'code_ue': self.learning_unit_year.acronym,
                   'component_code': 'PM'
               }

    def test_check_number_of_classes_correct(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(
            component=self.lecturing_component,
            number_of_occurence=self.lecturing_component.planned_classes
        )
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 0)


class LearningUnitYearCheckClassesVolumesWarnings(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.lecturing_component = LecturingLearningComponentYearFactory(
            learning_unit_year=cls.learning_unit_year,
            hourly_volume_total_annual=30,
            hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=20,
        )

    def test_check_quadrimester_volume_consistent(self):
        LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_partial_q1,
            hourly_volume_partial_q2=self.lecturing_component.hourly_volume_partial_q2
        )
        query_components = _get_components_with_classes()

        messages = learning_unit_year._check_classes_volumes(list(query_components))
        self.assertEqual(len(messages), 0)

    def test_check_quadrimester_volume_inconsistent_too_high(self):
        too_high_volume = self.lecturing_component.hourly_volume_partial_q2 * 2
        effective_class = LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_partial_q1,
            hourly_volume_partial_q2=too_high_volume
        )
        query_components = _get_components_with_classes()
        messages = learning_unit_year._check_classes_volumes(list(query_components))
        self.assertEqual(len(messages), 2)
        inconsistent_msg = _('Volumes of {} are inconsistent').format(
            effective_class.effective_class_complete_acronym
        )

        self.assertEqual(
            messages[0],
            "{} ({}) ".format(
                inconsistent_msg,
                _('at least one class volume is greater than the volume of the LU (%(sub_type)s)') % {
                    'sub_type': self.lecturing_component.learning_unit_year.get_subtype_display().lower()
                }
            )

        )
        self.assertEqual(
            messages[1],
            "{} ({}) ".format(
                inconsistent_msg,
                _('the annual volume must be equal to the sum of the volumes Q1 and Q2')
            )

        )

    def test_check_quadrimester_volume_inconsistent_too_low(self):
        too_high_volume = self.lecturing_component.hourly_volume_partial_q2 / 2
        LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_partial_q1,
            hourly_volume_partial_q2=too_high_volume
        )
        query_components = _get_components_with_classes()
        messages = learning_unit_year._check_classes_volumes(list(query_components))
        self.assertEqual(len(messages), 0)


class LearningUnitYearCheckClassesSessionWarnings(TestCase):

    def setUp(self):
        self.message = _('The %(code_class)s derogation session is inconsistent with the LU derogation session '
                         '(should be %(should_be_values)s)')

    def test_check_with_ue_session_1xx(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_1XX)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_1XX)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, '1'))

    def test_check_with_ue_session_x2x(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_X2X)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, '2'))

    def test_check_with_ue_session_xx3(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_XX3)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, '3'))

    def test_check_with_ue_session_12X(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_1XX)
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)
        wrong_values.remove(learning_unit_year_session.SESSION_12X)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_12X)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '1, 2 {} 12'.format(_('or')))
        )

    def test_check_with_ue_session_1x3(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_1X3)
        wrong_values.remove(learning_unit_year_session.SESSION_1XX)
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_1X3)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '1, 3 {} 13'.format(_('or')))
        )

    def test_check_with_ue_session_x23(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)
        wrong_values.remove(learning_unit_year_session.SESSION_X23)
        wrong_values.remove(learning_unit_year_session.SESSION_P23)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_X23)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '2, 3, 23 {} P23'.format(_('or')))
        )

    def test_check_with_ue_session_p23(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)
        wrong_values.remove(learning_unit_year_session.SESSION_X23)
        wrong_values.remove(learning_unit_year_session.SESSION_P23)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_P23)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '2, 3, 23 {} P23'.format(_('or')))
        )

    def test_check_with_ue_session_correct(self):
        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_1XX)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        LearningClassYearFactory(
            learning_component_year=component,
            session=learning_unit_year_session.SESSION_1XX
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 0)


class LearningUnitYearCheckClassesQuadrimesterWarnings(TestCase):

    def setUp(self):
        self.message = _('The %(code_class)s quadrimester is inconsistent with the LU quadrimester '
                         '(should be %(should_be_values)s)')

    def test_check_with_ue_quadrimester_q1(self):
        wrong_values = ALL_QUADRIMESTER_VALUES.copy()
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q1.name)

        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1.value)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, 'Q1'))

    def test_check_with_ue_quadrimester_q2(self):
        wrong_values = ALL_QUADRIMESTER_VALUES.copy()
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q2.name)

        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q2.value)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, 'Q2'))

    def test_check_with_ue_quadrimester_q3(self):
        wrong_values = ALL_QUADRIMESTER_VALUES.copy()
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q3.name)

        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q3.value)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, 'Q3'))

    def test_check_with_ue_quadrimester_q1_and_q2(self):
        wrong_values = [quadrimesters.LearningUnitYearQuadrimester.Q3.name]
        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1and2.name)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, 'Q1 {}/{} Q2'.format(_('and'), _('or')))
        )

    def test_check_with_ue_quadrimester_q1_or_q2(self):
        wrong_values = ALL_QUADRIMESTER_VALUES.copy()
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q1or2.name)
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q1.name)
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q2.name)

        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1or2.name)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, 'Q1 {} Q2'.format(_('or')))
        )


def _build_expected_message(message, effective_class, should_be_values_str):
    return message % {
        'code_class': effective_class.effective_class_complete_acronym,
        'should_be_values': should_be_values_str
    }


def _get_components_with_classes():
    return LearningComponentYear.objects.all().prefetch_related(
        models.Prefetch('learningclassyear_set', to_attr="classes")
    )


def _build_effective_classes(component: LearningComponentYear, number_of_occurence: int) -> None:
    factories = []
    for cpt in range(number_of_occurence):
        factories.append(LearningClassYearFactory(learning_component_year=component))


class LearningUnitYearAndClassTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        luy_class = LearningClassYearFactory()
        cls.learning_unit_year_with_class = luy_class.learning_component_year.learning_unit_year
        cls.luy_without_class = LearningUnitYearFactory()

    def test_has_class_this_year(self):
        self.assertTrue(self.learning_unit_year_with_class.has_class_this_year_or_in_future())
        self.assertFalse(self.luy_without_class.has_class_this_year_or_in_future())

    def test_has_class_in_future(self):
        luy_this_year = LearningUnitYearFactory()
        next_year = AcademicYearFactory(year=luy_this_year.academic_year.year + 1)
        luy_in_future = LearningUnitYearFactory(learning_unit=luy_this_year.learning_unit, academic_year=next_year)
        LearningClassYearFactory(learning_component_year__learning_unit_year=luy_in_future)
        self.assertTrue(luy_this_year.has_class_this_year_or_in_future())


class LearningUnitYearCheckNumberOfClassesWarnings(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.lecturing_component = LecturingLearningComponentYearFactory(
            learning_unit_year=cls.learning_unit_year,
            planned_classes=2
        )

    def test_check_number_of_classes_not_enough(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(component=self.lecturing_component, number_of_occurence=1)
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            self._build_check_number_of_classes_message()
        )

    def test_check_number_of_classes_too_much(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(component=self.lecturing_component, number_of_occurence=3)
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            self._build_check_number_of_classes_message()
        )

    def _build_check_number_of_classes_message(self):
        return _('The planned classes number and the effective classes number of %(code_ue)s/%(component_code)s '
                 'is not consistent') % \
               {
                   'code_ue': self.learning_unit_year.acronym,
                   'component_code': 'PM'
               }

    def test_check_number_of_classes_correct(self):
        query_components = _get_components_with_classes()
        _build_effective_classes(
            component=self.lecturing_component,
            number_of_occurence=self.lecturing_component.planned_classes
        )
        messages = learning_unit_year._check_number_of_classes(list(query_components))
        self.assertEqual(len(messages), 0)


class LearningUnitYearCheckClassesVolumesWarnings(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.lecturing_component = LecturingLearningComponentYearFactory(
            learning_unit_year=cls.learning_unit_year,
            hourly_volume_total_annual=30,
            hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=20,
        )

    def test_check_quadrimester_volume_consistent(self):
        LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_partial_q1,
            hourly_volume_partial_q2=self.lecturing_component.hourly_volume_partial_q2
        )
        query_components = _get_components_with_classes()

        messages = learning_unit_year._check_classes_volumes(list(query_components))
        self.assertEqual(len(messages), 0)

    def test_check_quadrimester_volume_inconsistent_too_high(self):
        too_high_volume = self.lecturing_component.hourly_volume_partial_q2 * 2
        effective_class = LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_partial_q1,
            hourly_volume_partial_q2=too_high_volume
        )
        query_components = _get_components_with_classes()
        messages = learning_unit_year._check_classes_volumes(list(query_components))
        self.assertEqual(len(messages), 2)
        inconsistent_msg = _('Volumes of {} are inconsistent').format(
            effective_class.effective_class_complete_acronym
        )

        self.assertEqual(
            messages[0],
            "{} ({}) ".format(
                inconsistent_msg,
                _('at least one class volume is greater than the volume of the LU (%(sub_type)s)') % {
                    'sub_type': self.lecturing_component.learning_unit_year.get_subtype_display().lower()
                }
            )

        )
        self.assertEqual(
            messages[1],
            "{} ({}) ".format(
                inconsistent_msg,
                _('the annual volume must be equal to the sum of the volumes Q1 and Q2')
            )

        )

    def test_check_quadrimester_volume_inconsistent_too_low(self):
        too_high_volume = self.lecturing_component.hourly_volume_partial_q2 / 2
        LearningClassYearFactory(
            learning_component_year=self.lecturing_component,
            hourly_volume_partial_q1=self.lecturing_component.hourly_volume_partial_q1,
            hourly_volume_partial_q2=too_high_volume
        )
        query_components = _get_components_with_classes()
        messages = learning_unit_year._check_classes_volumes(list(query_components))
        self.assertEqual(len(messages), 0)


class LearningUnitYearCheckClassesSessionWarnings(TestCase):

    def setUp(self):
        self.message = _('The %(code_class)s derogation session is inconsistent with the LU derogation session '
                         '(should be %(should_be_values)s)')

    def test_check_with_ue_session_1xx(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_1XX)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_1XX)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, '1'))

    def test_check_with_ue_session_x2x(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_X2X)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, '2'))

    def test_check_with_ue_session_xx3(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_XX3)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, '3'))

    def test_check_with_ue_session_12X(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_1XX)
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)
        wrong_values.remove(learning_unit_year_session.SESSION_12X)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_12X)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '1, 2 {} 12'.format(_('or')))
        )

    def test_check_with_ue_session_1x3(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_1X3)
        wrong_values.remove(learning_unit_year_session.SESSION_1XX)
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_1X3)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '1, 3 {} 13'.format(_('or')))
        )

    def test_check_with_ue_session_x23(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)
        wrong_values.remove(learning_unit_year_session.SESSION_X23)
        wrong_values.remove(learning_unit_year_session.SESSION_P23)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_X23)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '2, 3, 23 {} P23'.format(_('or')))
        )

    def test_check_with_ue_session_p23(self):
        wrong_values = ALL_SESSION_VALUES.copy()
        wrong_values.remove(learning_unit_year_session.SESSION_X2X)
        wrong_values.remove(learning_unit_year_session.SESSION_XX3)
        wrong_values.remove(learning_unit_year_session.SESSION_X23)
        wrong_values.remove(learning_unit_year_session.SESSION_P23)

        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_P23)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            session=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, '2, 3, 23 {} P23'.format(_('or')))
        )

    def test_check_with_ue_session_correct(self):
        luy = LearningUnitYearFactory(session=learning_unit_year_session.SESSION_1XX)
        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        LearningClassYearFactory(
            learning_component_year=component,
            session=learning_unit_year_session.SESSION_1XX
        )

        messages = learning_unit_year._check_classes_session(luy.session, list(_get_components_with_classes()))
        self.assertEqual(len(messages), 0)


class LearningUnitYearCheckClassesQuadrimesterWarnings(TestCase):

    def setUp(self):
        self.message = _('The %(code_class)s quadrimester is inconsistent with the LU quadrimester '
                         '(should be %(should_be_values)s)')

    def test_check_with_ue_quadrimester_q1(self):
        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1.value)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1or2.value
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, 'Q1'))

    def test_check_with_ue_quadrimester_q2(self):
        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q2.value)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1or2.value
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, 'Q2'))

    def test_check_with_ue_quadrimester_q3(self):
        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q3.value)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1or2.value
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], _build_expected_message(self.message, effective_class, 'Q3'))

    def test_check_with_ue_quadrimester_q1_and_q2(self):
        wrong_values = [quadrimesters.LearningUnitYearQuadrimester.Q3.name]
        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1and2.name)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=random.choice(wrong_values)
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, 'Q1 {}/{} Q2'.format(_('and'), _('or')))
        )

    def test_check_with_ue_quadrimester_q1_or_q2(self):
        wrong_values = ALL_QUADRIMESTER_VALUES.copy()
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q1or2.name)
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q1.name)
        wrong_values.remove(quadrimesters.LearningUnitYearQuadrimester.Q2.name)

        luy = LearningUnitYearFactory(quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1or2.name)

        component = LecturingLearningComponentYearFactory(
            learning_unit_year=luy
        )
        effective_class = LearningClassYearFactory(
            learning_component_year=component,
            quadrimester=random.choice(wrong_values),
            hourly_volume_partial_q1=1,
            hourly_volume_partial_q2=1
        )

        messages = learning_unit_year._check_classes_quadrimester(
            luy.quadrimester,
            list(_get_components_with_classes())
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0],
            _build_expected_message(self.message, effective_class, 'Q1 {} Q2'.format(_('or')))
        )


def _build_expected_message(message, effective_class, should_be_values_str):
    return message % {
        'code_class': effective_class.effective_class_complete_acronym,
        'should_be_values': should_be_values_str
    }


def _get_components_with_classes():
    return LearningComponentYear.objects.all().prefetch_related(
        models.Prefetch('learningclassyear_set', to_attr="classes")
    )


def _build_effective_classes(component: LearningComponentYear, number_of_occurence: int) -> None:
    for cpt in range(number_of_occurence):
        LearningClassYearFactory(learning_component_year=component)
