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
from typing import List

from django.utils.translation import ugettext_lazy as _

from base.business.learning_units.quadrimester_strategy import QUADRIMESTER_CHECK_RULES
from base.business.learning_units.session_strategy import SESSION_CHECK_RULES
from base.models.enums.quadrimesters import LearningUnitYearQuadrimester
from ddd.logic.learning_unit.domain.model.effective_class import LecturingEffectiveClass, EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from osis_common.ddd import interface


class EffectiveClassWarnings(interface.DomainService):

    @staticmethod
    def get(effective_class: 'EffectiveClass', learning_unit: 'LearningUnit') -> List[str]:
        _warnings = []
        _warnings.extend(_check_classes_volumes(effective_class, learning_unit))
        if effective_class.derogation_quadrimester:
            _warnings.extend(_check_classes_quadrimester(effective_class, learning_unit))
        if effective_class.session_derogation:
            _warnings.extend(_check_classes_session(effective_class, learning_unit))
        return _warnings


def _check_classes_quadrimester(effective_class: 'EffectiveClass', learning_unit: 'LearningUnit') -> List[str]:
    _warnings = []
    message = _('The %(code_class)s quadrimester is inconsistent with the LU quadrimester '
                '(should be %(should_be_values)s)')
    quadri = effective_class.derogation_quadrimester
    lu_quadri = learning_unit.derogation_quadrimester

    if quadri and quadri.name not in QUADRIMESTER_CHECK_RULES[lu_quadri.name]['correct_values']:
        _warnings.append(message % {
            'code_class': effective_class.complete_acronym,
            'should_be_values': QUADRIMESTER_CHECK_RULES[lu_quadri.name]['available_values_str']
        })
    _warnings.extend(_check_quadrimester_volume(effective_class))

    return _warnings


def _check_classes_session(effective_class: 'EffectiveClass', learning_unit: 'LearningUnit') -> List[str]:
    _warnings = []
    message = _('The %(code_class)s derogation session is inconsistent with the LU derogation session '
                '(should be %(should_be_values)s)')

    session = effective_class.session_derogation
    lu_session = learning_unit.derogation_session
    if lu_session and session and session not in SESSION_CHECK_RULES[lu_session.value]['correct_values']:
        _warnings.append(message % {
            'code_class': effective_class.complete_acronym,
            'should_be_values': SESSION_CHECK_RULES[lu_session.value]['available_values_str']
        })

    return _warnings


def _check_classes_volumes(effective_class: 'EffectiveClass', learning_unit: 'LearningUnit') -> List[str]:
    _warnings = []

    inconsistent_msg = _('Volumes of {} are inconsistent').format(
        effective_class.complete_acronym
    )

    if _class_volume_exceeds_learning_unit_volume(effective_class, learning_unit):
        _warnings.append(
            "{} ({}) ".format(
                inconsistent_msg,
                _('at least one class volume is greater than the volume of the LU')
            )
        )

    if _class_volumes_sum_in_q1_and_q2_exceeds_annual_volume(effective_class, learning_unit):
        _warnings.append(
            "{} ({}) ".format(
                inconsistent_msg,
                _('the annual volume must be equal to the sum of the volumes Q1 and Q2')
            )
        )

    return _warnings


def _class_volume_exceeds_learning_unit_volume(
        effective_class: 'EffectiveClass',
        learning_unit: 'LearningUnit'
) -> bool:
    learning_unit_part = learning_unit.lecturing_part \
        if type(effective_class) == LecturingEffectiveClass else learning_unit.practical_part
    return effective_class.is_volume_first_quadrimester_greater_than(
        learning_unit_part.volumes.volume_first_quadrimester or 0
    ) or effective_class.is_volume_second_quadrimester_greater_than(
        learning_unit_part.volumes.volume_second_quadrimester or 0
    )


def _class_volumes_sum_in_q1_and_q2_exceeds_annual_volume(
        effective_class: 'EffectiveClass',
        learning_unit: 'LearningUnit'
) -> bool:
    learning_unit_part = learning_unit.lecturing_part \
        if type(effective_class) == LecturingEffectiveClass else learning_unit.practical_part
    class_sum_q1_q2 = (effective_class.volumes.volume_first_quadrimester or 0) + \
                      (effective_class.volumes.volume_second_quadrimester or 0)
    return class_sum_q1_q2 > (learning_unit_part.volumes.volume_annual or 0)


def _check_quadrimester_volume(effective_class: 'EffectiveClass') -> List[str]:
    q1_q2_warnings = _get_q1_q2_warnings(effective_class)
    q1and2_q1or2_warnings = _get_q1and2_q1or2_warnings(effective_class)
    return q1_q2_warnings + q1and2_q1or2_warnings


def _get_q1and2_q1or2_warnings(effective_class: 'EffectiveClass') -> List[str]:
    warnings = []

    quadri = effective_class.derogation_quadrimester.name
    q1and2 = LearningUnitYearQuadrimester.Q1and2.name
    q1or2 = LearningUnitYearQuadrimester.Q1or2.name

    if quadri == q1and2 and not (
            effective_class.volumes.volume_first_quadrimester and effective_class.volumes.volume_second_quadrimester
    ):
        warnings.append(
            _('The %(effective_class_complete_acronym)s volumes are inconsistent (the Q1 and Q2 volumes have to be '
              'completed)') % {
                'effective_class_complete_acronym': effective_class.complete_acronym
            }
        )
    elif quadri == q1or2 and not (
            bool(effective_class.volumes.volume_first_quadrimester) ^  # It is equivalent to a XOR
            bool(effective_class.volumes.volume_second_quadrimester)
    ):
        warnings.append(
            _('The %(effective_class_complete_acronym)s volumes are inconsistent (the Q1 or Q2 volume has to be '
              'completed but not both)') % {
                'effective_class_complete_acronym': effective_class.complete_acronym
            }
        )
    print(quadri, effective_class.volumes)
    return warnings


def _get_q1_q2_warnings(effective_class: 'EffectiveClass') -> List[str]:
    warnings = []

    quadri = effective_class.derogation_quadrimester.name
    q1 = LearningUnitYearQuadrimester.Q1.name
    q2 = LearningUnitYearQuadrimester.Q2.name

    if quadri in [q1, q2]:
        other_quadri_partial_volume = effective_class.volumes.volume_second_quadrimester \
            if quadri == q1 else effective_class.volumes.volume_first_quadrimester
        quadri_volume = effective_class.volumes.volume_first_quadrimester \
            if quadri == q1 else effective_class.volumes.volume_second_quadrimester

        if other_quadri_partial_volume and other_quadri_partial_volume > 0:
            warnings.append(
                _('The %(effective_class_complete_acronym)s volumes are inconsistent(only the %(quadrimester)s '
                  'volume has to be completed)') % {
                    'effective_class_complete_acronym': effective_class.complete_acronym,
                    'quadrimester': quadri
                }
            )
        elif not quadri_volume or quadri_volume < 0:
            warnings.append(
                _('The %(effective_class_complete_acronym)s volumes are inconsistent(the %(quadrimester)s '
                  'volume has to be completed)') % {
                    'effective_class_complete_acronym': effective_class.complete_acronym,
                    'quadrimester': quadri
                }
            )
    return warnings
