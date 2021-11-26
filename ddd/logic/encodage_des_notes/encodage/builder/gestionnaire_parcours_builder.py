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
from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours, \
    IdentiteGestionnaire
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PasGestionnaireParcoursException

from osis_common.ddd import interface
from osis_common.ddd.interface import CommandRequest


class GestionnaireParcoursBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'NoteEtudiant':
        raise NotImplementedError

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'interface.DTO') -> 'NoteEtudiant':
        raise NotImplementedError

    @classmethod
    def get(
            cls,
            matricule_gestionnaire: str,
            cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
    ) -> 'GestionnaireParcours':
        cohortes_gestionnaire = cohortes_gestionnaire_translator.search(matricule_gestionnaire)
        if not cohortes_gestionnaire:
            raise PasGestionnaireParcoursException()
        return GestionnaireParcours(
            entity_id=IdentiteGestionnaire(matricule_gestionnaire),
            cohortes_gerees=[dto.nom_cohorte for dto in cohortes_gestionnaire],
        )
