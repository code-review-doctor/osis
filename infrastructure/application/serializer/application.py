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
from base.models.learning_container_year import LearningContainerYear
from ddd.logic.application.domain.model.application import Application


class ApplicationSerializer:
    def serialize_to_delete_epc_message(self, application: Application):
        return {
            'operation': "delete",
            'remark': application.remark,
            'course_summary': application.course_summary,
            'lecturing_allocation': str(application.lecturing_volume) if application.lecturing_volume else '0',
            'practical_allocation': str(application.practical_volume) if application.practical_volume else '0',
            'learning_container_year': {
                'reference': self._get_reference(application),
                'year': str(application.vacant_course_id.year),
                'acronym': application.vacant_course_id.code
            }
        }

    def serialize_to_update_epc_message(self, application: Application):
        return {
            'operation': "update",
            'remark': application.remark,
            'course_summary': application.course_summary,
            'lecturing_allocation': str(application.lecturing_volume) if application.lecturing_volume else '0',
            'practical_allocation': str(application.practical_volume) if application.practical_volume else '0',
            'learning_container_year': {
                'reference': self._get_reference(application),
                'year': str(application.vacant_course_id.year),
                'acronym': application.vacant_course_id.code
            }
        }

    def _get_reference(self, application: Application) -> str:
        db_obj = LearningContainerYear.objects.get(
            academic_year__year=application.vacant_course_id.year,
            acronym=application.vacant_course_id.code
        )
        external_id = db_obj.external_id.replace("osis.learning_container_year_", '')
        external_ids = external_id.split('_')
        if len(external_ids) >= 2:
            return external_ids[0]
        return ''
