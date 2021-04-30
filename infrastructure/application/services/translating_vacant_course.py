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
from ddd.logic.application.domain.model.vacant_course import VacantCourse, VacantCourseIdentity
from ddd.logic.application.domain.service.vacant_course_service import IVacantCourseService
from ddd.logic.learning_unit.commands import LearningUnitSearchCommand
from infrastructure.messages_bus import message_bus_instance


class LearningUnitInVacantCourseAdapter:
    def to_vacant_course(self, code: str, academic_year: int):
        cmd = LearningUnitSearchCommand(
            code=code,
            year=academic_year,
            type=None,
            full_title=None,
            responsible_entity_code=None
        )
        external_obj = message_bus_instance.invoke(cmd)
        vacant_course = VacantCourseTranslator().to_vacant_course_from_representation(external_obj)
        return vacant_course


class VacantCourseTranslator:
    def to_vacant_course_from_representation(self, external_obj):
        identity = VacantCourseIdentity(academic_year=external_obj.academic_year, code=external_obj.code)
        return VacantCourse(
            entity_id=identity,
            lecturing_volume_available=0,
            practical_volume_available=0
        )


class TranslatingVacantCourseService(IVacantCourseService):
    def get(self, code: str, academic_year: int) -> VacantCourse:
        return LearningUnitInVacantCourseAdapter().to_vacant_course(code, academic_year)
