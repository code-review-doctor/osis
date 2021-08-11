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

from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.domain.service.i_feuille_de_notes_enseignant import \
    IFeuilleDeNotesEnseignantTranslator
from ddd.logic.encodage_des_notes.encodage.dtos import FeuilleDeNotesGestionnaireDTO, NoteEtudiantDTO
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from osis_common.ddd import interface


class FeuilleDeNotesGestionnaire(interface.DomainService):

    @classmethod
    def get(
            cls,
            code_unite_enseignement: str,
            matricule_gestionnaire: str,
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            attribution_translator: 'IAttributionEnseignantTranslator',
            feuille_notes_enseignant_translator: 'IFeuilleDeNotesEnseignantTranslator',
            cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
    ) -> 'FeuilleDeNotesGestionnaireDTO':
        periode_soumission_ouverte = periode_soumission_note_translator.get()

        feuille_notes_enseignant = _get_feuille_de_notes_enseignant(
            attribution_translator,
            code_unite_enseignement,
            feuille_notes_enseignant_translator,
            periode_soumission_ouverte.annee_concernee,
        )

        cohortes_gerees_par_gestionnaire = _get_cohortes_gerees_par_gestionnaire(
            cohortes_gestionnaire_translator,
            matricule_gestionnaire,
        )

        etudiants_gestionnaire = []
        etudiants_enseignant = feuille_notes_enseignant.notes_etudiants
        test = sorted(etudiants_enseignant, key=lambda note: (note.nom_cohorte, note.nom, note.prenom))
        for note in test:
            if note.nom_cohorte in cohortes_gerees_par_gestionnaire:
                etudiants_gestionnaire.append(
                    NoteEtudiantDTO(
                        est_soumise=note.est_soumise,
                        echeance_enseignant=note.date_remise_de_notes,
                        nom_cohorte=note.nom_cohorte,
                        noma=note.noma,
                        nom=note.nom,
                        prenom=note.prenom,
                        peps=note.peps,
                        email=note.email,
                        note=note.note,
                        inscrit_tardivement=note.inscrit_tardivement,
                        desinscrit_tardivement=note.desinscrit_tardivement,
                    )
                )

        return FeuilleDeNotesGestionnaireDTO(
            code_unite_enseignement=feuille_notes_enseignant.code_unite_enseignement,
            intitule_complet_unite_enseignement=feuille_notes_enseignant.intitule_complet_unite_enseignement,
            responsable_note=feuille_notes_enseignant.responsable_note,
            autres_enseignants=feuille_notes_enseignant.autres_enseignants,
            annee_academique=feuille_notes_enseignant.annee_academique,
            numero_session=feuille_notes_enseignant.numero_session,
            notes_etudiants=etudiants_gestionnaire,
        )


def _get_cohortes_gerees_par_gestionnaire(cohortes_gestionnaire_translator, matricule_gestionnaire):
    cohortes_gestionnaire = cohortes_gestionnaire_translator.search(matricule_gestionnaire=matricule_gestionnaire)
    return {gestionnaire.nom_cohorte for gestionnaire in cohortes_gestionnaire}


def _get_feuille_de_notes_enseignant(
        attribution_translator,
        code_unite_enseignement,
        feuille_notes_enseignant_translator,
        annee_concernee,
):
    attributions = attribution_translator.search_attributions_enseignant(
        code_unite_enseignement,
        annee_concernee,
    )
    # Peu importe l'enseignant, l'objectif est de récupérer la feuille de notes => on récupère le premier
    matricule_fgs_enseignant = list(attributions)[0].matricule_fgs_enseignant
    return feuille_notes_enseignant_translator.get(
        code_unite_enseignement=code_unite_enseignement,
        matricule_fgs_enseignant=matricule_fgs_enseignant,
    )
