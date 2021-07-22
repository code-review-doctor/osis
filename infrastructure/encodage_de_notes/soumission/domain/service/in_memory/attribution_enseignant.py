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
from typing import Set

from django.db.models import F

from attribution.models.attribution_class import AttributionClass
from attribution.models.attribution_new import AttributionNew
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO


class AttributionEnseignantTranslatorInMemory(IAttributionEnseignantTranslator):

    attributions_dtos = {
        AttributionEnseignantDTO(
            code_unite_enseignement="LDROI1001",
            annee=2020,
            nom="Smith",
            prenom="Charles",
        ),
        AttributionEnseignantDTO(
            code_unite_enseignement="LDROI1001",
            annee=2020,
            nom="Jolypas",
            prenom="Michelle",
        ),
    }  # type: Set[AttributionEnseignantDTO]

    @classmethod
    def search_attributions_enseignant(
            cls,
            code_unite_enseignement: str,
            annee: int,
    ) -> Set['AttributionEnseignantDTO']:
        return set(
            filter(
                lambda dto: dto.code_unite_enseignement == code_unite_enseignement and dto.annee == annee,
                cls.attributions_dtos,
            )
        )
