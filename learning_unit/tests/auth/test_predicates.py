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
import mock
from django.test import TestCase

from base.models.enums import learning_unit_year_subtypes
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory, CloseAcademicCalendarFactory
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearPartimFactory, LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from learning_unit.auth import predicates
from learning_unit.auth.predicates import is_learning_unit_container_type_deletable
from base.models.enums.learning_container_year_types import LearningContainerYearType


class TestIsLearningUnitContainerTypeDeletableForPartim(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()

    def test_is_learning_unit_container_type_deletable_for_partim(self):
        partim_ue = LearningUnitYearPartimFactory()
        self.assertTrue(is_learning_unit_container_type_deletable(self.person.user, partim_ue))


class TestIsLearningUnitSummaryEditionCalendarOpen(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.learning_unit_year = LearningUnitYearFactory()

    def setUp(self) -> None:
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_learning_unit_summary_edition_calendar_opened(self):
        OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )

        self.assertTrue(
            predicates.is_learning_unit_summary_edition_calendar_open(self.person.user, self.learning_unit_year)
        )

    def test_learning_unit_summary_edition_calendar_closed(self):
        CloseAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )

        self.assertFalse(
            predicates.is_learning_unit_summary_edition_calendar_open(self.person.user, self.learning_unit_year)
        )


class TestIsLearningUnitForceMajeurSummaryEditionCalendarOpen(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.learning_unit_year = LearningUnitYearFactory()

    def setUp(self) -> None:
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_learning_unit_summary_force_majeur_edition_calendar_opened(self):
        OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE.name,
            data_year=self.learning_unit_year.academic_year
        )

        self.assertTrue(
            predicates.is_learning_unit_force_majeur_summary_edition_calendar_open(
                self.person.user, self.learning_unit_year
            )
        )

    def test_learning_unit_summary_force_majeur_edition_calendar_closed(self):
        CloseAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE.name,
            data_year=self.learning_unit_year.academic_year
        )

        self.assertFalse(
            predicates.is_learning_unit_force_majeur_summary_edition_calendar_open(
                self.person.user,
                self.learning_unit_year
            )
        )


class TestIsLearningUnitSummaryEditable(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()

    def setUp(self) -> None:
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_is_learning_unit_year_summary_editable(self):
        learning_unit_year = LearningUnitYearFactory(summary_locked=False)

        self.assertTrue(
            predicates.is_learning_unit_year_summary_editable(self.person.user, learning_unit_year)
        )

    def test_is_not_learning_unit_year_summary_editable(self):
        learning_unit_year = LearningUnitYearFactory(summary_locked=True)

        self.assertFalse(
            predicates.is_learning_unit_year_summary_editable(self.person.user, learning_unit_year)
        )


class TestCanCreateClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()

    def setUp(self) -> None:
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_is_learning_unit_year_container_type_editable_to_create_classe(self):
        eligible_types = LearningContainerYearType.all()

        eligible_types.remove(LearningContainerYearType.EXTERNAL)
        luy = LearningUnitYearFactory(
            learning_container_year__container_type=LearningContainerYearType.EXTERNAL.name
        )
        self.assertFalse(
            predicates.is_learning_unit_year_container_type_editable_to_create_classe(self.person.user, luy)
        )
        for container_type in eligible_types:
            luy = LearningUnitYearFactory(
                learning_container_year__container_type=container_type.name
            )
            self.assertTrue(
                predicates.is_learning_unit_year_container_type_editable_to_create_classe(self.person.user, luy)
            )

    def test_check_the_original_learning_unit_a_not_partim(self):
        luy = LearningUnitYearPartimFactory()
        self.assertFalse(predicates.check_the_original_learning_unit_a_not_partim(self.person.user, luy))
        luy = LearningUnitYearFactory()
        self.assertTrue(predicates.check_the_original_learning_unit_a_not_partim(self.person.user, luy))

    def test_has_no_partim(self):
        luy = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.FULL)
        self.assertTrue(predicates.has_no_partim(self.person.user, luy))

    def test_has_no_partim_false(self):
        luy_with_partim = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.FULL)
        LearningUnitYearPartimFactory(learning_container_year=luy_with_partim.learning_container_year)
        self.assertFalse(predicates.has_no_partim(self.person.user, luy_with_partim))

    def test_has_global_volume_greater_than_0_is_false(self):
        luy = LearningUnitYearFactory()
        LecturingLearningComponentYearFactory(learning_unit_year=luy, hourly_volume_total_annual=0)
        PracticalLearningComponentYearFactory(learning_unit_year=luy, hourly_volume_total_annual=0)
        self.assertFalse(predicates.has_global_volume_greater_than_0(self.person.user, luy))

    def test_has_global_volume_greater_than_0(self):
        luy = LearningUnitYearFactory()
        LecturingLearningComponentYearFactory(learning_unit_year=luy, repartition_volume_requirement_entity=30)
        self.assertTrue(predicates.has_global_volume_greater_than_0(self.person.user, luy))

    def test_has_no_enrollment(self):
        luy = LearningUnitYearFactory()
        self.assertTrue(predicates.has_no_enrollment(self.person.user, luy))
        LearningUnitEnrollmentFactory(learning_unit_year=luy)
        self.assertFalse(predicates.has_no_enrollment(self.person.user, luy))
