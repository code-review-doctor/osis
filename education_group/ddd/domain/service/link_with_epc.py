##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.offer_enrollment import OfferEnrollment
from education_group.ddd.business_types import *
from education_group.ddd.domain.training import TrainingIdentity
from osis_common.ddd import interface


class LinkWithEPC(interface.DomainService):
    def have_link_with_epc(self, entity_id: Union['TrainingIdentity',  'MiniTrainingIdentity']):
        if isinstance(entity_id, TrainingIdentity):
            return self._training_have_link_with_epc(entity_id)
        # elif isinstance(entity_id, MiniTrainingIdentity):
        #    return self._mini_training_have_link_with_epc(entity_id)
        raise Exception("entity_id instance type not supported")

    def _training_have_link_with_epc(self, training_id: 'TrainingIdentity') -> bool:
        return OfferEnrollment.objects.filter(
            education_group_year__acronym=training_id.acronym,
            education_group_year__academic_year__year=training_id.year
        ).count()

    def _mini_training_have_link_with_epc(self, mini_training_id: 'MiniTrainingIdentity') -> bool:
        return OfferEnrollment.objects.filter(
            education_group_year__acronym=mini_training_id.acronym,
            education_group_year__academic_year__year=mini_training_id.year
        ).count()
