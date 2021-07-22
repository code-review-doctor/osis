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
import attr

from ddd.logic.encodage_des_notes.soumission.dtos import UniteEnseignementIdentiteFromRepositoryDTO
from osis_common.ddd import interface


class UniteEnseignementIdentiteBuilder(interface.EntityIdentity):
    @staticmethod
    def build_from_repository_dto(
            dto_object: 'UniteEnseignementIdentiteFromRepositoryDTO'
    ) -> 'UniteEnseignementIdentite':
        return UniteEnseignementIdentite(
            code_unite_enseignement=dto_object.code_unite_enseignement,
            annee_academique=dto_object.annee_academique
        )


@attr.s(frozen=True, slots=True)
class UniteEnseignementIdentite(interface.EntityIdentity):
    """Identifie un cours, stage, mémoire partim, classe..."""
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
