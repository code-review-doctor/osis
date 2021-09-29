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
from base.models.enums.entity_type import EntityType
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from ddd.logic.shared_kernel.entite.domain.model._adresse_entite import AdresseEntite
from ddd.logic.shared_kernel.entite.domain.model.entiteucl import EntiteUCL
from ddd.logic.shared_kernel.entite.dtos import EntiteRepositoryDTO
from osis_common.ddd.interface import EntityIdentityBuilder


class EntiteBuilder(EntityIdentityBuilder):

    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'EntiteUCL':
        pass

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'EntiteRepositoryDTO') -> 'EntiteUCL':
        builder = IdentiteEntiteBuilder()
        return EntiteUCL(
            entity_id=builder.build_from_repository_dto(dto_object),
            parent=builder.build_from_sigle(dto_object.parent_sigle) if dto_object.parent_sigle else None,
            type=EntityType[dto_object.type] if dto_object.type else None,
            intitule=dto_object.intitule,
            adresse=AdresseEntite(
                rue_numero=dto_object.rue_numero,
                code_postal=dto_object.code_postal,
                ville=dto_object.ville,
                pays=dto_object.pays,
                telephone=dto_object.telephone,
                fax=dto_object.fax
            )
        )
