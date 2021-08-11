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
from typing import List, Dict

from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_identity_builder import \
    ResponsableDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model._note_etudiant import Noma
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import FeuilleDeNotesEnseignantDTO, EnseignantDTO, NoteEtudiantDTO, \
    SignaletiqueEtudiantDTO, InscriptionExamenDTO, DesinscriptionExamenDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd import interface


class FeuilleDeNotesEnseignant(interface.DomainService):

    @staticmethod
    def get(
            feuille_de_notes: 'FeuilleDeNotes',
            responsable_notes_repo: 'IResponsableDeNotesRepository',
            periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            attribution_translator: 'IAttributionEnseignantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'FeuilleDeNotesEnseignantDTO':

        periode_soumission_ouverte = periode_soumission_note_translator.get()
        unite_enseignement = unite_enseignement_translator.get(
            feuille_de_notes.code_unite_enseignement,
            feuille_de_notes.annee,
        )
        responsable_notes = _get_responsable_de_notes(
            feuille_de_notes.code_unite_enseignement,
            feuille_de_notes.annee,
            responsable_notes_repo,
        )
        autres_enseignants = _get_autres_enseignants(attribution_translator, feuille_de_notes, responsable_notes)

        nomas_concernes = [note.noma for note in feuille_de_notes.notes]

        inscr_examen_par_noma = _get_inscriptions_examens_par_noma(feuille_de_notes, inscription_examen_translator)
        desinscr_exam_par_noma = _get_desinscriptions_examens_par_noma(feuille_de_notes, inscription_examen_translator)
        signaletique_par_noma = _get_signaletique_etudiant_par_noma(nomas_concernes, signaletique_etudiant_translator)

        notes_etudiants = []
        for note in feuille_de_notes.notes:
            inscr_exmen = inscr_examen_par_noma.get(note.noma)
            ouverture_periode_soumission = periode_soumission_ouverte.debut_periode_soumission.to_date()
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
        return FeuilleDeNotesEnseignantDTO(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            intitule_complet_unite_enseignement=unite_enseignement.intitule_complet,
            note_decimale_est_autorisee=feuille_de_notes.note_decimale_est_autorisee(),
            responsable_note=EnseignantDTO(
                nom=responsable_notes.nom,
                prenom=responsable_notes.prenom,
            ),
            autres_enseignants=autres_enseignants,
            annee_academique=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            notes_etudiants=notes_etudiants,
        )


def _get_signaletique_etudiant_par_noma(
        nomas_concernes: List['Noma'],
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
) -> Dict['Noma', 'SignaletiqueEtudiantDTO']:
    signaletiques_etds = signaletique_etudiant_translator.search(nomas=nomas_concernes)
    return {signal.noma: signal for signal in signaletiques_etds}


def _get_desinscriptions_examens_par_noma(
        feuille_de_notes: 'FeuilleDeNotes',
        inscription_examen_translator: 'IInscriptionExamenTranslator'
) -> Dict['Noma', 'DesinscriptionExamenDTO']:
    desinscriptions_examens = inscription_examen_translator.search_desinscrits(
        code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
        annee=feuille_de_notes.annee,
        numero_session=feuille_de_notes.numero_session,
    )
    return {desinscr.noma: desinscr for desinscr in desinscriptions_examens}


def _get_inscriptions_examens_par_noma(
        feuille_de_notes: 'FeuilleDeNotes',
        inscription_examen_translator: 'IInscriptionExamenTranslator'
) -> Dict['Noma', 'InscriptionExamenDTO']:
    inscr_examens = inscription_examen_translator.search_inscrits(
        code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
        annee=feuille_de_notes.annee,
        numero_session=feuille_de_notes.numero_session,
    )
    return {insc_exam.noma: insc_exam for insc_exam in inscr_examens}


def _get_autres_enseignants(
        attribution_translator: 'IAttributionEnseignantTranslator',
        feuille_de_notes: 'FeuilleDeNotes',
        responsable_notes: 'EnseignantDTO'
) -> List[EnseignantDTO]:
    enseignants = attribution_translator.search_attributions_enseignant(
        feuille_de_notes.code_unite_enseignement,
        feuille_de_notes.annee,
    )
    return [
        EnseignantDTO(nom=enseignant.nom, prenom=enseignant.prenom)
        for enseignant in sorted(enseignants, key=lambda ens: (ens.nom, ens.prenom))
        if enseignant.nom != responsable_notes.nom and enseignant.prenom != responsable_notes.prenom
    ]


def _get_responsable_de_notes(
        code_unite_enseignement: str,
        annee: int,
        responsable_notes_repo: 'IResponsableDeNotesRepository'
) -> EnseignantDTO:
    resp_notes = responsable_notes_repo.get_for_unite_enseignement(code_unite_enseignement, annee)
    return responsable_notes_repo.get_detail_enseignant(resp_notes.entity_id)
