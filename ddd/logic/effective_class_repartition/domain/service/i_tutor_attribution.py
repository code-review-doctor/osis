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
import abc
from typing import List

from ddd.logic.effective_class_repartition.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from osis_common.ddd import interface


class ITutorAttributionToLearningUnitTranslator(interface.DomainService):
    @classmethod
    @abc.abstractmethod
    def search_attributions_to_learning_unit(
            cls,
            learning_unit_identity: 'LearningUnitIdentity',
    ) -> List['TutorAttributionToLearningUnitDTO']:
        pass

    @classmethod
    @abc.abstractmethod
    def get_learning_unit_attribution(cls, attribution_uuid: str) -> 'TutorAttributionToLearningUnitDTO':
        pass

    @classmethod
    @abc.abstractmethod
    def search_learning_unit_attributions(
            cls,
            attribution_uuids: List[str]
    ) -> List['TutorAttributionToLearningUnitDTO']:
        pass

    @classmethod
    @abc.abstractmethod
    def search_par_nom_prenom_enseignant(
            cls,
            annee: int,
            nom_prenom: str,
    ) -> List['TutorAttributionToLearningUnitDTO']:
        pass

    @classmethod
    @abc.abstractmethod
    def get_by_enseignant(cls, matricule_fgs_enseignant: str, annee: int) -> List['TutorAttributionToLearningUnitDTO']:
        pass
