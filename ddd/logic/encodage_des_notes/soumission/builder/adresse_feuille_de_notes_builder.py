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
from assessments.models.enums.score_sheet_address_choices import ScoreSheetAddressEntityType
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from osis_common.ddd import interface
from osis_common.ddd.interface import CommandRequest


class AdresseFeuilleDeNotesBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'AdresseFeuilleDeNotes':
        pass

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'AdresseFeuilleDeNotesDTO') -> 'AdresseFeuilleDeNotes':
        return AdresseFeuilleDeNotes(
            entity_id=AdresseFeuilleDeNotesIdentityBuilder().build_from_repository_dto(dto_object),
            type_entite=ScoreSheetAddressEntityType[dto_object.type_entite] if dto_object.type_entite else None,
            destinataire=dto_object.destinataire,
            rue_numero=dto_object.rue_numero,
            code_postal=dto_object.code_postal,
            ville=dto_object.ville,
            pays=dto_object.pays,
            telephone=dto_object.telephone,
            fax=dto_object.fax,
            email=dto_object.email,
        )
