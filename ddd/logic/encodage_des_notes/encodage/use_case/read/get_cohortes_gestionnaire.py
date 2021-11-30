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
from typing import Set

from ddd.logic.encodage_des_notes.encodage.commands import GetCohortesGestionnaireCommand, GetPeriodeEncodageCommand
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.dtos import CohorteGestionnaireDTO
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_periode_encodage_service import get_periode_encodage
from infrastructure.encodage_de_notes.shared_kernel.service.periode_encodage_notes import \
    PeriodeEncodageNotesTranslator


def get_cohortes_gestionnaire(
        cmd: GetCohortesGestionnaireCommand,
        cohortes_gestionnaire_translator: ICohortesDuGestionnaire,
) -> Set[CohorteGestionnaireDTO]:
    return cohortes_gestionnaire_translator.search(
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        annee_concernee=_get_annee_periode_encodage()
    )


def _get_annee_periode_encodage() -> int:
    period_encodage = get_periode_encodage(GetPeriodeEncodageCommand(), PeriodeEncodageNotesTranslator())
    return period_encodage.annee_concernee
