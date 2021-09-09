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
from typing import List, Optional, Dict, Set

from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.encodage.domain.model._note import NOTE_MANQUANTE
from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import Noma
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import NoteEtudiantDTO, DateDTO, PeriodeEncodageNotesDTO
from ddd.logic.encodage_des_notes.soumission.dtos import UniteEnseignementDTO, InscriptionExamenDTO, \
    DesinscriptionExamenDTO, SignaletiqueEtudiantDTO
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
            periode_encodage: 'PeriodeEncodageNotesDTO',

            note_etudiant_repo: 'INoteEtudiantRepository',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
    ) -> List['NoteEtudiantDTO']:
        note_etudiant_filtered = cls._get_notes_etudiants_filtered(
            nom_cohorte=nom_cohorte,
            noma=noma,
            nom=nom,
            prenom=prenom,
            etat=etat,
            gestionnaire_parcours=gestionnaire_parcours,
            periode_encodage=periode_encodage,
            note_etudiant_repo=note_etudiant_repo,
            signaletique_etudiant_translator=signaletique_etudiant_translator,
        )

        codes_unites_enseignement = {note.code_unite_enseignement for note in note_etudiant_filtered}
        inscr_examen_par_noma = _get_inscriptions_examens_par_noma(
            codes_unites_enseignement,
            periode_encodage.annee_concernee,
            periode_encodage.session_concernee,
            inscription_examen_translator
        )
        desinscr_exam_par_noma = _get_desinscriptions_examens_par_noma(
            codes_unites_enseignement,
            periode_encodage.annee_concernee,
            periode_encodage.session_concernee,
            inscription_examen_translator
        )
        unites_enseignements = _get_unites_enseignements_par_code(
            codes_unites_enseignement,
            periode_encodage.annee_concernee,
            unite_enseignement_translator
        )

        nomas_concernes = [note.noma for note in note_etudiant_filtered]
        signaletique_par_noma = _get_signaletique_etudiant_par_noma(nomas_concernes, signaletique_etudiant_translator)

        notes_etudiants_dto = []
        for note_etudiant in note_etudiant_filtered:
            unite_enseignement_dto = unites_enseignements.get(note_etudiant.code_unite_enseignement)
            signaletique_etudiant_dto = signaletique_par_noma.get(note_etudiant.noma)
            desinscriptions_examens_dto = desinscr_exam_par_noma.get(note_etudiant.noma, set())

            inscription_examen_dto = next(
                (inscription for inscription in inscr_examen_par_noma.get(note_etudiant.noma, set())
                 if inscription.code_unite_enseignement == note_etudiant.code_unite_enseignement), None
            )
            ouverture_periode_soumission = periode_encodage.debut_periode_soumission.to_date()
            inscrit_tardivement = inscription_examen_dto and \
                inscription_examen_dto.date_inscription.to_date() > ouverture_periode_soumission

            notes_etudiants_dto.append(
                NoteEtudiantDTO(
                    code_unite_enseignement=getattr(unite_enseignement_dto, 'code', ''),
                    intitule_complet_unite_enseignement=getattr(unite_enseignement_dto, 'intitule_complet', ''),
                    annee_unite_enseignement=getattr(unite_enseignement_dto, 'annee', ''),
                    est_soumise=not note_etudiant.is_manquant,
                    date_remise_de_notes=DateDTO.build_from_date(note_etudiant.echeance_gestionnaire),
                    nom_cohorte=note_etudiant.nom_cohorte,
                    noma=note_etudiant.noma,
                    nom=getattr(signaletique_etudiant_dto, 'nom', ''),
                    prenom=getattr(signaletique_etudiant_dto, 'prenom', ''),
                    peps=getattr(signaletique_etudiant_dto, 'peps', ''),
                    email=note_etudiant.email,
                    note=str(note_etudiant.note),
                    inscrit_tardivement=inscrit_tardivement,
                    desinscrit_tardivement=any(
                        desinscription for desinscription in desinscriptions_examens_dto if
                        desinscription.code_unite_enseignement == note_etudiant.code_unite_enseignement
                    )
                )
            )
        return notes_etudiants_dto

    @classmethod
    def _get_notes_etudiants_filtered(
            cls,
            nom_cohorte: str,
            noma: str,
            nom: str,
            prenom: str,
            etat: str,
            gestionnaire_parcours: 'GestionnaireParcours',
            periode_encodage: 'PeriodeEncodageNotesDTO',
            note_etudiant_repo: 'INoteEtudiantRepository',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
    ):
        noms_cohortes = gestionnaire_parcours.cohortes_gerees
        if nom_cohorte:
            gestionnaire_parcours.verifier_gere_cohorte(nom_cohorte)
            noms_cohortes = [nom_cohorte]

        note_manquante = etat == NOTE_MANQUANTE
        justification = None
        if etat and etat != NOTE_MANQUANTE:
            justification = cls._convert_etat_to_justification_enum(etat)

        nomas_searched = None
        if any([noma, nom, prenom]):
            nomas_searched = [noma] if noma else cls._search_nomas_from_nom_prenom(
                nom,
                prenom,
                signaletique_etudiant_translator
            )

        return note_etudiant_repo.search(
            noms_cohortes=noms_cohortes,
            nomas=nomas_searched,
            annee_academique=periode_encodage.annee_concernee,
            numero_session=periode_encodage.session_concernee,
            note_manquante=note_manquante,
            justification=justification,
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


def _get_signaletique_etudiant_par_noma(
        nomas_concernes: List['Noma'],
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
) -> Dict['Noma', 'SignaletiqueEtudiantDTO']:
    signaletiques_etds = signaletique_etudiant_translator.search(nomas=nomas_concernes)
    return {signal.noma: signal for signal in signaletiques_etds}


def _get_desinscriptions_examens_par_noma(
        codes_unites_enseignement: Set[str],
        annee: int,
        numero_session: int,
        inscription_examen_translator: 'IInscriptionExamenTranslator'
) -> Dict['Noma', List['DesinscriptionExamenDTO']]:
    desinscriptions_examens = inscription_examen_translator.search_desinscrits_pour_plusieurs_unites_enseignement(
        codes_unites_enseignement=codes_unites_enseignement,
        annee=annee,
        numero_session=numero_session,
    )
    desinscriptions_examens_par_noma = dict()
    for desinscr in desinscriptions_examens:
        desinscriptions_examens_par_noma.setdefault(desinscr.noma, set()).add(desinscr)
    return desinscriptions_examens_par_noma


def _get_inscriptions_examens_par_noma(
        codes_unites_enseignement: Set[str],
        annee: int,
        numero_session: int,
        inscription_examen_translator: 'IInscriptionExamenTranslator'
) -> Dict['Noma', List['InscriptionExamenDTO']]:
    inscr_examens = inscription_examen_translator.search_inscrits_pour_plusieurs_unites_enseignement(
        codes_unites_enseignement=codes_unites_enseignement,
        annee=annee,
        numero_session=numero_session,
    )
    inscriptions_examens_par_noma = dict()
    for inscr in inscr_examens:
        inscriptions_examens_par_noma.setdefault(inscr.noma, set()).add(inscr)
    return inscriptions_examens_par_noma


def _get_unites_enseignements_par_code(
        codes_unites_enseignement: Set[str],
        annee: int,
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
) -> Dict[str, 'UniteEnseignementDTO']:
    unites_enseignements = unite_enseignement_translator.search(
        {(code_unite_enseignement, annee,) for code_unite_enseignement in codes_unites_enseignement}
    )
    return {unite_enseignement.code: unite_enseignement for unite_enseignement in unites_enseignements}
