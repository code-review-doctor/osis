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

from ddd.logic.encodage_des_notes.shared_kernel.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import InscriptionExamenDTO, DesinscriptionExamenDTO, DateDTO


class InscriptionExamenTranslatorInMemory(IInscriptionExamenTranslator):

    inscrits = {
        InscriptionExamenDTO(
            annee=2020,
            noma='11111111',
            code_unite_enseignement='LDROI1001',
            nom_cohorte='DROI1BA',
            date_inscription=DateDTO(
                jour=1,
                mois=1,
                annee=2020,
            ),
        ),
        InscriptionExamenDTO(
            annee=2020,
            noma='99999999',
            code_unite_enseignement='LDROI1001',
            nom_cohorte='DROI1BA',
            date_inscription=DateDTO(
                jour=1,
                mois=1,
                annee=2020,
            ),
        ),
    }

    desinscrits = {
        DesinscriptionExamenDTO(
            annee=2020,
            noma='22222222',
            code_unite_enseignement='LDROI1001',
            nom_cohorte='DROI1BA',
        ),
    }

    @classmethod
    def search_desinscrits(
            cls,
            code_unite_enseignement: str,
            numero_session: int,
            annee: int
    ) -> Set['DesinscriptionExamenDTO']:
        return set(
            filter(
                lambda dto: _filter(dto, code_unite_enseignement, annee),
                cls.desinscrits,
            )
        )

    @classmethod
    def search_inscrits(
            cls,
            code_unite_enseignement: str,
            numero_session: int,
            annee: int,
    ) -> Set['InscriptionExamenDTO']:
        return set(
            filter(
                lambda dto: _filter(dto, code_unite_enseignement, annee),
                cls.inscrits,
            )
        )


def _filter(dto, code_unite_enseignement, annee):
    return dto.code_unite_enseignement == code_unite_enseignement \
           and dto.annee == annee
