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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

from base.models import academic_year
from base.models.education_group_year import EducationGroupYear
from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import IEntitesCohorteTranslator
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from ddd.logic.shared_kernel.entite.domain.model.entite import IdentiteEntite
from education_group.models.cohort_year import CohortYear


class EntitesCohorteTranslator(IEntitesCohorteTranslator):

    @classmethod
    def search(cls, nom_cohorte: str) -> List['IdentiteEntite']:
        builder = IdentiteEntiteBuilder()
        if "11BA" in nom_cohorte:
            cohort = CohortYear.objects.get_first_year_bachelor(
                education_group_year__acronym=nom_cohorte.replace("11BA", '1BA'),
                education_group_year__academic_year=academic_year.current_academic_year()
            )
            entities = {
                builder.build_from_sigle(cohort.education_group_year.administration_entity.most_recent_acronym)
                if not cohort.administration_entity
                else builder.build_from_sigle(cohort.administration_entity.most_recent_acronym),
                builder.build_from_sigle(cohort.education_group_year.management_entity.most_recent_acronym),
            }
        else:
            egy = EducationGroupYear.objects.filter(
                academic_year=academic_year.current_academic_year(),
                acronym=nom_cohorte
            ).select_related(
                "management_entity",
                "administration_entity"
            ).get()
            entities = {
                builder.build_from_sigle(egy.management_entity.most_recent_acronym),
                builder.build_from_sigle(egy.administration_entity.most_recent_acronym),
            }
        return list(entities)
