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

from ddd.logic.encodage_des_notes.shared_kernel.service.i_signaletique_personne import ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DetailContactDTO, AdresseDTO


class SignaletiquePersonneTranslatorInMemory(ISignaletiquePersonneTranslator):

    signaletiques = {
        DetailContactDTO(
            matricule_fgs='00321234',
            email='charles.smith@email.com',
            adresse_professionnelle=AdresseDTO(
                code_postal='1410',
                ville='Waterloo',
                rue_numero_boite='Rue de Waterloo, 123',
            ),
        ),
    }

    @classmethod
    def search(
            cls,
            matricules_fgs: Set[str]
    ) -> Set['DetailContactDTO']:
        return set(
            filter(
                lambda dto: _filter(dto, matricules_fgs),
                cls.signaletiques,
            )
        )


def _filter(dto, matricules_fgs):
    return dto.matricule_fgs in matricules_fgs
