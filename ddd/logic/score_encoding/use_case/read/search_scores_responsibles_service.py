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
from typing import List

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.score_encoding.commands import SearchScoresResponsibleCommand
from ddd.logic.score_encoding.dtos import ScoreResponsibleDTO
from infrastructure.score_encoding.repository.score_responsible_repository import ScoreResponsibleRepository


def search_scores_responsibles(commands: List[SearchScoresResponsibleCommand]) -> List[ScoreResponsibleDTO]:
    repository = ScoreResponsibleRepository()
    lu_identities = [
        LearningUnitIdentityBuilder.build_from_search_scores_responsible_command(command) for command in commands
    ]
    return repository.score_responsible_search(lu_identities)
