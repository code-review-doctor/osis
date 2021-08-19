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

from ddd.logic.effective_class_repartition.commands import SearchClassesEnseignantCommand
from ddd.logic.effective_class_repartition.domain.service.class_distribution_with_attribution import \
    ClassDistributionWithAttribution
from ddd.logic.effective_class_repartition.domain.service.i_tutor_attribution import \
    ITutorAttributionToLearningUnitTranslator
from ddd.logic.effective_class_repartition.dtos import TutorClassRepartitionDTO
from ddd.logic.effective_class_repartition.repository.i_tutor import ITutorRepository


def search_classes_enseignant(
        cmd: 'SearchClassesEnseignantCommand',
        tutor_attribution_translator: 'ITutorAttributionToLearningUnitTranslator',
        tutor_repository: 'ITutorRepository'
) -> List['TutorClassRepartitionDTO']:
    return ClassDistributionWithAttribution().search_by_matricule_enseignant(
        cmd.matricule_fgs_enseignant,
        tutor_attribution_translator,
        tutor_repository
    )
