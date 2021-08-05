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
import attr
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from base.business.learning_units.quadrimester_strategy import QUADRIMESTER_CHECK_RULES
from base.business.learning_units.session_strategy import SESSION_CHECK_RULES
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.commands import GetEffectiveClassWarningsCommand
from ddd.logic.learning_unit.domain.model._volumes_repartition import ClassVolumes
from ddd.logic.learning_unit.tests.factory.effective_class import LecturingEffectiveClassFactory
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001CourseLearningUnitFactory
from ddd.logic.learning_unit.use_case.read.get_effective_class_warnings_service import get_effective_class_warnings
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class TestGetEffectiveClassWarningsService(TestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.effective_class_repository = EffectiveClassRepository()

        self.learning_unit = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(self.learning_unit)
        self.effective_class = LecturingEffectiveClassFactory(
            entity_id__learning_unit_identity=self.learning_unit.entity_id,
            volumes=ClassVolumes(
                volume_first_quadrimester=self.learning_unit.lecturing_part.volumes.volume_first_quadrimester,
                volume_second_quadrimester=self.learning_unit.lecturing_part.volumes.volume_second_quadrimester,
            ),
            derogation_quadrimester=self.learning_unit.derogation_quadrimester,
            session_derogation=self.learning_unit.derogation_session.value
        )
        self.cmd = GetEffectiveClassWarningsCommand(
            class_code=self.effective_class.class_code,
            learning_unit_year=self.learning_unit.year,
            learning_unit_code=self.learning_unit.code,
        )

    def test_should_get_no_warning(self):
        self.effective_class_repository.save(self.effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertFalse(warnings)

    def test_should_get_volume_greater_than_learning_unit_volume_warning(self):
        effective_class = attr.evolve(
            self.effective_class,
            volumes=ClassVolumes(
                volume_first_quadrimester=self.learning_unit.lecturing_part.volumes.volume_first_quadrimester + 1,
                volume_second_quadrimester=self.learning_unit.lecturing_part.volumes.volume_second_quadrimester - 1
            )
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        inconsistent_msg = _('Volumes of {} are inconsistent').format(
            effective_class.complete_acronym
        )
        self.assertIn(
            "{} ({}) ".format(
                inconsistent_msg,
                _('at least one class volume is greater than the volume of the LU')
            ),
            warnings
        )

    def test_should_get_volumes_sum_greater_than_learning_unit_volume_annual_warning(self):
        effective_class = attr.evolve(
            self.effective_class,
            volumes=ClassVolumes(
                volume_first_quadrimester=self.learning_unit.lecturing_part.volumes.volume_first_quadrimester + 1,
                volume_second_quadrimester=self.learning_unit.lecturing_part.volumes.volume_second_quadrimester + 1
            )
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        inconsistent_msg = _('Volumes of {} are inconsistent').format(
            effective_class.complete_acronym
        )
        self.assertIn(
            "{} ({}) ".format(
                inconsistent_msg,
                _('the annual volume must be equal to the sum of the volumes Q1 and Q2')
            ),
            warnings
        )

    def test_should_get_derogation_quadrimester_inconsistent_with_learning_unit_warning(self):
        learning_unit = attr.evolve(self.learning_unit, derogation_quadrimester=DerogationQuadrimester.Q1)
        self.learning_unit_repository.save(learning_unit)
        effective_class = attr.evolve(
            self.effective_class,
            derogation_quadrimester=DerogationQuadrimester.Q2
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertIn(
            _('The %(code_class)s quadrimester is inconsistent with the LU quadrimester '
              '(should be %(should_be_values)s)') % {
                'code_class': effective_class.complete_acronym,
                'should_be_values': QUADRIMESTER_CHECK_RULES[
                    learning_unit.derogation_quadrimester.name
                ]['available_values_str']
            },
            warnings
        )

    def test_should_get_one_volume_has_to_be_completed_if_q1or2_warning(self):
        effective_class = attr.evolve(
            self.effective_class,
            volumes=ClassVolumes(
                volume_first_quadrimester=0,
                volume_second_quadrimester=0
            ),
            derogation_quadrimester=DerogationQuadrimester.Q1or2
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertIn(
            _('The %(effective_class_complete_acronym)s volumes are inconsistent (the Q1 or Q2 volume has to be '
              'completed but not both)') % {
                'effective_class_complete_acronym': effective_class.complete_acronym
            },
            warnings
        )

    def test_should_get_both_volumes_has_to_be_completed_if_q1and2_warning(self):
        effective_class = attr.evolve(
            self.effective_class,
            volumes=ClassVolumes(
                volume_first_quadrimester=self.learning_unit.lecturing_part.volumes.volume_first_quadrimester,
                volume_second_quadrimester=0
            )
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertIn(
            _('The %(effective_class_complete_acronym)s volumes are inconsistent (the Q1 and Q2 volumes have to be '
              'completed)') % {
                'effective_class_complete_acronym': effective_class.complete_acronym
            },
            warnings
        )

    def test_should_get_volumes_q2_has_to_be_not_completed_if_q1_warning(self):
        effective_class = attr.evolve(
            self.effective_class,
            volumes=ClassVolumes(
                volume_first_quadrimester=0,
                volume_second_quadrimester=5
            ),
            derogation_quadrimester=DerogationQuadrimester.Q1
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertIn(
            _('The %(effective_class_complete_acronym)s volumes are inconsistent(only the %(quadrimester)s '
              'volume has to be completed)') % {
                'effective_class_complete_acronym': effective_class.complete_acronym,
                'quadrimester': effective_class.derogation_quadrimester.name
            },
            warnings
        )

    def test_should_get_volumes_q1_has_to_be_completed_if_q1_warning(self):
        effective_class = attr.evolve(
            self.effective_class,
            volumes=ClassVolumes(
                volume_first_quadrimester=0,
                volume_second_quadrimester=0
            ),
            derogation_quadrimester=DerogationQuadrimester.Q1
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertIn(
            _('The %(effective_class_complete_acronym)s volumes are inconsistent(the %(quadrimester)s '
              'volume has to be completed)') % {
                'effective_class_complete_acronym': effective_class.complete_acronym,
                'quadrimester': effective_class.derogation_quadrimester.name
            },
            warnings
        )

    def test_should_get_derogation_session_inconsistent_with_learning_unit_warning(self):
        effective_class = attr.evolve(
            self.effective_class,
            session_derogation=DerogationSession.DEROGATION_SESSION_X2X
        )
        self.effective_class_repository.save(effective_class)

        warnings = get_effective_class_warnings(
            cmd=self.cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertIn(
            _('The %(code_class)s derogation session is inconsistent with the LU derogation session '
              '(should be %(should_be_values)s)') % {
                'code_class': effective_class.complete_acronym,
                'should_be_values': SESSION_CHECK_RULES[
                    self.learning_unit.derogation_session.value
                ]['available_values_str']
            },
            warnings
        )
