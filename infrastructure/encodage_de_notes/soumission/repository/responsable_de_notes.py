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
import string
from typing import Optional, List

from django.db.models import F, Q, Value, CharField
from django.db.models.functions import Coalesce, Concat

from assessments.models.score_responsible import ScoreResponsible
from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_class import AttributionClass
from base.models.learning_unit_year import LearningUnitYear
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
                matricule_fgs_enseignant=global_id,
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
        qs_score_responsible = ScoreResponsible.objects.filter(
            Q(attribution_charge__attribution__tutor__person__global_id=entity_id.matricule_fgs_enseignant) |
            Q(
                attribution_class__attribution_charge__attribution__tutor__person__global_id=entity_id.
                matricule_fgs_enseignant
            )
        )
        for score_responsible in qs_score_responsible:
            score_responsible.delete()

    @classmethod
    def save(cls, entity: 'ResponsableDeNotes') -> None:
        if not entity.unites_enseignements:
            cls.delete(entity.entity_id)
            return

        for unite_enseignement in entity.unites_enseignements:
            is_class = unite_enseignement.code_unite_enseignement[-1] in string.ascii_letters
            if is_class:
                luy = LearningUnitYear.objects.get(
                    acronym=unite_enseignement.code_unite_enseignement[:-1],
                    academic_year__year=unite_enseignement.annee_academique
                )
                attribution_class = AttributionClass.objects.get(
                    learning_class_year__acronym=unite_enseignement.code_unite_enseignement[-1],
                    learning_class_year__learning_component_year__learning_unit_year=luy
                )
                ScoreResponsible.objects.update_or_create(
                    learning_unit_year=luy,
                    attribution_class=attribution_class
                )
            else:
                luy = LearningUnitYear.objects.get(
                    acronym=unite_enseignement.code_unite_enseignement,
                    academic_year__year=unite_enseignement.annee_academique
                )
                attribution_charge = AttributionChargeNew.objects.get(learning_component_year__learning_unit_year=luy)
                ScoreResponsible.objects.update_or_create(
                    learning_unit_year=luy,
                    attribution_charge=attribution_charge
                )

        unite_enseignement_filters = functools.reduce(
            operator.or_,
            [
                Q(acronym=identite_ue.code_unite_enseignement, year=identite_ue.annee_academique)
                for identite_ue in entity.unites_enseignements
            ]
        )
        qs_base_score_responsible = ScoreResponsible.objects.annotate(
            acronym=Concat(
                'learning_unit_year__acronym',
                'attribution_class__learning_class_year__acronym',
                output_field=CharField()
            ),
            year=F('learning_unit_year__academic_year__year')
        ).filter(
            Q(attribution_charge__attribution__tutor__person__global_id=entity.entity_id.matricule_fgs_enseignant) |
            Q(
                attribution_class__attribution_charge__attribution__tutor__person__global_id=entity.entity_id.
                matricule_fgs_enseignant
            )
        ).exclude(unite_enseignement_filters)

        for score_responsible in qs_base_score_responsible:
            score_responsible.delete()

    @classmethod
    def get_all_identities(cls) -> List['IdentiteResponsableDeNotes']:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'IdentiteResponsableDeNotes') -> 'ResponsableDeNotes':
        return cls.search([entity_id])[0]


def _fetch_responsable_de_notes():
    return ScoreResponsible.objects.annotate(
        global_id=Coalesce(
            'attribution_charge__attribution__tutor__person__global_id',
            'attribution_class__attribution_charge__attribution__tutor__person__global_id',
            Value('')
        ),
        acronym=Concat(
            'learning_unit_year__acronym',
            'attribution_class__learning_class_year__acronym',
            output_field=CharField()
        ),
        year=F('learning_unit_year__academic_year__year'),
    ).values_list(
        'global_id',
        'acronym',
        'year',
        named=True
    ).order_by(
        'global_id'
    )
