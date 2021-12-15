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
from typing import List, Optional

from ddd.logic.application.domain.model.applicant import ApplicantIdentity, Applicant
from ddd.logic.application.repository.i_applicant_respository import IApplicantRepository


class ApplicantInMemoryRepository(IApplicantRepository):
    applicants = []

    # TODO remove this and change classmethod to instance method save/search/...
    def __init__(self, applicants: List[Applicant] = None):
        ApplicantInMemoryRepository.applicants = applicants or []

    @classmethod
    def search(cls, entity_ids: Optional[List[ApplicantIdentity]] = None, **kwargs) -> List[Applicant]:
        results = cls.applicants
        if entity_ids:
            results = filter(lambda vacant_course: vacant_course.entity_id in entity_ids, results)
        return list(results)

    @classmethod
    def get(cls, entity_id: ApplicantIdentity) -> Applicant:
        return next(applicant for applicant in cls.applicants if applicant.entity_id == entity_id)
