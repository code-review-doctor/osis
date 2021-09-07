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
from collections import defaultdict
from typing import List, Dict, Iterable, Any, Callable, Tuple

import attr

from base.utils import send_mail
from base.utils.send_mail import get_enrollment_headers
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DetailContactDTO
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.service.i_notifier_soumission_notes import INotifierSoumissionNotes
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from osis_common.messaging import message_config, send_message

MAIL_TEMPLATE_NAME = "assessments_scores_submission"


@attr.s(frozen=True, slots=True)
class DonneesEmail:
    code_unite_enseignement = attr.ib(type=str)
    notes_toutes_encodees = attr.ib(type=bool)
    emails_destinataires = attr.ib(type=List[str])
    langue_email = attr.ib(type=str)
    notes = attr.ib(type=List[NoteEtudiant])
    signaletiques_etudiant_par_noma = attr.ib(type=Dict[str, SignaletiqueEtudiantDTO])


class NotifierSoumissionNotes(INotifierSoumissionNotes):

    @classmethod
    def notifier(
            cls,
            identites_notes_soumises: List['IdentiteNoteEtudiant'],
            note_etudiant_repo: 'INoteEtudiantRepository',
            attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
    ) -> None:
        liste_donnees_email = cls._get_donnees_email(
            identites_notes_soumises,
            note_etudiant_repo,
            attribution_enseignant_translator,
            signaletique_personne_translator,
            signaletique_etudiant_translator
        )
        for donnees_email in liste_donnees_email:
            cls._envoyer_mail(donnees_email)

    @classmethod
    def _envoyer_mail(
            cls,
            donnes_email: 'DonneesEmail'
    ) -> None:
        html_template_ref = '{}_html'.format(MAIL_TEMPLATE_NAME)
        txt_template_ref = '{}_txt'.format(MAIL_TEMPLATE_NAME)
        subject_data = {
            'learning_unit_name': donnes_email.code_unite_enseignement
        }
        template_data = {
            'learning_unit_name': donnes_email.code_unite_enseignement,
            'encoding_status': send_mail._get_encoding_status(
                donnes_email.langue_email,
                donnes_email.notes_toutes_encodees
            )
        }
        receivers = [
            message_config.create_receiver(None, email, donnes_email.langue_email)
            for email in donnes_email.emails_destinataires
        ]

        table = message_config.create_table(
            'submitted_enrollments',
            get_enrollment_headers(donnes_email.langue_email),
            cls._format_lignes_table(donnes_email.notes, donnes_email.signaletiques_etudiant_par_noma),
            data_translatable=['Justification'],
        )
        message_content = message_config.create_message_content(
            html_template_ref,
            txt_template_ref,
            [table],
            receivers,
            template_data,
            subject_data,
        )
        send_message.send_messages(message_content)

    @classmethod
    def _format_lignes_table(
            cls,
            notes: List[NoteEtudiant],
            signaletiques_etudiant_par_noma: Dict[str, SignaletiqueEtudiantDTO]
    ) -> List[Tuple]:
        result = []
        for note in notes:
            ligne = (
                note.nom_cohorte,
                note.numero_session,
                note.noma,
                signaletiques_etudiant_par_noma[note.noma].nom,
                signaletiques_etudiant_par_noma[note.noma].prenom,
                str(note.note) if note.is_chiffree else "",
                str(note.note) if note.is_justification else ""
            )
            result.append(ligne)
        return result

    @classmethod
    def _get_donnees_email(
            cls,
            identites_notes_soumises: List['IdentiteNoteEtudiant'],
            note_etudiant_repo: 'INoteEtudiantRepository',
            attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
    ) -> List['DonneesEmail']:
        code_unite_enseignement = identites_notes_soumises[0].code_unite_enseignement
        annee_academique = identites_notes_soumises[0].annee_academique
        numero_session = identites_notes_soumises[0].numero_session
        notes_unites_enseignements = note_etudiant_repo.search(
            code_unite_enseignement=code_unite_enseignement,
            numero_session=numero_session,
            annee_academique=annee_academique
        )
        notes_toutes_soumises = all(note.est_soumise for note in notes_unites_enseignements)
        notes_nouvellement_soumises = [note for note in notes_unites_enseignements if
                                       note.entity_id in identites_notes_soumises]

        nomas_des_notes_nouvellement_soumises = [note.noma for note in identites_notes_soumises]
        signaletiques_par_noma = cls._search_signaletiques_etudiants(
            nomas_des_notes_nouvellement_soumises,
            signaletique_etudiant_translator
        )

        signaletiques_enseignants = cls._search_signaletiques_enseignants_attribues_a_unite_enseignement(
            code_unite_enseignement=code_unite_enseignement,
            annee_academique=annee_academique,
            attribution_enseignant_translator=attribution_enseignant_translator,
            signaletique_personne_translator=signaletique_personne_translator
        )
        signaletiques_enseignants_groupees_par_langue = groupby(
            signaletiques_enseignants,
            key=lambda signaletique: signaletique.langue
        )

        result = []
        for langue, ensemble_de_signaletiques in signaletiques_enseignants_groupees_par_langue.items():
            emails_destinataire = [signaletique.email for signaletique in ensemble_de_signaletiques]
            result.append(
                DonneesEmail(
                    code_unite_enseignement=code_unite_enseignement,
                    notes_toutes_encodees=notes_toutes_soumises,
                    emails_destinataires=emails_destinataire,
                    langue_email=langue,
                    notes=notes_nouvellement_soumises,
                    signaletiques_etudiant_par_noma=signaletiques_par_noma
                )
            )
        return result

    @classmethod
    def _search_signaletiques_etudiants(
            cls,
            nomas: List[str],
            signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator',
    ) -> Dict[str, 'SignaletiqueEtudiantDTO']:
        signaletiques = signaletique_etudiant_repo.search(nomas=nomas)
        return {signaletique.noma: signaletique for signaletique in signaletiques}

    @classmethod
    def _search_signaletiques_enseignants_attribues_a_unite_enseignement(
            cls,
            code_unite_enseignement: str,
            annee_academique: int,
            attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
    ) -> Iterable['DetailContactDTO']:
        enseignants = attribution_enseignant_translator.search_attributions_enseignant(
            code_unite_enseignement,
            annee_academique
        )
        signaletiques = signaletique_personne_translator.search(
            matricules_fgs={enseignant.matricule_fgs_enseignant for enseignant in enseignants}
        )
        return signaletiques


def groupby(datas: Iterable[Any], key: Callable) -> Dict:
    result = defaultdict(list)
    for data in datas:
        result[key(data)].append(data)
    return result
