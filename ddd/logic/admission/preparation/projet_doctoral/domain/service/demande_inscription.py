# ##############################################################################
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
# ##############################################################################
from functools import partial

from base.ddd.utils.business_validator import execute_functions_and_aggregate_exceptions
from ddd.logic.admission.preparation.projet_doctoral.domain.model.groupe_de_supervision import GroupeDeSupervision
from ddd.logic.admission.preparation.projet_doctoral.domain.model.proposition import Proposition
from ddd.logic.admission.preparation.projet_doctoral.domain.service.i_profil_candidat import IProfilCandidatTranslator
from ddd.logic.admission.preparation.projet_doctoral.domain.service.profil_candidat import ProfilCandidat
from osis_common.ddd import interface


class DemandeInscription(interface.DomainService):
    @classmethod
    def verifier(
            cls,
            proposition_candidat: 'Proposition',
            groupe_supervision: 'GroupeDeSupervision',
            profil_candidat_translator: 'IProfilCandidatTranslator',
    ) -> None:
        profil_candidat_service = ProfilCandidat()
        execute_functions_and_aggregate_exceptions(
            partial(profil_candidat_service.verifier_identification, profil_candidat_translator),
            partial(profil_candidat_service.verifier_coordonnees, profil_candidat_translator),
            partial(profil_candidat_service.verifier_curriculum, profil_candidat_translator),
            groupe_supervision.verifier_tout_le_monde_a_approuve,
            proposition_candidat.verifier,
        )
