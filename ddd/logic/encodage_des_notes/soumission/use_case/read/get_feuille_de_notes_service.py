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
from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.service.feuille_de_notes_enseignant import FeuilleDeNotesEnseignant
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.periode_soumission_ouverte import PeriodeSoumissionOuverte
from ddd.logic.encodage_des_notes.soumission.dtos import FeuilleDeNotesEnseignantDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_feuille_de_notes import IFeuilleDeNotesRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def get_feuille_de_notes(
        cmd: 'GetFeuilleDeNotesCommand',
        feuille_de_note_repo: 'IFeuilleDeNotesRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
        inscription_examen_translator: 'IInscriptionExamenTranslator',
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator',
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
) -> 'FeuilleDeNotesEnseignantDTO':
    # GIVEN
    PeriodeSoumissionOuverte().verifier(periode_soumission_note_translator)
    periode_soumission = periode_soumission_note_translator.get()
    feuille_notes_entity_id = FeuilleDeNotesIdentityBuilder.build_from_session_and_unit_enseignement_datas(
        numero_session=periode_soumission.session_concernee,
        code_unite_enseignement=cmd.code_unite_enseignement,
        annee_academique=periode_soumission.annee_concernee,
    )

    # WHEN
    feuille_de_notes_dto = FeuilleDeNotesEnseignant().get(
        feuille_de_note_repo.get(feuille_notes_entity_id),
        responsable_notes_repo,
        periode_soumission_note_translator,
        inscription_examen_translator,
        signaletique_etudiant_translator,
        attribution_translator,
        unite_enseignement_translator,
    )

    return feuille_de_notes_dto
