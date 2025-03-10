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
from collections import OrderedDict
from typing import List, Dict, Set, Tuple

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.encodage.builder.identite_note_etudiant_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.encodage.builder.note_etudiant_builder import NoteEtudiantBuilder
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNoteCommand
from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.cohorte_non_complete import CodeUniteEnseignement, NomCohorte
from ddd.logic.encodage_des_notes.encodage.domain.service.i_historiser_notes import IHistoriserEncodageNotesService
from ddd.logic.encodage_des_notes.encodage.domain.service.i_notifier_encodage_notes import INotifierEncodageNotes
from ddd.logic.encodage_des_notes.encodage.domain.validator.exceptions import \
    EncoderNotesEnLotLigneBusinessExceptions, EtudiantNonInscritAExamenException
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.model.encoder_notes_rapport import EncoderNotesRapport
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import PeriodeEncodageNotesDTO
from ddd.logic.encodage_des_notes.shared_kernel.repository.i_encoder_notes_rapport import IEncoderNotesRapportRepository
from ddd.logic.encodage_des_notes.soumission.dtos import DesinscriptionExamenDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from osis_common.ddd import interface

NouvelleNote = str
EmailEtudiant = str


class EncoderNotesEnLot(interface.DomainService):

    @classmethod
    def execute(
            cls,
            notes_encodees: List['EncoderNoteCommand'],
            gestionnaire_parcours: 'GestionnaireParcours',
            note_etudiant_repo: 'INoteEtudiantRepository',
            periode_ouverte: 'PeriodeEncodageNotesDTO',
            historiser_note_service: 'IHistoriserEncodageNotesService',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
            rapport: 'EncoderNotesRapport',
            rapport_repository: 'IEncoderNotesRapportRepository',
            notification_encodage: 'INotifierEncodageNotes',
            cohortes_non_entierement_encodees_avant_encodage: List[Tuple[CodeUniteEnseignement, NomCohorte]],
            attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
    ) -> List['IdentiteNoteEtudiant']:
        note_encodee_cmd_par_identite = _associer_nouvelle_note_a_son_identite(notes_encodees, periode_ouverte)
        anciennes_notes_a_modifier = note_etudiant_repo.search(entity_ids=list(note_encodee_cmd_par_identite.keys()))
        note_etudiant_par_identite = {n.entity_id: n for n in anciennes_notes_a_modifier}
        desinscriptions = inscription_examen_translator.search_desinscrits_pour_plusieurs_unites_enseignement(
            codes_unites_enseignement={n.code_unite_enseignement for n in notes_encodees},
            numero_session=periode_ouverte.session_concernee,
            annee=periode_ouverte.annee_concernee
        )

        exceptions = []
        notes_a_persister = list()
        for identite, note_encodee_cmd in note_encodee_cmd_par_identite.items():
            nouvelle_valeur_note = note_encodee_cmd.note
            email_encode = note_encodee_cmd.email
            ancienne_note_etudiant = note_etudiant_par_identite.get(identite)
            if ancienne_note_etudiant:
                try:
                    gestionnaire_parcours.verifier_gere_cohorte(ancienne_note_etudiant.nom_cohorte)
                    _verifier_etudiant_est_desinscrit(identite, desinscriptions)
                    nouvelle_note = NoteEtudiantBuilder().build_from_ancienne_note(
                        ancienne_note=ancienne_note_etudiant,
                        email_encode=email_encode,
                        nouvelle_note=nouvelle_valeur_note,
                    )
                    if nouvelle_note.note != ancienne_note_etudiant.note:
                        notes_a_persister.append(nouvelle_note)
                except MultipleBusinessExceptions as e:
                    for business_exception in e.exceptions:
                        rapport.add_note_non_enregistree(
                            noma=ancienne_note_etudiant.noma,
                            numero_session=ancienne_note_etudiant.numero_session,
                            code_unite_enseignement=ancienne_note_etudiant.code_unite_enseignement,
                            annee_academique=ancienne_note_etudiant.annee_academique,
                            cause=str(business_exception.message)
                        )
                        exceptions.append(
                            EncoderNotesEnLotLigneBusinessExceptions(note_id=identite, exception=business_exception)
                        )

        for note in notes_a_persister:
            rapport.add_note_enregistree(
                noma=note.noma,
                numero_session=note.numero_session,
                code_unite_enseignement=note.code_unite_enseignement,
                annee_academique=note.annee_academique,
            )
            note_etudiant_repo.save(note)

        if notes_a_persister:
            historiser_note_service.historiser_encodage(
                gestionnaire_parcours.entity_id.matricule_fgs_gestionnaire,
                notes_a_persister,
            )

            notification_encodage.notifier(
                [n.entity_id for n in notes_a_persister],
                cohortes_non_entierement_encodees_avant_encodage,
                gestionnaire_parcours,
                note_etudiant_repo,
                attribution_enseignant_translator,
                signaletique_personne_translator,
                signaletique_etudiant_translator,
                adresse_feuille_de_notes_repo,
                inscription_examen_translator,
            )

        rapport_repository.save(rapport)
        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)

        return [n.entity_id for n in notes_a_persister]


def _associer_nouvelle_note_a_son_identite(
        notes_encodees: List['EncoderNoteCommand'],
        periode_ouverte: 'PeriodeEncodageNotesDTO'
) -> Dict[IdentiteNoteEtudiant, 'EncoderNoteCommand']:
    notes = OrderedDict()
    for note_cmd in notes_encodees:
        identity = NoteEtudiantIdentityBuilder().build(
            note_cmd.noma,
            note_cmd.code_unite_enseignement,
            periode_ouverte.annee_concernee,
            periode_ouverte.session_concernee,
        )
        notes[identity] = note_cmd
    return notes


def _verifier_etudiant_est_desinscrit(
    identite_note_etudiant: IdentiteNoteEtudiant,
    desinscriptions: Set[DesinscriptionExamenDTO]
) -> None:
    if any(desinscription for desinscription in desinscriptions if
           desinscription.noma == identite_note_etudiant.noma and
           desinscription.code_unite_enseignement == identite_note_etudiant.code_unite_enseignement and
           desinscription.annee == identite_note_etudiant.annee_academique):
        raise MultipleBusinessExceptions(exceptions=[EtudiantNonInscritAExamenException()])
