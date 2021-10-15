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

from base.models import academic_year
from base.models.education_group_year import EducationGroupYear
from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import IEntitesCohorteTranslator, \
    EntitesCohorteDTO
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from education_group.models.cohort_year import CohortYear


class EntitesCohorteTranslator(IEntitesCohorteTranslator):

    @classmethod
    def search_entite_administration_et_gestion(cls, nom_cohorte: str) -> EntitesCohorteDTO:
        builder = IdentiteEntiteBuilder()
        if "11BA" in nom_cohorte:
            cohort = CohortYear.objects.get_first_year_bachelor(
                education_group_year__acronym=nom_cohorte.replace("11BA", '1BA'),
                education_group_year__academic_year=academic_year.current_academic_year()
            )
            management_entity_acronym = cohort.education_group_year.management_entity.most_recent_acronym
            administration_entity_acronym = cohort.education_group_year.administration_entity.most_recent_acronym \
                if not cohort.administration_entity \
                else cohort.administration_entity.most_recent_acronym

        else:
            egy = EducationGroupYear.objects.filter(
                academic_year=academic_year.current_academic_year(),
                acronym=nom_cohorte
            ).select_related(
                "management_entity",
                "administration_entity"
            ).get()
            management_entity_acronym = egy.management_entity.most_recent_acronym
            administration_entity_acronym = egy.administration_entity.most_recent_acronym

        management_entity = None
        administration_entity = None
        if management_entity_acronym:
            management_entity = builder.build_from_sigle(management_entity_acronym)
        if administration_entity_acronym:
            administration_entity = builder.build_from_sigle(administration_entity_acronym)
        return EntitesCohorteDTO(
            administration=administration_entity,
            gestion=management_entity
        )
