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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import abc
import uuid
from typing import List

import attr

from osis_common.ddd import interface


class ReportEvent(abc.ABC):
    def __str__(self):
        raise NotImplementedError


@attr.s(frozen=True, slots=True)
class ReportIdentity(interface.EntityIdentity):
    transaction_id = attr.ib(type=uuid.UUID)


@attr.s()
class Report(interface.Entity):
    entity_id = attr.ib(type=ReportIdentity)
    changes = attr.ib(init=False, type=List[ReportEvent], factory=list)
    warnings = attr.ib(init=False, type=List[ReportEvent], factory=list)

    def add_change(self, event: ReportEvent) -> None:
        self.changes.append(event)

    def add_warning(self, event: ReportEvent) -> None:
        self.warnings.append(event)

    def get_changes(self) -> List[ReportEvent]:
        return self.changes

    def get_warnings(self) -> List[ReportEvent]:
        return self.warnings
