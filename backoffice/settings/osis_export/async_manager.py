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
from osis_async.models import AsyncTask
from osis_async.models.enums import TaskStates
from osis_async.utils import update_task
from osis_export.contrib.async_manager import AsyncManager


class AsyncTaskManager(AsyncManager):
    @staticmethod
    def get_pending_job_uuids():
        """"Must return the pending export job uuids"""
        pending_tasks = AsyncTask.objects.filter(
            state=TaskStates.PENDING.name
        ).values_list("uuid", flat=True)
        return pending_tasks

    @staticmethod
    def update(
        uuid,
        progression=None,
        description=None,
        state=None,
        started_at=None,
        completed_at=None,
    ):
        update_task(uuid, progression, description, state, started_at, completed_at)
