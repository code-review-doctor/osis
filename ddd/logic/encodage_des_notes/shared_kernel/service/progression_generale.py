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
import itertools
from typing import List, Dict, Set, Tuple, Optional

from ddd.logic.encodage_des_notes.shared_kernel.dtos import PeriodeEncodageNotesDTO, DateEcheanceDTO, \
    ProgressionEncodageNotesUniteEnseignementDTO, ProgressionGeneraleEncodageNotesDTO, EnseignantDTO
from ddd.logic.encodage_des_notes.shared_kernel.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.domain.model._unite_enseignement_identite import \
    UniteEnseignementIdentite, UniteEnseignementIdentiteBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant, IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.dtos import UniteEnseignementDTO, ResponsableDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd import interface


class ProgressionGeneral(interface.DomainService):
    @classmethod
    def get(
        cls,
        note_identites: List['IdentiteNoteEtudiant'],
        note_etudiant_soumission_repo: 'INoteEtudiantRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_encodage: 'PeriodeEncodageNotesDTO',
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'ProgressionGeneraleEncodageNotesDTO':
        nomas_concernes = [note.noma for note in note_identites]
        nomas_avec_peps = _get_nomas_avec_peps(nomas_concernes, signaletique_etudiant_translator)

        if note_identites:
            detail_unite_enseignement_par_code = _get_detail_unite_enseignement_par_code(
                {(note.code_unite_enseignement, note.annee_academique) for note in note_identites},
                unite_enseignement_translator,
            )
            identites_unites_enseignements = {
                UniteEnseignementIdentiteBuilder.build_from_code_and_annee(
                    code_unite_enseignement=note.code_unite_enseignement,
                    annee_academique=note.annee_academique,
                ) for note in note_identites
            }
            dates_echeances_par_code_unite_enseigement = _get_dates_echeances_par_unite_enseignement(
                identites_unites_enseignements,
                note_etudiant_soumission_repo
            )
            responsable_notes_par_code = _get_responsable_notes_par_unite_enseignement(
                identites_unites_enseignements,
                responsable_notes_repo,
            )

        progressions = []
        notes_ordonnee_ue = sorted(note_identites, key=lambda note_id: note_id.code_unite_enseignement)
        for code_ue, notes_id_par_ue in itertools.groupby(notes_ordonnee_ue, lambda note: note.code_unite_enseignement):
            progression_par_ue = cls._compute_progression_par_unite_enseignement(
                list(notes_id_par_ue),
                dates_echeances_par_code_unite_enseigement[code_ue],
                nomas_avec_peps,
                detail_unite_enseignement_par_code[code_ue],
                responsable_notes_par_code.get(code_ue)
            )
            progressions.append(progression_par_ue)

        return ProgressionGeneraleEncodageNotesDTO(
            annee_academique=periode_encodage.annee_concernee,
            numero_session=periode_encodage.session_concernee,
            progression_generale=progressions,
        )

    @classmethod
    def _compute_progression_par_unite_enseignement(
            cls,
            notes_identites: List[IdentiteNoteEtudiant],
            dates_echeances: List[DateEcheanceDTO],
            nomas_avec_peps: Set[str],
            detail_unite_enseignement: UniteEnseignementDTO,
            responsable_notes: Optional[ResponsableDeNotesDTO]
    ):
        # dates_echeance = []
        # notes_ordonnee_date_remise = sorted(notes, key=lambda note: note.date_limite_de_remise)
        # for date_limite_de_remise, notes_grouped in itertools.groupby(
        #         notes_ordonnee_date_remise, lambda note: note.date_limite_de_remise
        # ):
        #     notes_grouped = list(notes_grouped)
        #     dates_echeance.append(
        #         DateEcheanceDTO(
        #             jour=date_limite_de_remise.jour,
        #             mois=date_limite_de_remise.mois,
        #             annee=date_limite_de_remise.annee,
        #             quantite_notes_soumises=sum(1 for n in notes_grouped if n.est_soumise),
        #             quantite_total_notes=len(notes_grouped),
        #         )
        #     )

        return ProgressionEncodageNotesUniteEnseignementDTO(
            code_unite_enseignement=detail_unite_enseignement.code,
            intitule_complet_unite_enseignement=detail_unite_enseignement.intitule_complet,
            dates_echeance=dates_echeances,
            a_etudiants_peps=any(note.noma in nomas_avec_peps for note in notes_identites),
            responsable_note=EnseignantDTO(
                nom=responsable_notes.nom,
                prenom=responsable_notes.prenom,
            ) if responsable_notes else EnseignantDTO(nom='', prenom='')
        )


def _get_nomas_avec_peps(
    nomas_concernes: List[str],
    signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
) -> Set[str]:
    signaletiques_etds = signaletique_etudiant_translator.search(nomas=nomas_concernes)
    return {signal.noma for signal in signaletiques_etds if bool(signal.peps)}


def _get_detail_unite_enseignement_par_code(
    code_annee_valeurs: Set[Tuple[str, int]],
    unite_enseignement_translator: 'IUniteEnseignementTranslator',
) -> Dict[str, UniteEnseignementDTO]:
    unites_enseignement = unite_enseignement_translator.search(code_annee_valeurs)
    return {ue.code: ue for ue in unites_enseignement}


def _get_responsable_notes_par_unite_enseignement(
    unite_enseignement_identities: Set[UniteEnseignementIdentite],
    responsable_notes_repo: 'IResponsableDeNotesRepository',
) -> Dict[str, ResponsableDeNotesDTO]:
    responsables_notes = responsable_notes_repo.search_dto(unite_enseignement_identities)
    return {resp.code_unite_enseignement: resp for resp in responsables_notes}


def _get_dates_echeances_par_unite_enseignement(
    unite_enseignement_identities: Set[UniteEnseignementIdentite],
    note_etudiant_soumission_repo: 'INoteEtudiantRepository',
    periode_encodage: 'PeriodeEncodageNotesDTO',
) -> Dict[str, List[DateEcheanceDTO]]:
    dates_echeances_notes = note_etudiant_soumission_repo.search_dates_echeances(
        criterias=[
            (
                unite_enseignement_id.code_unite_enseignement,
                unite_enseignement_id.annee_academique,
                periode_encodage.session_concernee
            ) for unite_enseignement_id in unite_enseignement_identities
        ]
    )

    dates_echeances = []
    dates_echeances_ordonee = sorted(dates_echeances_notes, key=lambda echeance_note: echeance_note.to_date())
    for date_limite_de_remise, notes_grouped in itertools.groupby(
            dates_echeances_ordonee, lambda echeance_note: echeance_note.to_date()
    ):
        notes_grouped = list(notes_grouped)
        dates_echeances.append(
            DateEcheanceDTO(
                jour=date_limite_de_remise.jour,
                mois=date_limite_de_remise.mois,
                annee=date_limite_de_remise.annee,
                quantite_notes_soumises=sum(1 for n in notes_grouped if n.est_soumise),
                quantite_total_notes=len(notes_grouped),
            )
        )
    return dates_echeances
