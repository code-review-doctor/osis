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
from typing import Optional

import attr
from django.utils.translation import gettext_lazy as _

from base.models.utils.utils import ChoiceEnum
from ddd.logic.projet_doctoral.domain.model._detail_projet import DetailProjet
from ddd.logic.projet_doctoral.domain.model._experience_precedente_recherche import (
    ExperiencePrecedenteRecherche,
    aucune_experience_precedente_recherche,
)
from ddd.logic.projet_doctoral.domain.model._financement import (
    Financement,
    financement_non_rempli,
)
from ddd.logic.projet_doctoral.domain.model.doctorat import DoctoratIdentity
from osis_common.ddd import interface


class ChoixStatusProposition(ChoiceEnum):
    CANCELLED = _('CANCELLED')
    IN_PROGRESS = _('IN_PROGRESS')


class ChoixTypeAdmission(ChoiceEnum):
    ADMISSION = _('ADMISSION')
    PRE_ADMISSION = _('PRE_ADMISSION')


@attr.s(frozen=True, slots=True)
class PropositionIdentity(interface.EntityIdentity):
    uuid = attr.ib(type=str)


@attr.s(slots=True, hash=False)
class Proposition(interface.RootEntity):
    entity_id = attr.ib(type=PropositionIdentity)
    type_admission = attr.ib(type=ChoixTypeAdmission)
    doctorat_id = attr.ib(type=DoctoratIdentity)
    matricule_candidat = attr.ib(type=str)
    projet = attr.ib(type=DetailProjet)
    status = attr.ib(type=ChoixStatusProposition, default=ChoixStatusProposition.IN_PROGRESS)
    bureau_CDE = attr.ib(type=Optional[str], default='')  # CDE = Comission Doctorale du domaine Sciences Economique et de Gestion
    financement = attr.ib(type=Financement, default=financement_non_rempli)
    experience_precedente_recherche = attr.ib(
        type=ExperiencePrecedenteRecherche,
        default=aucune_experience_precedente_recherche,
    )

    def est_en_cours(self):
        return self.status == ChoixStatusProposition.IN_PROGRESS
