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

from attribution.models.tutor_application import TutorApplication
from base.auth.roles.tutor import Tutor
from base.models.learning_container_year import LearningContainerYear
from ddd.logic.application.domain.model.application import ApplicationIdentity, Application
from ddd.logic.application.repository.i_application_repository import IApplicationRepository


class ApplicationRepository(IApplicationRepository):
    @classmethod
    def search(
            cls,
            entity_ids: Optional[List[ApplicationIdentity]] = None,
            global_id: Optional[str] = None, **kwargs
    ) -> List[Application]:
        pass

    @classmethod
    def get(cls, entity_id: 'ApplicationIdentity') -> 'Application':
        pass

    @classmethod
    def save(cls, application: Application) -> None:
        tutor_id = Tutor.objects.get(global_id=application.applicant.entity_id.global_id).pk
        learning_container_year_id = LearningContainerYear.objects.get(
            acronym=application.course.code,
            academic_year__year=application.course.year
        ).pk

        obj, created = TutorApplication.objects.update_or_create(
            uuid=application.entity_id.uuid,
            defaults={
                "tutor_id": tutor_id,
                "learning_container_year_id": learning_container_year_id,
                "volume_lecturing": application.lecturing_volume,
                "volume_pratical_exercice": application.practical_volume,
                "remark": application.remark,
                "course_summary": application.course_summary
            }
        )
