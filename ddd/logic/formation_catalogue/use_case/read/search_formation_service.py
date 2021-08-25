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
from typing import List

from ddd.logic.formation_catalogue.commands import SearchFormationsCommand
from ddd.logic.formation_catalogue.dtos import TrainingDto
from education_group.ddd.repository.training import TrainingRepository


def search_formations(
        cmd: 'SearchFormationsCommand',
        training_repository: 'TrainingRepository',
) -> List['TrainingDto']:
    # TODO :: assurer qu'au moins 1 param de recherche soit rempli
    # entites_de_gestion = [cmd.sigle_entite_gestion] if cmd.sigle_entite_gestion else []
    # if cmd.inclure_entites_gestion_subordonnees:
    #     entities = get_entities_ids(entity_acronym=cmd.sigle_entite_gestion, with_entity_subordinated=True)
    #     entites_de_gestion += entities
    # TODO :: gérer cmd. inclure_entites_gestion_subordonnees et cmd.sigle_entite_gestion (shared kernel UCLEntity)
    # TODO :: unit tests
    return training_repository.search_dtos(
        sigle=cmd.sigle,
        annee=cmd.annee,
        type=cmd.type,
    )
