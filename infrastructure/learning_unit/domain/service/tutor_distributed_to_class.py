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
from typing import Union

from attribution.models.attribution_class import AttributionClass as AttributionClassDb
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.service.i_tutor_distributed_to_class import ITutorDistributedToClass


class TutorDistributedToClass(ITutorDistributedToClass):

    @classmethod
    def get_first_tutor_full_name_if_exists(
            cls,
            effective_class_identity: 'EffectiveClassIdentity'
    ) -> Optional[str]:
        ue_identity = effective_class_identity.learning_unit_identity
        results = AttributionClassDb.objects.filter(
            learning_class_year__learning_component_year__learning_unit_year__acronym=ue_identity.code,
            learning_class_year__learning_component_year__learning_unit_year__academic_year__year=ue_identity.year,
            learning_class_year__acronym=effective_class_identity.class_code
        )
        if results:
            return results[0].attribution_charge.attribution.tutor.person.full_name
        return None
