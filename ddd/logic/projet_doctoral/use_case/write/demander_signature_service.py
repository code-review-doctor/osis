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
from ddd.logic.projet_doctoral.commands import DemanderSignatureCommand
from ddd.logic.projet_doctoral.domain.model.proposition import PropositionIdentity
from ddd.logic.projet_doctoral.domain.service.i_processus_signature import IProcessusSignature
from ddd.logic.projet_doctoral.repository.i_proposition import IPropositionRepository
from ddd.logic.shared_kernel.processus_signature.domain.service.i_signature_email import ISignatureEmail


# TODO :: unit tests
def demander_signature(
        cmd: 'DemanderSignatureCommand',
        proposition_repository: 'IPropositionRepository',
        signature_email: 'ISignatureEmail',
        signature_process_service: 'IProcessusSignature',
        notification_service: 'INotification',
) -> 'PropositionIdentity':
    # GIVEN
    entity_id = PropositionIdentityBuilder.build_from_uuid(cmd.uuid_proposition)
    proposition_candidat = proposition_repository.get(entity_id=entity_id)
    processus_id = signature_process_service.get(cmd.uuid_proposition)
    signature_email.verifier_deja_envoyee(processus_id, cmd.matricule_signataire)

    # WHEN
    proposition_candidat.demander_signature(cmd.matricule_signataire)

    # THEN
    contenu_notification = signature_process_service.build_notification(proposition_candidat, cmd.matricule_signataire)
    notification_service.envoyer(cmd.matricule_signataire, contenu_notification, type=WEB)  # FIXME

    return proposition_candidat.entity_id
