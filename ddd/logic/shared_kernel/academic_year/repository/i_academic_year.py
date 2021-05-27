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
from abc import abstractmethod
from typing import Optional, List

from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYear, AcademicYearIdentity
from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService


class IAcademicYearRepository(interface.AbstractRepository):
    @classmethod
    @abstractmethod
    def get(cls, entity_id: 'AcademicYearIdentity') -> 'AcademicYear':
        pass

    @classmethod
    @abstractmethod
    def search(
            cls,
            entity_ids: Optional[List['AcademicYearIdentity']] = None,
            min_year: Optional[int] = None,
            **kwargs
    ) -> List['AcademicYear']:
        pass

    @classmethod
    @abstractmethod
    def delete(cls, entity_id: 'AcademicYearIdentity', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    @abstractmethod
    def save(cls, entity: 'AcademicYear') -> None:
        pass
