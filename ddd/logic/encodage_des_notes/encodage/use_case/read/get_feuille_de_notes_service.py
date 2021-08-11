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
from ddd.logic.encodage_des_notes.encodage.domain.service.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.domain.service.feuille_de_notes_gestionnaire import \
    FeuilleDeNotesGestionnaire
from ddd.logic.encodage_des_notes.encodage.domain.service.i_feuille_de_notes_enseignant import \
    IFeuilleDeNotesEnseignantTranslator
from ddd.logic.encodage_des_notes.encodage.dtos import FeuilleDeNotesGestionnaireDTO
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.common_domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.periode_soumission_ouverte import PeriodeEncodageOuverte


def get_feuille_de_notes_gestionnaire(
        cmd: 'GetFeuilleDeNotesGestionnaireCommand',
        periode_encodage_note_translator: 'IPeriodeEncodageNotesTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator',  # FIXME :: domain service partagé - à déplacer
        feuille_notes_enseignant_translator: 'IFeuilleDeNotesEnseignantTranslator',
        cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
) -> 'FeuilleDeNotesGestionnaireDTO':
    PeriodeEncodageOuverte().verifier(periode_encodage_note_translator)  # FIXME :: domain service partagé - à déplacer
    GestionnaireParcours().verifier(cmd.matricule_fgs_gestionnaire, cohortes_gestionnaire_translator)
    return FeuilleDeNotesGestionnaire().get(
        code_unite_enseignement=cmd.code_unite_enseignement,
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        periode_soumission_note_translator=periode_encodage_note_translator,
        attribution_translator=attribution_translator,
        feuille_notes_enseignant_translator=feuille_notes_enseignant_translator,
        cohortes_gestionnaire_translator=cohortes_gestionnaire_translator,
    )
