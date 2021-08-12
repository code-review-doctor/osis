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
from ddd.logic.encodage_des_notes.shared_kernel.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.periode_encodage_ouverte import PeriodeEncodageOuverte
from ddd.logic.encodage_des_notes.encodage.commands import GetFeuilleDeNotesGestionnaireCommand
from ddd.logic.encodage_des_notes.encodage.domain.service.feuille_de_notes_gestionnaire import \
    FeuilleDeNotesGestionnaire
from ddd.logic.encodage_des_notes.encodage.domain.service.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.dtos import FeuilleDeNotesGestionnaireDTO
from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.shared_kernel.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.repository.i_feuille_de_notes import IFeuilleDeNotesRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def get_feuille_de_notes_gestionnaire(
        cmd: 'GetFeuilleDeNotesGestionnaireCommand',
        feuille_de_note_repo: 'IFeuilleDeNotesRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_encodage_note_translator: 'IPeriodeEncodageNotesTranslator',
        inscription_examen_translator: 'IInscriptionExamenTranslator',
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator',
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
        cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
) -> 'FeuilleDeNotesGestionnaireDTO':
    # GIVEN
    PeriodeEncodageOuverte().verifier(periode_encodage_note_translator)
    GestionnaireParcours().verifier(cmd.matricule_fgs_gestionnaire, cohortes_gestionnaire_translator)

    periode_encodage = periode_encodage_note_translator.get()
    feuille_notes_entity_id = FeuilleDeNotesIdentityBuilder.build_from_session_and_unit_enseignement_datas(
        numero_session=periode_encodage.session_concernee,
        code_unite_enseignement=cmd.code_unite_enseignement,
        annee_academique=periode_encodage.annee_concernee,
    )
    feuille_de_notes = feuille_de_note_repo.get(feuille_notes_entity_id)

    return FeuilleDeNotesGestionnaire().get(
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        feuille_de_notes=feuille_de_notes,
        responsable_notes_repo=responsable_notes_repo,
        periode_encodage=periode_encodage_note_translator.get(),
        inscription_examen_translator=inscription_examen_translator,
        signaletique_etudiant_translator=signaletique_etudiant_translator,
        attribution_translator=attribution_translator,
        unite_enseignement_translator=unite_enseignement_translator,
        cohortes_gestionnaire_translator=cohortes_gestionnaire_translator,
    )
