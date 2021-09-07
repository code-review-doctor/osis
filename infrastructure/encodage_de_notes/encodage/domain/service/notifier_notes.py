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

from base.models.person import Person
from base.utils.send_mail import get_enrollment_headers, _get_txt_complementary_first_col_header
from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.i_notifier_notes import INotifierNotes
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from osis_common.messaging import message_config, send_message

ASSESSMENTS_ALL_SCORES_BY_PGM_MANAGER = "assessments_all_scores_by_pgm_manager"


@attr.s(frozen=True, slots=True)
class EmailData:
    subject_data = attr.ib(type=Dict)
    template_base_data = attr.ib(type=Dict)
    html_template_ref = attr.ib(type=str)
    txt_template_ref = attr.ib(type=str)
    receivers = attr.ib(type=List)
    cc = attr.ib(type=List[Person])
    table = attr.ib(type=Any)


class NotifierNotes(INotifierNotes):

    @classmethod
    def notifier(
            cls,
            notes_encodees: List['IdentiteNoteEtudiant'],
            gestionnaire_parcours: 'GestionnaireParcours',
            note_etudiant_repo: 'INoteEtudiantRepository',
            translator: 'IAttributionEnseignantTranslator',
            signaletique_repo: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator',
            adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
    ) -> None:
        mail_datas = cls.generer_mail(
            notes_encodees,
            gestionnaire_parcours,
            note_etudiant_repo,
            translator,
            signaletique_repo,
            signaletique_etudiant_repo,
            adresse_feuille_de_notes_repo,
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
                cc=data.cc,
            )
            send_message.send_messages(message_content)

    @classmethod
    def generer_mail(
            cls,
            notes_encodees: List['IdentiteNoteEtudiant'],
            gestionnaire_parcours: 'GestionnaireParcours',
            note_etudiant_repo: 'INoteEtudiantRepository',
            translator: 'IAttributionEnseignantTranslator',
            signaletique_repo: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator',
            adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
    ) -> List['EmailData']:
        codes_unite_enseignement = {notes_encodee.code_unite_enseignement for notes_encodee in notes_encodees}
        notes = note_etudiant_repo.search(
            codes_unite_enseignement=list(codes_unite_enseignement),
            numero_session=notes_encodees[0].numero_session,
            annee_academique=notes_encodees[0].annee_academique
        )
        notes_groupees_par_code_unite_enseignement_et_cohorte = groupby(
            notes,
            key=lambda note: (note.code_unite_enseignement, note.nom_cohorte)
        )  # type: Dict[Tuple, List[NoteEtudiant]]
        result = list()
        for key, notes_groupees in notes_groupees_par_code_unite_enseignement_et_cohorte.items():
            if cls.a_une_note_encodee(notes_groupees, notes_encodees):
                receivers = cls.get_receivers(
                    code_unite_enseignement=notes_groupees[0].code_unite_enseignement,
                    annee_academique=notes_groupees[0].annee_academique,
                    translator=translator,
                    signaletique_repo=signaletique_repo
                )
                for lang, receivers in groupby(receivers, key=lambda receiver: receiver["receiver_lang"]).items():
                    email_data = EmailData(
                        subject_data={
                            'learning_unit_acronym': key[0],
                            'offer_acronym': key[1]
                        },
                        template_base_data={
                            'learning_unit_acronym': key[0],
                            'offer_acronym': key[1]
                        },
                        html_template_ref=cls.get_html_template_ref(),
                        txt_template_ref=cls.get_txt_template_ref(),
                        receivers=receivers,
                        cc=cls.get_cc(
                            gestionnaire_parcours,
                            key[1],
                            signaletique_repo,
                            adresse_feuille_de_notes_repo
                        ),
                        table=cls.get_table(lang, notes_groupees, signaletique_etudiant_repo)
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
            'enrollments',
            get_enrollment_headers(receiver_lang),
            {
                "style": [],
                "data": cls.get_table_rows(notes_groupees, signaletique_etudiant_repo),
                "txt_complementary_first_col": {
                    "header": _get_txt_complementary_first_col_header(receiver_lang),
                    "rows_content": []
                }
            },
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
    def get_cc(
            cls,
            gestionnaire_parcours: 'GestionnaireParcours',
            nom_cohorte: str,
            signaletique_repo: 'ISignaletiquePersonneTranslator',
            adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
    ) -> List['Person']:
        signaletique_gestionnaire = signaletique_repo.search(
            matricules_fgs={gestionnaire_parcours.entity_id.matricule_fgs_gestionnaire}
        ).pop()
        result = [Person(email=signaletique_gestionnaire.email)]

        identite_adresse = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte(nom_cohorte)
        try:
            adresse = adresse_feuille_de_notes_repo.get(identite_adresse)
        except IndexError:
            adresse = None
        if adresse:
            result.append(Person(email=adresse.email))
        return result

    @classmethod
    def a_une_note_encodee(
            cls,
            notes_groupees: List['NoteEtudiant'],
            notes_encodees: List['IdentiteNoteEtudiant']
    ) -> bool:
        return any(
            note for note in notes_groupees if note.entity_id in notes_encodees
        )

    @classmethod
    def get_html_template_ref(cls) -> str:
        return '{}_html'.format(ASSESSMENTS_ALL_SCORES_BY_PGM_MANAGER)

    @classmethod
    def get_txt_template_ref(cls) -> str:
        return '{}_txt'.format(ASSESSMENTS_ALL_SCORES_BY_PGM_MANAGER)

    @classmethod
    def generate_attachment(cls):
        return None


def groupby(datas: Iterable[Any], key: Callable) -> Dict:
    result = defaultdict(list)
    for data in datas:
        result[key(data)].append(data)
    return result
