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
from ddd.logic.shared_kernel.entite.domain.model.entiteucl import IdentiteUCLEntite
from ddd.logic.shared_kernel.entite.dtos import EntiteRepositoryDTO
from osis_common.ddd.interface import EntityIdentityBuilder


class IdentiteEntiteBuilder(EntityIdentityBuilder):

    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'EntityIdentity':
        pass

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'EntiteRepositoryDTO') -> 'IdentiteUCLEntite':
        return IdentiteUCLEntite(sigle=dto_object.sigle)

    @classmethod
    def build_from_sigle(cls, sigle: str) -> 'IdentiteUCLEntite':
        return IdentiteUCLEntite(sigle=sigle)
