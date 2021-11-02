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

from base.models.person import Person, search_employee
from ddd.logic.shared_kernel.personne_connue_ucl.domain.service.personne_connue_ucl import IPersonneConnueUclTranslator
from ddd.logic.shared_kernel.personne_connue_ucl.dtos import PersonneConnueUclDTO


class PersonneConnueUclTranslator(IPersonneConnueUclTranslator):
    @classmethod
    def get(cls, matricule: str) -> 'PersonneConnueUclDTO':
        person = Person.objects.get(global_id=matricule)
        return PersonneConnueUclDTO(
            matricule=matricule,
            nom=person.last_name,
            prenom=person.first_name,
            email=person.email,
            adresse_professionnelle=None,
        )

    @classmethod
    def search(cls, terme_de_recherche: str) -> List['PersonneConnueUclDTO']:
        persons = search_employee(terme_de_recherche)
        return [PersonneConnueUclDTO(
            matricule=person.global_id,
            nom=person.last_name,
            prenom=person.first_name,
            email=person.email,
            adresse_professionnelle=None,
        ) for person in persons]

    @classmethod
    def search_by_matricules(cls, matricules_fgs: Set[str]) -> List['PersonneConnueUclDTO']:
        persons = Person.objects.filter(global_id__in=matricules_fgs)
        return [PersonneConnueUclDTO(
            matricule=person.global_id,
            nom=person.last_name,
            prenom=person.first_name,
            email=person.email,
            adresse_professionnelle=None,
        ) for person in persons]
