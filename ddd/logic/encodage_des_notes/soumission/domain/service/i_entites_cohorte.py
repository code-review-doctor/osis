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
from typing import Set, List, Optional

import attr

from ddd.logic.shared_kernel.entite.domain.model.entiteucl import IdentiteUCLEntite
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class EntitesCohorteDTO:
    administration = attr.ib(type=Optional[IdentiteUCLEntite])
    gestion = attr.ib(type=Optional[IdentiteUCLEntite])


class IEntitesCohorteTranslator(interface.DomainService):

    @classmethod
    @abc.abstractmethod
    def search_entite_administration_et_gestion(cls, nom_cohorte: str, annee: int) -> EntitesCohorteDTO:
        raise NotImplementedError()
