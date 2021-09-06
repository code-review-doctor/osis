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
from typing import List, Dict, Optional

from ddd.logic.encodage_des_notes.shared_kernel.dtos import FeuilleDeNotesDTO, NoteEtudiantDTO, EnseignantDTO, \
    PeriodeEncodageNotesDTO
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import Noma, NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO, InscriptionExamenDTO, \
    DesinscriptionExamenDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd import interface


class FeuilleDeNotesParUniteEnseignement(interface.DomainService):  # TODO :: déplacer dans domain common

    @staticmethod
    def get(
            notes: List['NoteEtudiant'],
            responsable_notes_repo: 'IResponsableDeNotesRepository',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            periode_encodage: 'PeriodeEncodageNotesDTO',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            attribution_translator: 'IAttributionEnseignantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'FeuilleDeNotesDTO':
        code_unite_enseignement = notes[0].code_unite_enseignement
        annee = periode_encodage.annee_concernee
        numero_session = periode_encodage.session_concernee

        unite_enseignement = unite_enseignement_translator.get(code_unite_enseignement, annee)
        resp_notes = responsable_notes_repo.get_for_unite_enseignement(code_unite_enseignement, annee)
        responsable_notes_dto = None
        if resp_notes:
            responsable_notes_dto = responsable_notes_repo.get_detail_enseignant(resp_notes.entity_id)

        autres_enseignants = _get_autres_enseignants(
            attribution_translator,
            code_unite_enseignement,
            annee,
            responsable_notes_dto
        )

        nomas_concernes = [note.noma for note in notes]

        inscr_examen_par_noma = _get_inscriptions_examens_par_noma(
            code_unite_enseignement,
            annee,
            numero_session,
            inscription_examen_translator
        )
        desinscr_exam_par_noma = _get_desinscriptions_examens_par_noma(
            code_unite_enseignement,
            annee,
            numero_session,
            inscription_examen_translator
        )
        signaletique_par_noma = _get_signaletique_etudiant_par_noma(nomas_concernes, signaletique_etudiant_translator)

        notes_etudiants = []
        for note in notes:
            inscr_exmen = inscr_examen_par_noma.get(note.noma)
            ouverture_periode_soumission = periode_encodage.debut_periode_soumission.to_date()
            inscrit_tardivement = inscr_exmen and inscr_exmen.date_inscription.to_date() > ouverture_periode_soumission
            desinscription = desinscr_exam_par_noma.get(note.noma)
            signaletique = signaletique_par_noma[note.noma]
            notes_etudiants.append(
                NoteEtudiantDTO(
                    est_soumise=note.est_soumise,
                    date_remise_de_notes=note.date_limite_de_remise,
                    nom_cohorte=inscr_exmen.nom_cohorte if inscr_exmen else desinscription.nom_cohorte,
                    noma=note.noma,
                    nom=signaletique.nom,
                    prenom=signaletique.prenom,
                    peps=signaletique.peps,
                    email=note.email,
                    note=note.note.value,
                    inscrit_tardivement=inscrit_tardivement,
                    desinscrit_tardivement=bool(desinscription),
                )
            )

        notes_etudiants.sort(key=lambda note: (note.nom_cohorte, note.nom, note.prenom))

        contact_responsable_notes = None
        if resp_notes:
            signaletiques_personnes = signaletique_personne_translator.search({resp_notes.matricule_fgs_enseignant})
            contact_responsable_notes = list(signaletiques_personnes)[0]

        return FeuilleDeNotesDTO(
            code_unite_enseignement=code_unite_enseignement,
            intitule_complet_unite_enseignement=unite_enseignement.intitule_complet,
            note_decimale_est_autorisee=notes[0].note_decimale_est_autorisee(),
            responsable_note=responsable_notes_dto,
            contact_responsable_notes=contact_responsable_notes,  # TODO :: merger responsable_note et contact_responsable note ?
            autres_enseignants=autres_enseignants,
            annee_academique=annee,
            numero_session=numero_session,
            notes_etudiants=notes_etudiants,
        )


def _get_signaletique_etudiant_par_noma(
        nomas_concernes: List['Noma'],
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
) -> Dict['Noma', 'SignaletiqueEtudiantDTO']:
    signaletiques_etds = signaletique_etudiant_translator.search(nomas=nomas_concernes)
    return {signal.noma: signal for signal in signaletiques_etds}


def _get_desinscriptions_examens_par_noma(
        code_unite_enseignement: str,
        annee: int,
        numero_session: int,
        inscription_examen_translator: 'IInscriptionExamenTranslator'
) -> Dict['Noma', 'DesinscriptionExamenDTO']:
    desinscriptions_examens = inscription_examen_translator.search_desinscrits(
        code_unite_enseignement=code_unite_enseignement,
        annee=annee,
        numero_session=numero_session,
    )
    return {desinscr.noma: desinscr for desinscr in desinscriptions_examens}


def _get_inscriptions_examens_par_noma(
        code_unite_enseignement: str,
        annee: int,
        numero_session: int,
        inscription_examen_translator: 'IInscriptionExamenTranslator'
) -> Dict['Noma', 'InscriptionExamenDTO']:
    inscr_examens = inscription_examen_translator.search_inscrits(
        code_unite_enseignement=code_unite_enseignement,
        annee=annee,
        numero_session=numero_session,
    )
    return {insc_exam.noma: insc_exam for insc_exam in inscr_examens}


def _get_autres_enseignants(
        attribution_translator: 'IAttributionEnseignantTranslator',
        code_unite_enseignement: str,
        annee: int,
        responsable_notes: Optional['EnseignantDTO']
) -> List[EnseignantDTO]:
    enseignants = attribution_translator.search_attributions_enseignant(code_unite_enseignement, annee)
    return [
        EnseignantDTO(nom=enseignant.nom, prenom=enseignant.prenom)
        for enseignant in sorted(enseignants, key=lambda ens: (ens.nom, ens.prenom))
        if not responsable_notes or (
                enseignant.nom != responsable_notes.nom and enseignant.prenom != responsable_notes.prenom
        )
    ]
