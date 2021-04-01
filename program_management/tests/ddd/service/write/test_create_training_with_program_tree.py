# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
# ############################################################################
from collections import namedtuple

import mock
from django.test import TestCase

from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.constraint_type import ConstraintTypeEnum
from base.models.enums.education_group_types import TrainingType
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.ddd import command
from education_group.ddd.domain import training
from education_group.ddd.domain.training import TrainingIdentity
from education_group.tests.ddd.factories.command.create_and_postpone_training_and_tree_command import \
    CreateAndPostponeTrainingAndProgramTreeCommandFactory
from program_management.ddd.domain import program_tree, program_tree_version
from program_management.ddd.domain.program_tree_version import NOT_A_TRANSITION
from program_management.ddd.domain.service.calculate_end_postponement import DEFAULT_YEARS_TO_POSTPONE
from program_management.ddd.service.write import create_training_with_program_tree
from testing.testcases import DDDTestCase


class TestCreateAndReportTrainingWithProgramTree(DDDTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.starting_academic_year_year = 2020
        cls.max_postponement_year = cls.starting_academic_year_year + DEFAULT_YEARS_TO_POSTPONE

    def setUp(self) -> None:
        super().setUp()

        self.cmd = command.CreateAndPostponeTrainingAndProgramTreeCommand(
            code="INFO1BA",
            year=2021,
            type=TrainingType.BACHELOR.name,
            abbreviated_title="INFO100B",
            title_fr="Bachelier en info",
            title_en="Bachelor info",
            keywords="",
            status=ActiveStatusEnum.ACTIVE.name,
            schedule_type=ScheduleTypeEnum.DAILY.name,
            credits=180,
            constraint_type=ConstraintTypeEnum.CREDITS.name,
            min_constraint=0,
            max_constraint=5,
            remark_fr="",
            remark_en="",
            start_year=2021,
            end_year=None,
            duration=3,
            partial_title_fr=None,
            partial_title_en=None,
            internship_presence=None,
            is_enrollment_enabled=False,
            has_online_re_registration=False,
            has_partial_deliberation=False,
            has_admission_exam=False,
            has_dissertation=False,
            produce_university_certificate=True,
            decree_category=None,
            rate_code=None,
            main_language='French',
            english_activities=None,
            other_language_activities=None,
            internal_comment="",
            main_domain_code=None,
            main_domain_decree=None,
            secondary_domains=[],
            isced_domain_code=None,
            management_entity_acronym="INFO",
            administration_entity_acronym="INFO",
            teaching_campus_name="LLN",
            teaching_campus_organization_name='UCL',
            enrollment_campus_name="LLN",
            enrollment_campus_organization_name="UCL",
            other_campus_activities=None,
            funding_orientation=None,
            can_be_international_funded=True,
            international_funding_orientation=None,
            ares_code=None,
            ares_graca=None,
            ares_authorization=None,
            code_inter_cfb=None,
            coefficient=None,
            academic_type=None,
            duration_unit=None,
            leads_to_diploma=True,
            printing_title='',
            professional_title='',
            can_be_funded=True,
        )

        self.mock_service(
            "base.models.academic_year.starting_academic_year",
            return_value=namedtuple("academic_year", "year")(self.starting_academic_year_year)
        )

    def test_should_return_identities_of_trainings_created(self):
        result = create_training_with_program_tree.create_and_report_training_with_program_tree(self.cmd)

        expected = [
            TrainingIdentity(acronym=self.cmd.abbreviated_title, year=year)
            for year in range(2021, self.max_postponement_year+1)
        ]
        self.assertListEqual(expected, result)
