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
import functools
import itertools
import operator
from typing import Optional, List

from django.db.models import F, Q

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.auth.roles.tutor import Tutor
from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_builder import ResponsableDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import IdentiteResponsableDeNotes, \
    ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import ResponsableDeNotesFromRepositoryDTO, \
    UniteEnseignementIdentiteFromRepositoryDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd.interface import ApplicationService


class ResponsableDeNotesRepository(IResponsableDeNotesRepository):
    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteResponsableDeNotes']] = None,
            **kwargs
    ) -> List['ResponsableDeNotes']:
        if not entity_ids:
            return []

        filter = {"global_id__in": [str(entity_id.matricule_fgs_enseignant) for entity_id in entity_ids]}

        rows = _fetch_responsable_de_notes().filter(**filter)
        rows_grouped_by_global_id = itertools.groupby(rows, key=lambda row: row.global_id)

        result = []
        for global_id, rows_grouped in rows_grouped_by_global_id:
            dto = ResponsableDeNotesFromRepositoryDTO(
                matricule_fgs_enseignant=int(global_id),
                unites_enseignements=[
                    UniteEnseignementIdentiteFromRepositoryDTO(
                        code_unite_enseignement=row.acronym,
                        annee_academique=row.year
                    )
                    for row in rows_grouped
                ]
            )
            result.append(
                ResponsableDeNotesBuilder().build_from_repository_dto(dto)
            )
        return result

    @classmethod
    def delete(cls, entity_id: 'IdentiteResponsableDeNotes', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'ResponsableDeNotes') -> None:
        for identite_ue in entity.unites_enseignements:
            attribution = AttributionNew.objects.get(
                attributionchargenew__learning_component_year__learning_unit_year__acronym=identite_ue.
                code_unite_enseignement,
                attributionchargenew__learning_component_year__learning_unit_year__academic_year__year=identite_ue.
                annee_academique,
                tutor__person__global_id=entity.entity_id.matricule_fgs_enseignant
            )
            attribution.score_responsible = True
            attribution.save()

    @classmethod
    def get_all_identities(cls) -> List['IdentiteResponsableDeNotes']:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'IdentiteResponsableDeNotes') -> 'ResponsableDeNotes':
        return cls.search([entity_id])[0]


def _fetch_responsable_de_notes():
    return AttributionChargeNew.objects.filter(
        attribution__score_responsible=True
    ).annotate(
        global_id=F('attribution__tutor__person__global_id'),
        acronym=F('learning_component_year__learning_unit_year__acronym'),
        year=F('learning_component_year__learning_unit_year__academic_year__year'),
    ).values_list(
        'global_id',
        'acronym',
        'year',
        named=True
    ).order_by(
        'global_id'
    )
