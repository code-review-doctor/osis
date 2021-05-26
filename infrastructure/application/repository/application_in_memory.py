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

from ddd.logic.application.domain.model.applicant import ApplicantIdentity
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.repository.i_application_repository import IApplicationRepository
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity


class ApplicationInMemoryRepository(IApplicationRepository):
    applications = []

    # TODO remove this and change classmethod to instance method save/search/...
    def __init__(self, applications: List[Application] = None):
        ApplicationInMemoryRepository.applications = applications or []

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List[ApplicationIdentity]] = None,
            applicant_id: Optional[ApplicantIdentity] = None,
            academic_year_id: AcademicYearIdentity = None,
            **kwargs
    ) -> List[Application]:
        results = cls.applications
        if entity_ids is not None:
            results = filter(lambda application: application.entity_id in entity_ids, results)
        if applicant_id is not None:
            results = filter(lambda application: application.applicant_id == applicant_id, results)
        if academic_year_id is not None:
            results = filter(
                lambda application: application.vacant_course_id.academic_year == academic_year_id, results
            )
        return list(results)

    @classmethod
    def get(cls, entity_id: ApplicationIdentity) -> Application:
        return next(application for application in cls.applications if application.entity_id == entity_id)

    @classmethod
    def save(cls, application: Application) -> None:
        index = next((i for i, row in enumerate(cls.applications) if row == application), None)
        if index:
            cls.applications[index] = application
        else:
            cls.applications.append(application)

    @classmethod
    def delete(cls, entity_id: ApplicationIdentity, **kwargs) -> None:
        index = next((i for i, row in enumerate(cls.applications) if row.entity_id == entity_id), None)
        if index is not None:
            cls.applications.pop(index)
