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
from typing import List, Dict, Iterable, Any, Callable

import attr

from base.utils import send_mail
from base.utils.send_mail import get_enrollment_headers
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.service.i_notifier_notes import INotifierSoumissionNotes
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from osis_common.messaging import message_config, send_message

MAIL_TEMPLATE_NAME = "assessments_scores_submission"


@attr.s(frozen=True, slots=True)
class EmailData:
    subject_data = attr.ib(type=Dict)
    template_base_data = attr.ib(type=Dict)
    html_template_ref = attr.ib(type=str)
    txt_template_ref = attr.ib(type=str)
    receivers = attr.ib(type=List)
    table = attr.ib(type=Any)


class NotifierSoumissionNotes(INotifierSoumissionNotes):

    @classmethod
    def notifier(
            cls,
            notes_encodees: List['IdentiteNoteEtudiant'],
            note_etudiant_repo: 'INoteEtudiantRepository',
            translator: 'IAttributionEnseignantTranslator',
            signaletique_repo: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator',
    ) -> None:
        mail_datas = cls.generer_mail(
            notes_encodees,
            note_etudiant_repo,
            translator,
            signaletique_repo,
            signaletique_etudiant_repo,
        )
        for data in mail_datas:
            message_content = message_config.create_message_content(
                data.html_template_ref,
                data.txt_template_ref,
                [data.table],
                data.receivers,
                data.template_base_data,
                data.subject_data,
                None,
            )
            send_message.send_messages(message_content)

    @classmethod
    def generer_mail(
            cls,
            notes_encodees: List['IdentiteNoteEtudiant'],
            note_etudiant_repo: 'INoteEtudiantRepository',
            translator: 'IAttributionEnseignantTranslator',
            signaletique_repo: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator',
    ) -> List['EmailData']:
        notes = note_etudiant_repo.search(entity_ids=notes_encodees)
        all_learning_unit_notes = note_etudiant_repo.search(
            codes_unite_enseignement=notes[0].code_unite_enseignement,
            numero_session=notes[0].numero_session,
            annee_academique=notes[0].annee
        )
        notes_toutes_soumises = all(note.est_soumise for note in all_learning_unit_notes)
        result = []

        receivers = cls.get_receivers(
            code_unite_enseignement=notes[0].code_unite_enseignement,
            annee_academique=notes[0].annee,
            translator=translator,
            signaletique_repo=signaletique_repo
        )
        for lang, receivers in groupby(receivers, key=lambda receiver: receiver["receiver_lang"]).items():
            email_data = EmailData(
                subject_data={
                    'learning_unit_name': notes[0].code_unite_enseignement
                },
                template_base_data={
                    'learning_unit_name': notes[0].code_unite_enseignement,
                    'encoding_status': send_mail._get_encoding_status(lang, notes_toutes_soumises)
                },
                html_template_ref=cls.get_html_template_ref(),
                txt_template_ref=cls.get_txt_template_ref(),
                receivers=receivers,
                table=cls.get_table(lang, notes, signaletique_etudiant_repo)
            )
            result.append(email_data)
        return result

    @classmethod
    def get_table(
            cls,
            receiver_lang: str,
            notes_groupees: List[NoteEtudiant],
            signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator'
    ):
        return message_config.create_table(
            'submitted_enrollments',
            get_enrollment_headers(receiver_lang),
            cls.get_table_rows(notes_groupees, signaletique_etudiant_repo),
            data_translatable=['Justification'],
        )

    @classmethod
    def get_table_rows(
            cls,
            notes_groupees: List[NoteEtudiant],
            signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator'
    ) -> List:
        signaletiques = cls.get_signaletique_etudiant(notes_groupees, signaletique_etudiant_repo)
        return [
            (note.nom_cohorte, note.numero_session, note.noma, signaletiques[note.noma].nom,
             signaletiques[note.noma].prenom,
             str(note.note) if note.is_chiffree else "", str(note.note) if note.is_justification else "")
            for note in notes_groupees
        ]

    @classmethod
    def get_signaletique_etudiant(cls, notes_groupes: List[NoteEtudiant], repo: 'ISignaletiqueEtudiantTranslator'):
        nomas = [note.noma for note in notes_groupes]
        signaletiques = repo.search(nomas=nomas)
        return {signaletique.noma: signaletique for signaletique in signaletiques}

    @classmethod
    def get_receivers(
            cls,
            code_unite_enseignement: str,
            annee_academique: int,
            translator: 'IAttributionEnseignantTranslator',
            signaletique_repo: 'ISignaletiquePersonneTranslator',
    ) -> List[Dict]:
        enseignants = translator.search_attributions_enseignant(code_unite_enseignement, annee_academique)
        signaletiques = signaletique_repo.search(
            matricules_fgs={enseignant.matricule_fgs_enseignant for enseignant in enseignants}
        )
        return [
            message_config.create_receiver(None, signaletique.email, signaletique.langue)
            for signaletique in signaletiques
        ]

    @classmethod
    def get_html_template_ref(cls) -> str:
        return '{}_html'.format(MAIL_TEMPLATE_NAME)

    @classmethod
    def get_txt_template_ref(cls) -> str:
        return '{}_txt'.format(MAIL_TEMPLATE_NAME)

    @classmethod
    def generate_attachment(cls):
        return None


def groupby(datas: Iterable[Any], key: Callable) -> Dict:
    result = defaultdict(list)
    for data in datas:
        result[key(data)].append(data)
    return result
