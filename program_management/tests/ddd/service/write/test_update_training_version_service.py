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
import attr

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.constraint_type import ConstraintTypeEnum
from base.models.enums.education_group_types import TrainingType
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.ddd import command
from education_group.ddd.service.read import get_training_service
from program_management.ddd.command import UpdateTrainingVersionCommand
from program_management.ddd.domain.program_tree_version import NOT_A_TRANSITION, STANDARD
from program_management.ddd.service.write import update_and_postpone_training_version_service, \
    create_training_with_program_tree
from testing.testcases import DDDTestCase


# TODO implement test when finalities present
# TODO implement test when transitions present
# TODO should generate a specific version training
class TestUpdateTrainingVersion(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.trainings = self.generate_trainings()

        self.cmd = UpdateTrainingVersionCommand(
            offer_acronym="INFO100B",
            version_name=STANDARD,
            transition_name=NOT_A_TRANSITION,
            year=2021,
            credits=23,
            end_year=None,
            title_fr="Bachelier en info",
            title_en="Bachelor info",
            teaching_campus_name="LLN",
            management_entity_acronym="INFO",
            teaching_campus_organization_name='UCL',
            constraint_type=None,
            min_constraint=None,
            max_constraint=None,
            remark_fr=None,
            remark_en=None,
        )

    def test_credits_must_be_greater_than_0(self):
        cmd = attr.evolve(self.cmd, credits=-1)

        with self.assertRaises(MultipleBusinessExceptions):
            update_and_postpone_training_version_service.update_and_postpone_training_version(cmd)

    def test_constraints_must_be_legit(self):
        cmd = attr.evolve(self.cmd, min_constraint=150)

        with self.assertRaises(MultipleBusinessExceptions):
            update_and_postpone_training_version_service.update_and_postpone_training_version(cmd)


    def generate_trainings(self):
        cmd = command.CreateAndPostponeTrainingAndProgramTreeCommand(
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
            ares_code=10,
            ares_graca=25,
            ares_authorization=15,
            code_inter_cfb=None,
            coefficient=None,
            academic_type=None,
            duration_unit=None,
            leads_to_diploma=True,
            printing_title='',
            professional_title='',
            can_be_funded=True,
        )

        training_identities = create_training_with_program_tree.create_and_report_training_with_program_tree(cmd)

        return [
            get_training_service.get_training(command.GetTrainingCommand(acronym=identity.acronym, year=identity.year))
            for identity in training_identities
        ]
