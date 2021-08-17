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
from ddd.logic.encodage_des_notes.encodage.commands import GetFeuilleDeNotesGestionnaireCommand
from ddd.logic.encodage_des_notes.encodage.domain.service.feuille_de_notes_par_cohorte import \
    FeuilleDeNotesParCohorte
from ddd.logic.encodage_des_notes.encodage.domain.service.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.dtos import FeuilleDeNotesParCohorteDTO
from ddd.logic.encodage_des_notes.shared_kernel.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.periode_encodage_ouverte import PeriodeEncodageOuverte
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def get_feuille_de_notes_gestionnaire(
        cmd: 'GetFeuilleDeNotesGestionnaireCommand',
        note_repo: 'INoteEtudiantRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_encodage_note_translator: 'IPeriodeEncodageNotesTranslator',
        inscription_examen_translator: 'IInscriptionExamenTranslator',
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator',
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
        cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
) -> 'FeuilleDeNotesParCohorteDTO':
    # GIVEN
    PeriodeEncodageOuverte().verifier(periode_encodage_note_translator)
    GestionnaireParcours().verifier(cmd.matricule_fgs_gestionnaire, cohortes_gestionnaire_translator)

    periode_encodage = periode_encodage_note_translator.get()
    notes = note_repo.search_by_code_unite_enseignement_annee_session(
        criterias=[
            (cmd.code_unite_enseignement, periode_encodage.annee_concernee, periode_encodage.session_concernee)
        ]
    )

    return FeuilleDeNotesParCohorte().get(
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        notes=notes,
        responsable_notes_repo=responsable_notes_repo,
        periode_encodage=periode_encodage_note_translator.get(),
        inscription_examen_translator=inscription_examen_translator,
        signaletique_etudiant_translator=signaletique_etudiant_translator,
        attribution_translator=attribution_translator,
        unite_enseignement_translator=unite_enseignement_translator,
        cohortes_gestionnaire_translator=cohortes_gestionnaire_translator,
    )
