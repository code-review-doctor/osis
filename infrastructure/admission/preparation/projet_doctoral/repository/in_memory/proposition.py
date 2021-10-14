# ##############################################################################
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
# ##############################################################################
from typing import List, Optional

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.admission.preparation.projet_doctoral.domain.model.proposition import Proposition, PropositionIdentity
from ddd.logic.admission.preparation.projet_doctoral.repository.i_proposition import IPropositionRepository
from ddd.logic.admission.preparation.projet_doctoral.test.factory.proposition import (
    PropositionAdmissionSC3DPAvecMembresFactory,
    PropositionAdmissionSC3DPAvecMembresInvitesFactory,
    PropositionAdmissionSC3DPMinimaleFactory,
)


class PropositionInMemoryRepository(InMemoryGenericRepository, IPropositionRepository):
    entities = []  # type: List[Proposition]

    @classmethod
    def reset(cls):
        cls.entities = [
            PropositionAdmissionSC3DPMinimaleFactory(),
            PropositionAdmissionSC3DPAvecMembresFactory(),
            PropositionAdmissionSC3DPAvecMembresInvitesFactory(),
        ]

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['PropositionIdentity']] = None,
            matricule_candidat: str = None,
            **kwargs
    ) -> List['Proposition']:
        returned = cls.entities
        if matricule_candidat:
            returned = filter(lambda p: p.matricule_candidat == matricule_candidat, returned)
        if entity_ids:
            returned = filter(lambda p: p.entity_id in entity_ids, returned)
        return list(returned)
