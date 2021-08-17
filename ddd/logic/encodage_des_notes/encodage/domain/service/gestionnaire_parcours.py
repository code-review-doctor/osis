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
from typing import List, Set

from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    PasGestionnaireParcoursException, PasGestionnaireParcoursCohorteException
from osis_common.ddd import interface


class GestionnaireParcours(interface.DomainService):

    @classmethod
    def verifier(
            cls,
            matricule_gestionnaire: str,
            cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
    ) -> None:
        if not cohortes_gestionnaire_translator.search(matricule_gestionnaire):
            # TODO :: perfomance : 'search' est appelé 2 fois dans meme use case
            # TODO :: perfomance : pareil pour 'PeriodeSoumissionOuverte'
            raise PasGestionnaireParcoursException()

    @classmethod
    def verifier_cohortes_gerees(
            cls,
            matricule_gestionnaire: str,
            cohortes_a_verifier: Set[str],
            cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
    ) -> None:
        cohortes_gerees = cohortes_gestionnaire_translator.search(matricule_gestionnaire)
        noms_cohortes_gerees = {c.nom_cohorte for c in cohortes_gerees}
        cohortes_non_gerees = cohortes_a_verifier - noms_cohortes_gerees
        if cohortes_non_gerees:
            raise PasGestionnaireParcoursCohorteException(cohortes_non_gerees)
