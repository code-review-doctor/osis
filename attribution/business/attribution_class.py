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
from collections import OrderedDict
from typing import List

from attribution.models.attribution_class import AttributionClass
from base.models.enums.component_type import LECTURING, PRACTICAL_EXERCISES


def create_attributions_dictionary(class_attribution_charges: List[AttributionClass]) -> OrderedDict():
    attributions = OrderedDict()

    for class_attribution in class_attribution_charges:
        attribution_charge = class_attribution.attribution_charge
        attribution = attribution_charge.attribution
        key = attribution.id
        component_type = class_attribution.learning_class_year.learning_component_year.type
        attribution_dict = {
            "person": attribution.tutor.person,
            "function": attribution.function,
            "start_year": attribution.start_year,
            "duration": attribution.duration,
            "substitute": attribution.substitute,
            "score_responsible": attribution.score_responsible,
            "pm_allocation_charge":
                class_attribution.allocation_charge if component_type == LECTURING else None,
            "pp_allocation_charge":
                class_attribution.allocation_charge if component_type == PRACTICAL_EXERCISES else None
        }
        attributions.setdefault(key, attribution_dict) \
            .update({attribution_charge.learning_component_year.type: attribution_charge.allocation_charge})
    return attributions
