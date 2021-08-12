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
from typing import Set

from ddd.logic.encodage_des_notes.soumission.domain.service.i_deliberation import IDeliberationTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import DeliberationDTO, DateDTO


class DeliberationTranslatorInMemory(IDeliberationTranslator):

    deliberations = {
        DeliberationDTO(
            annee=2020,
            session=2,
            nom_cohorte='DROI1BA',
            date=DateDTO(
                jour=15,
                mois=6,
                annee=2020,
            ),
        ),
    }

    @classmethod
    def search(
            cls,
            annee: int,
            session: int,
            noms_cohortes: Set[str],
    ) -> Set['DeliberationDTO']:
        return set(
            filter(
                lambda dto: _filter(dto, annee, session, noms_cohortes),
                cls.deliberations,
            )
        )


def _filter(dto, annee: int, session: int, noms_cohortes: Set[str]):
    return dto.nom_cohorte in noms_cohortes and dto.annee == annee and dto.session == session

