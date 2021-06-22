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
from decimal import Decimal

import attr

from ddd.logic.application.domain.model.applicant import ApplicantIdentity
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class ApplicationIdentity(interface.EntityIdentity):
    uuid = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class Application(interface.RootEntity):
    entity_id = attr.ib(type=ApplicationIdentity)
    applicant_id = attr.ib(type=ApplicantIdentity)
    vacant_course_id = attr.ib(type=VacantCourseIdentity)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)
    remark = attr.ib(type=str)
    course_summary = attr.ib(type=str)

    def update(self, cmd: 'UpdateApplicationCommand'):
        # FIXME: Replace by setter/getter + validator on setter
        self.lecturing_volume = cmd.lecturing_volume
        self.practical_volume = cmd.practical_volume
        self.course_summary = cmd.course_summary
        self.remark = cmd.remark
