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
from ddd.logic.projet_doctoral.builder.proposition_builder import PropositionBuilder
from ddd.logic.projet_doctoral.commands import InitierPropositionCommand
from ddd.logic.projet_doctoral.domain.model.proposition import PropositionIdentity
from ddd.logic.projet_doctoral.domain.service.initier_proposition import InitierProposition
from ddd.logic.projet_doctoral.repository.i_proposition import IPropositionRepository


def initier_proposition(
        cmd: 'InitierPropositionCommand',
        proposition_repository: 'IPropositionRepository',
) -> 'PropositionIdentity':
    # GIVEN
    propositions_candidat = proposition_repository.search(matricule_candidat=cmd.matricule_candidat)
    InitierProposition().verifier_maximum_propositions_autorisees(propositions_candidat)

    # WHEN
    proposition = PropositionBuilder().initier_proposition(cmd)

    # THEN
    proposition_repository.save(proposition)

    return proposition.entity_id
