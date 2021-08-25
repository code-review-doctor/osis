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
from ddd.logic.projet_doctoral.builder.proposition_builder import PropositionBuilder
from ddd.logic.projet_doctoral.builder.proposition_identity_builder import PropositionIdentityBuilder
from ddd.logic.projet_doctoral.commands import CompleterPropositionCommand
from ddd.logic.projet_doctoral.domain.model.proposition import PropositionIdentity
from ddd.logic.projet_doctoral.domain.service.bureau_CDE import BureauCDE
from ddd.logic.projet_doctoral.repository.i_proposition import IPropositionRepository


def completer_proposition(
        cmd: 'CompleterPropositionCommand',
        proposition_repository: 'IPropositionRepository',
) -> 'PropositionIdentity':
    # GIVEN
    entity_id = PropositionIdentityBuilder.build_from_uuid(cmd.uuid)
    proposition_candidat = proposition_repository.get(entity_id=entity_id)
    BureauCDE().verifier(proposition_candidat.doctorat_id, cmd.bureau_CDE)

    # WHEN
    proposition = proposition_candidat.completer(
        type_admission=cmd.type_admission,
        bureau_CDE=cmd.bureau_CDE,
        type_financement=cmd.type_financement,
        type_contrat_travail=cmd.type_contrat_travail,
        titre=cmd.titre_projet,
        resume=cmd.resume_projet,
        doctorat_deja_realise=cmd.doctorat_deja_realise,
        institution=cmd.institution,
        documents=cmd.documents_projet,
    )

    # THEN
    proposition_repository.save(proposition)

    return proposition.entity_id
