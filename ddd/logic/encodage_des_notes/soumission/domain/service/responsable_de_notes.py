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
from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_identity_builder import \
    ResponsableDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import IdentiteFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PasResponsableDeNotesException
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd import interface


class ResponsableDeNotes(interface.DomainService):

    @classmethod
    def verifier(
            cls,
            matricule_fgs_enseignant: str,
            feuille_de_notes_id: 'IdentiteFeuilleDeNotes',
            responsable_notes_repo: 'IResponsableDeNotesRepository',
    ) -> None:
        resp_notes_identity = ResponsableDeNotesIdentityBuilder.build_from_matricule_fgs(matricule_fgs_enseignant)
        resp_notes = responsable_notes_repo.get(resp_notes_identity)
        if not resp_notes:
            raise PasResponsableDeNotesException(feuille_de_notes_id.code_unite_enseignement)
        est_responsable = resp_notes.is_responsable_unite_enseignement(
            feuille_de_notes_id.code_unite_enseignement,
            feuille_de_notes_id.annee_academique,
        )
        if not est_responsable:
            raise PasResponsableDeNotesException(feuille_de_notes_id.code_unite_enseignement)
