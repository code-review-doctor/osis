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
from typing import List

from base.utils.string import unaccent
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.feuille_de_notes_par_unite_enseignement import \
    FeuilleDeNotesParUniteEnseignement, DonneesNotes
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EnseignantDTO, PeriodeEncodageNotesDTO, FeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd import interface


class FeuilleDeNotesParCohorte(interface.DomainService):

    @classmethod
    def get(
            cls,
            matricule_gestionnaire: str,
            notes: List['NoteEtudiant'],
            responsable_notes_repo: 'IResponsableDeNotesRepository',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            periode_encodage: 'PeriodeEncodageNotesDTO',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            attribution_translator: 'IAttributionEnseignantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
            cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
    ) -> 'FeuilleDeNotesDTO':
        donnees_notes = [
            DonneesNotes(
                code_unite_enseignement=note.code_unite_enseignement,
                annee=note.annee_academique,
                noma=note.noma,
                email=note.email,
                note=str(note.note),
                date_limite_de_remise=note.echeance_gestionnaire,
                est_soumise=not note.is_manquant,
                note_decimale_autorisee=note.note_decimale_autorisee,
                echeance_enseignant=note.echeance_enseignant
            )
            for note in notes
        ]

        feuille_notes_enseignant = FeuilleDeNotesParUniteEnseignement().get(
            notes=donnees_notes,
            responsable_notes_repo=responsable_notes_repo,
            signaletique_personne_translator=signaletique_personne_translator,
            periode_encodage=periode_encodage,
            inscription_examen_translator=inscription_examen_translator,
            signaletique_etudiant_translator=signaletique_etudiant_translator,
            attribution_translator=attribution_translator,
            unite_enseignement_translator=unite_enseignement_translator,
        )

        cohortes_gerees_par_gestionnaire = _get_cohortes_gerees_par_gestionnaire(
            cohortes_gestionnaire_translator,
            matricule_gestionnaire,
            periode_encodage.annee_concernee
        )

        notes_triees = sorted(
            feuille_notes_enseignant.notes_etudiants,
            key=lambda note: (note.nom_cohorte, unaccent(note.nom), unaccent(note.prenom))
        )
        etudiants_gestionnaire = [note for note in notes_triees if note.nom_cohorte in cohortes_gerees_par_gestionnaire]

        autres_enseignants = [
            EnseignantDTO(nom=enseignant.nom, prenom=enseignant.prenom)
            for enseignant in feuille_notes_enseignant.autres_enseignants
        ]

        return FeuilleDeNotesDTO(
            code_unite_enseignement=feuille_notes_enseignant.code_unite_enseignement,
            intitule_complet_unite_enseignement=feuille_notes_enseignant.intitule_complet_unite_enseignement,
            responsable_note=feuille_notes_enseignant.responsable_note,
            contact_responsable_notes=feuille_notes_enseignant.contact_responsable_notes,
            autres_enseignants=autres_enseignants,
            annee_academique=feuille_notes_enseignant.annee_academique,
            numero_session=feuille_notes_enseignant.numero_session,
            notes_etudiants=etudiants_gestionnaire,
            note_decimale_est_autorisee=feuille_notes_enseignant.note_decimale_est_autorisee
        )


def _get_cohortes_gerees_par_gestionnaire(
        cohortes_gestionnaire_translator, matricule_gestionnaire: str, annee_concernee: int
):
    cohortes_gestionnaire = cohortes_gestionnaire_translator.search(
        matricule_gestionnaire=matricule_gestionnaire,
        annee_concernee=annee_concernee
    )
    return {gestionnaire.nom_cohorte for gestionnaire in cohortes_gestionnaire}
