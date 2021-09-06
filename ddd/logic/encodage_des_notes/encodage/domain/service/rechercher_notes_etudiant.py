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
from typing import List, Optional

from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.encodage.domain.model._note import NOTE_MANQUANTE
from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import NoteEtudiantDTO
from osis_common.ddd import interface


class RechercheNotesEtudiant(interface.DomainService):

    @classmethod
    def search(
            cls,
            nom_cohorte: str,
            noma: str,
            nom: str,
            prenom: str,
            etat: str,
            gestionnaire_parcours: 'GestionnaireParcours',
            note_etudiant_repo: 'INoteEtudiantRepository',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
    ) -> List['NoteEtudiantDTO']:
        noms_cohortes = gestionnaire_parcours.cohortes_gerees
        if nom_cohorte:
            gestionnaire_parcours.verifier_gere_cohorte(nom_cohorte)
            noms_cohortes = [nom_cohorte]

        note_manquante = etat == NOTE_MANQUANTE
        justification = None
        if etat and etat != NOTE_MANQUANTE:
            justification = cls._convert_etat_to_justification_enum(etat)

        return [
            cls._convert_note_etudiant_to_dto(note_etudiant)
            for note_etudiant
            in note_etudiant_repo.search(
                noms_cohortes=noms_cohortes,
                nomas=[noma] if noma else cls._search_nomas_from_nom_prenom(
                    nom,
                    prenom,
                    signaletique_etudiant_translator
                ),
                note_manquante=note_manquante,
                justification=justification,
            )
        ]

    @classmethod
    def _convert_note_etudiant_to_dto(cls, note_etudiant: 'NoteEtudiant') -> 'NoteEtudiantDTO':
        return NoteEtudiantDTO(
            est_soumise=None,
            date_remise_de_notes=note_etudiant.echeance_gestionnaire,
            nom_cohorte=note_etudiant.nom_cohorte,
            noma=note_etudiant.noma,
            nom="",
            prenom="",
            peps=[],
            email=note_etudiant.email,
            note=str(note_etudiant.note.value),
            inscrit_tardivement=None,
            desinscrit_tardivement=None
        )

    @classmethod
    def _convert_etat_to_justification_enum(cls, etat: str) -> Optional[JustificationTypes]:
        return JustificationTypes[etat]

    @classmethod
    def _search_nomas_from_nom_prenom(
            cls,
            nom: str,
            prenom: str,
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
    ) -> List[str]:
        signaletiques_etudiant = signaletique_etudiant_translator.search([], nom=nom, prenom=prenom)
        return [signaletique.noma for signaletique in signaletiques_etudiant]
