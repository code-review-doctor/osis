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
from typing import Set, List

from ddd.logic.shared_kernel.personne_connue_ucl.domain.service.personne_connue_ucl import IPersonneConnueUclTranslator
from ddd.logic.shared_kernel.personne_connue_ucl.domain.validator.exceptions import PersonneNonConnueDeLUcl
from ddd.logic.shared_kernel.personne_connue_ucl.dtos import PersonneConnueUclDTO, AdresseDTO


class PersonneConnueUclInMemoryTranslator(IPersonneConnueUclTranslator):
    personnes_connues_ucl = {
        PersonneConnueUclDTO(
            matricule='00321234',
            email='charles.smith@email.com',
            prenom='Charles',
            nom='Smith',
            adresse_professionnelle=AdresseDTO(
                code_postal='1410',
                ville='Waterloo',
                rue_numero_boite='Rue de Waterloo, 123',
            ),
        ),
        PersonneConnueUclDTO(
            matricule='00987890',
            email='jean.dupont@email.com',
            prenom='Jean',
            nom='Dupont',
            adresse_professionnelle=AdresseDTO(
                code_postal='1348',
                ville='Louvain-La-Neuve',
                rue_numero_boite='Rue du Compas, 1',
            ),
        ),
    }

    @classmethod
    def get(cls, matricule: str) -> 'PersonneConnueUclDTO':
        try:
            return next(p for p in cls.personnes_connues_ucl if p.matricule == matricule)
        except StopIteration:
            raise PersonneNonConnueDeLUcl

    @classmethod
    def search(cls, terme_de_recherche: str) -> List['PersonneConnueUclDTO']:
        raise NotImplementedError

    @classmethod
    def search_by_matricules(cls, matricules: Set[str]) -> Set['PersonneConnueUclDTO']:
        return {p for p in cls.personnes_connues_ucl if p.matricule in matricules}
