##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import Optional, List

import uuid

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    IdentiteGroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee, UniteEnseignementAjouteeIdentity
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from education_group.ddd.domain.group import GroupIdentity
from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity, STANDARD


class GroupementAjusteInscriptionCoursInMemoryRepository(
    InMemoryGenericRepository,
    IGroupementAjusteInscriptionCoursRepository
):

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteGroupementAjusteInscriptionCours']] = None,
            version_programme_id: 'ProgramTreeVersionIdentity' = None,
            groupement_id: 'GroupIdentity' = None,
            **kwargs
    ) -> List['GroupementAjusteInscriptionCours']:
        return [
            ajustement for ajustement in cls.entities
            if (not version_programme_id or ajustement.version_programme_id == version_programme_id)
            and (not groupement_id or ajustement.groupement_id == groupement_id)
        ]
