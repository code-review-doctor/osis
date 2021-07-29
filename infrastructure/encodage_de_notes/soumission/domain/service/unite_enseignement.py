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
from typing import Set, Tuple

from ddd.logic.encodage_des_notes.soumission.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import UniteEnseignementDTO
from ddd.logic.learning_unit.commands import LearningUnitSearchCommand


class UniteEnseignementTranslator(IUniteEnseignementTranslator):

    @classmethod
    def get(
            cls,
            code: str,
            annee: int,
    ) -> 'UniteEnseignementDTO':
        dtos = cls.search({(code, annee)})
        if dtos:
            return list(dtos)[0]

    @classmethod
    def search(
            cls,
            code_annee_values: Set[Tuple[str, int]],
    ) -> Set['UniteEnseignementDTO']:
        from infrastructure.messages_bus import message_bus_instance
        results = message_bus_instance.invoke(LearningUnitSearchCommand(code_annee_values=code_annee_values))
        return {
            UniteEnseignementDTO(
                annee=dto.year,
                code=dto.code,
                intitule_complet=dto.full_title,
            ) for dto in results
        }
