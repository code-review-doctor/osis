# ##############################################################################
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
# ##############################################################################
from ddd.logic.projet_doctoral.builder.proposition_identity_builder import PropositionIdentityBuilder
from ddd.logic.projet_doctoral.commands import IdentifierPromoteurCommand
from ddd.logic.projet_doctoral.domain.model.proposition import PropositionIdentity
from ddd.logic.projet_doctoral.domain.service.i_promoteur import IPromoteurTranslator
from ddd.logic.projet_doctoral.repository.i_proposition import IPropositionRepository


# TODO :: unit tests
def identifier_promoteur(
        cmd: 'IdentifierPromoteurCommand',
        proposition_repository: 'IPropositionRepository',
        promoteur_translator: 'IPromoteurTranslator',
) -> 'PropositionIdentity':
    # GIVEN
    entity_id = PropositionIdentityBuilder.build_from_uuid(cmd.uuid_proposition)
    proposition_candidat = proposition_repository.get(entity_id=entity_id)
    promoteur_id = promoteur_translator.get(cmd.matricule)

    # WHEN
    proposition_candidat.identifier_promoteur(promoteur_id)

    # THEN
    proposition_repository.save(proposition_candidat)

    return proposition_candidat.entity_id
