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
from typing import List, Dict, Iterable, Any, Callable, Tuple, Optional, Set

import attr
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext_lazy

from base.models.person import Person
from base.utils.send_mail import _get_txt_complementary_first_col_header
from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.cohorte_non_complete import CodeUniteEnseignement, NomCohorte
from ddd.logic.encodage_des_notes.encodage.domain.service.i_notifier_encodage_notes import INotifierEncodageNotes
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DetailContactDTO
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO, DesinscriptionExamenDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from osis_common.messaging import message_config, send_message

ENCODAGE_COMPLET_MAIL_TEMPLATE = "assessments_all_scores_by_pgm_manager"
CORRECTION_ENCODAGE_COMPLET_MAIL_TEMPLATE = "assessments_correction_encodage_complet"
DEFAULT_LANGUAGE = settings.LANGUAGE_CODE_FR


@attr.s(frozen=True, slots=True)
class DonneesEmail:
    code_unite_enseignement = attr.ib(type=str)
    nom_cohorte = attr.ib(type=str)
    encodage_complet_avant_encodage = attr.ib(type=bool)
    encodage_complet_apres_encodage = attr.ib(type=bool)
    identites_notes_encodees = attr.ib(type=List['IdentiteNoteEtudiant'])
    notes = attr.ib(type=List['NoteEtudiant'])
    emails_destinataires = attr.ib(type=List[str])
    email_gestionnaire = attr.ib(type=str)
    adresse_feuille_de_notes = attr.ib(type=Optional['AdresseFeuilleDeNotes'])
    langue_email = attr.ib(type=str)
    signaletiques_etudiant_par_noma = attr.ib(type=Dict[str, SignaletiqueEtudiantDTO])


class NotifierEncodageNotes(INotifierEncodageNotes):

    @classmethod
    def notifier(
            cls,
            identites_notes_encodees: List['IdentiteNoteEtudiant'],
            cohortes_non_entierement_encodees_avant_encodage: List[Tuple[CodeUniteEnseignement, NomCohorte]],
            gestionnaire_parcours: 'GestionnaireParcours',
            note_etudiant_repository: 'INoteEtudiantRepository',
            attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
            inscr_exam_translator: 'IInscriptionExamenTranslator',
    ) -> None:
        liste_donnees_email = cls._get_donnees_email(
            identites_notes_encodees,
            cohortes_non_entierement_encodees_avant_encodage,
            gestionnaire_parcours,
            note_etudiant_repository,
            attribution_enseignant_translator,
            signaletique_personne_translator,
            signaletique_etudiant_translator,
            adresse_feuille_de_notes_repo,
            inscr_exam_translator,
        )
        for donnees_email in liste_donnees_email:
            if not donnees_email.encodage_complet_avant_encodage and donnees_email.encodage_complet_apres_encodage:
                cls._envoyer_mail_encodage_complet(donnees_email)
            elif donnees_email.encodage_complet_avant_encodage and donnees_email.encodage_complet_apres_encodage:
                cls._envoyer_mail_correction_encodage_complet(donnees_email)

    @classmethod
    def _envoyer_mail_correction_encodage_complet(cls, donnees_email: 'DonneesEmail') -> None:
        html_template_ref = '{}_html'.format(CORRECTION_ENCODAGE_COMPLET_MAIL_TEMPLATE)
        txt_template_ref = '{}_txt'.format(CORRECTION_ENCODAGE_COMPLET_MAIL_TEMPLATE)
        subject_data = {
            'unite_enseignement': donnees_email.code_unite_enseignement,
            'cohorte': donnees_email.nom_cohorte
        }
        template_base_data = {
            'unite_enseignement': donnees_email.code_unite_enseignement,
            'cohorte': donnees_email.nom_cohorte
        }

        rows = cls._format_lignes_table(donnees_email.notes, donnees_email.signaletiques_etudiant_par_noma)
        row_styles = [
            cls._get_row_style(
                row,
                donnees_email.code_unite_enseignement,
                donnees_email.identites_notes_encodees,
                donnees_email.encodage_complet_avant_encodage
            ) for row in rows
        ]
        txt_complementary_rows_content = ["*" if row_style else "" for row_style in row_styles]
        table = message_config.create_table(
            'enrollments',
            cls._get_table_headers(donnees_email.langue_email),
            {
                "style": row_styles,
                "data": rows,
                "txt_complementary_first_col": {
                    "header": _get_txt_complementary_first_col_header(donnees_email.langue_email),
                    "rows_content": txt_complementary_rows_content
                }
            },
        )

        message_content = message_config.create_message_content(
            html_template_ref,
            txt_template_ref,
            tables=[table],
            receivers=cls._get_destinataires_email(donnees_email),
            template_base_data=template_base_data,
            subject_data=subject_data,
            attachment=None,
            cc=cls._get_destinataires_cc_email(donnees_email),

        )
        send_message.send_messages(message_content)

    @classmethod
    def _envoyer_mail_encodage_complet(
            cls,
            donnes_email: 'DonneesEmail'
    ) -> None:
        html_template_ref = '{}_html'.format(ENCODAGE_COMPLET_MAIL_TEMPLATE)
        txt_template_ref = '{}_txt'.format(ENCODAGE_COMPLET_MAIL_TEMPLATE)
        subject_data = {
            'learning_unit_acronym': donnes_email.code_unite_enseignement,
            'offer_acronym': donnes_email.nom_cohorte
        }
        template_base_data = {
            'learning_unit_acronym': donnes_email.code_unite_enseignement,
            'offer_acronym': donnes_email.nom_cohorte
        }

        rows = cls._format_lignes_table(donnes_email.notes, donnes_email.signaletiques_etudiant_par_noma)
        row_styles = ['' for row in rows]
        txt_complementary_rows_content = ["" for row_style in row_styles]
        table = message_config.create_table(
            'enrollments',
            cls._get_table_headers(donnes_email.langue_email),
            {
                "style": row_styles,
                "data": rows,
                "txt_complementary_first_col": {
                    "header": _get_txt_complementary_first_col_header(donnes_email.langue_email),
                    "rows_content": txt_complementary_rows_content
                }
            },
        )

        message_content = message_config.create_message_content(
            html_template_ref,
            txt_template_ref,
            tables=[table],
            receivers=cls._get_destinataires_email(donnes_email),
            template_base_data=template_base_data,
            subject_data=subject_data,
            attachment=None,
            cc=cls._get_destinataires_cc_email(donnes_email),

        )
        send_message.send_messages(message_content)

    @classmethod
    def _get_destinataires_cc_email(cls, donnes_email):
        cc = [Person(email=donnes_email.email_gestionnaire)]
        if donnes_email.adresse_feuille_de_notes and donnes_email.adresse_feuille_de_notes.email:
            cc.append(Person(email=donnes_email.adresse_feuille_de_notes.email))
        return cc

    @classmethod
    def _get_destinataires_email(cls, donnes_email):
        receivers = [
            message_config.create_receiver(
                cls._get_receiver_id(email),
                email,
                donnes_email.langue_email
            )
            for email in donnes_email.emails_destinataires
        ]
        return receivers

    @classmethod
    def _get_receiver_id(cls, email: str) -> Optional[int]:
        # FIXME :: performances :: 1 hit DB par receiver par cohorte
        person_obj = Person.objects.filter(email=email).only('id').first()
        if person_obj:
            return person_obj.id
        return None

    @classmethod
    def _get_table_headers(cls, lang_code: str):
        with translation.override(lang_code):
            return [
                translation.pgettext('Submission email table header', 'Program'),
                translation.pgettext('Submission email table header', 'Session number'),
                translation.pgettext('Submission email table header', 'Registration number'),
                translation.gettext_lazy('Last name'),
                translation.gettext_lazy('First name'),
                translation.gettext_lazy('Score'),
            ]

    @classmethod
    def _get_row_style(
            cls,
            row: Tuple,
            code_unite_enseignment: str,
            notes_nouvellement_encodees: List['IdentiteNoteEtudiant'],
            encodage_etait_complet: bool

    ) -> str:
        if not encodage_etait_complet:
            return 'background-color: lime;'
        est_une_note_nouvellement_encodee = any(
            note
            for note in notes_nouvellement_encodees
            if (note.code_unite_enseignement, note.noma) == (code_unite_enseignment, row[2])
        )
        return 'background-color: lime;' if est_une_note_nouvellement_encodee else ''

    @classmethod
    def _format_lignes_table(
            cls,
            notes: List[NoteEtudiant],
            signaletiques_etudiant_par_noma: Dict[str, SignaletiqueEtudiantDTO]
    ) -> List[Tuple]:
        result = [
            (
                note.nom_cohorte,
                note.numero_session,
                note.noma,
                signaletiques_etudiant_par_noma[note.noma].nom,
                signaletiques_etudiant_par_noma[note.noma].prenom,
                cls._format_score(str(note.note)),
            )
            for note in notes
        ]
        return sorted(result, key=lambda l: (l[0], l[3], l[4]))

    @classmethod
    def _format_score(cls, score: str) -> str:
        if score == 'T':
            return gettext_lazy("Cheating")
        elif score == 'S':
            return gettext_lazy('Absence unjustified')
        elif score == 'M':
            return gettext_lazy('Absence justified')
        else:
            return score

    @classmethod
    def _get_donnees_email(
            cls,
            identites_notes_encodees: List['IdentiteNoteEtudiant'],
            cohortes_non_entierement_encodees_avant_encodage: List[Tuple[str, str]],
            gestionnaire_parcours: 'GestionnaireParcours',
            note_etudiant_repository: 'INoteEtudiantRepository',
            attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            adresse_feuille_de_notes_repository: 'IAdresseFeuilleDeNotesRepository',
            inscr_exam_translator: 'IInscriptionExamenTranslator',
    ) -> List['DonneesEmail']:
        if not identites_notes_encodees:
            return []

        annee_academique = identites_notes_encodees[0].annee_academique
        numero_session = identites_notes_encodees[0].numero_session
        codes_unite_enseignement = {identite.code_unite_enseignement for identite in identites_notes_encodees}
        notes = note_etudiant_repository.search(
            codes_unite_enseignement=list(codes_unite_enseignement),
            numero_session=numero_session,
            annee_academique=annee_academique
        )

        nomas = [note.noma for note in notes]
        signaletiques_etudiants_par_noma = cls._search_signaletiques_etudiants(nomas, signaletique_etudiant_translator)

        notes_groupees_par_code_unite_enseignement = groupby(
            notes,
            key=lambda note: note.code_unite_enseignement
        )  # type: Dict[str, List[NoteEtudiant]]

        email_gestionnaire = cls._get_email_gestionnaire_de_parcours(
            gestionnaire_parcours,
            signaletique_personne_translator
        )

        etudiants_desinscrits_exams = inscr_exam_translator.search_desinscrits_pour_plusieurs_unites_enseignement(
            codes_unites_enseignement=codes_unite_enseignement,
            numero_session=numero_session,
            annee=annee_academique,
        )

        result = []
        for code_unite_enseignement, notes_pour_meme_unite_enseignement in notes_groupees_par_code_unite_enseignement.\
                items():
            signaletiques_enseignants = cls._search_signaletiques_enseignants_attribuee_unite_enseignement(
                code_unite_enseignement,
                annee_academique,
                attribution_enseignant_translator,
                signaletique_personne_translator
            )
            signaletiques_enseignants_groupes_par_langue = groupby(
                signaletiques_enseignants,
                key=lambda signaletique: signaletique.langue or DEFAULT_LANGUAGE
            )
            notes_groupes_par_cohorte = groupby(
                notes_pour_meme_unite_enseignement,
                key=lambda note: note.nom_cohorte
            )
            for nom_cohorte, notes_pour_meme_cohorte in notes_groupes_par_cohorte.items():
                if not cls._doit_notifier_encodage_pour_la_cohorte(
                        notes_pour_meme_cohorte,
                        identites_notes_encodees,
                        etudiants_desinscrits_exams
                ):
                    continue
                adresse_feuille_de_notes = cls._get_adresse_feuille_de_notes(
                    nom_cohorte,
                    adresse_feuille_de_notes_repository
                )
                for langue, ensemble_de_signaletiques in signaletiques_enseignants_groupes_par_langue.items():
                    email_destinataire = [signaletique.email for signaletique in ensemble_de_signaletiques]
                    encodage_complet_avant = (code_unite_enseignement, nom_cohorte) \
                        not in cohortes_non_entierement_encodees_avant_encodage
                    encodage_complet_apres = cls._est_encodage_complet(
                        etudiants_desinscrits_exams,
                        notes_pour_meme_cohorte,
                    )
                    result.append(
                        DonneesEmail(
                            code_unite_enseignement=code_unite_enseignement,
                            nom_cohorte=nom_cohorte,
                            identites_notes_encodees=identites_notes_encodees,
                            notes=notes_pour_meme_cohorte,
                            emails_destinataires=email_destinataire,
                            langue_email=langue,
                            signaletiques_etudiant_par_noma=signaletiques_etudiants_par_noma,
                            email_gestionnaire=email_gestionnaire,
                            adresse_feuille_de_notes=adresse_feuille_de_notes,
                            encodage_complet_avant_encodage=encodage_complet_avant,
                            encodage_complet_apres_encodage=encodage_complet_apres,
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
    def _search_signaletiques_enseignants_attribuee_unite_enseignement(
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

    @classmethod
    def _get_email_gestionnaire_de_parcours(
            cls,
            gestionnaire_parcours: 'GestionnaireParcours',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
    ) -> str:
        signaletique_gestionnaire = signaletique_personne_translator.search(
            matricules_fgs={gestionnaire_parcours.entity_id.matricule_fgs_gestionnaire}
        ).pop()
        return signaletique_gestionnaire.email

    @classmethod
    def _get_adresse_feuille_de_notes(
            cls,
            nom_cohorte: str,
            adresse_feuille_de_notes_repository: 'IAdresseFeuilleDeNotesRepository'
    ) -> Optional['AdresseFeuilleDeNotes']:
        identite_adresse_feuille_de_notes = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte(nom_cohorte)
        try:
            return adresse_feuille_de_notes_repository.get(identite_adresse_feuille_de_notes)
        except IndexError:
            return None

    @classmethod
    def _doit_notifier_encodage_pour_la_cohorte(
            cls,
            notes_de_la_cohorte: List['NoteEtudiant'],
            identites_notes_encodees: List['IdentiteNoteEtudiant'],
            etudiants_desinscrits: Set['DesinscriptionExamenDTO']
    ) -> bool:
        a_une_note_nouvellement_encodee = any(
            note for note in notes_de_la_cohorte if note.entity_id in identites_notes_encodees
        )
        notes_de_la_cohorte_sont_toutes_encodees = cls._est_encodage_complet(etudiants_desinscrits, notes_de_la_cohorte)
        return a_une_note_nouvellement_encodee and notes_de_la_cohorte_sont_toutes_encodees

    @classmethod
    def _est_encodage_complet(
            cls,
            etudiants_desinscrits: Set['DesinscriptionExamenDTO'],
            notes_de_la_cohorte: List['NoteEtudiant']
    ):
        return all(
            (not note.is_manquant or cls._est_desinscrit(etudiants_desinscrits, note))
            for note in notes_de_la_cohorte
        )

    @classmethod
    def _est_desinscrit(cls, etudiants_desinscrits: Set['DesinscriptionExamenDTO'], note: 'NoteEtudiant') -> bool:
        return any(
            etd for etd in etudiants_desinscrits
            if etd.noma == note.noma and etd.code_unite_enseignement == note.code_unite_enseignement
        )

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
    def generate_attachment(cls):
        return None


def groupby(datas: Iterable[Any], key: Callable) -> Dict:
    result = defaultdict(list)
    for data in datas:
        result[key(data)].append(data)
    return result
