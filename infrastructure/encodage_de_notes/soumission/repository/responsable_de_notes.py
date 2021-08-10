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
from typing import Optional, List, Tuple

from django.db.models import F, Q, CharField
from django.db.models.functions import Concat

from assessments.models.score_responsible import ScoreResponsible
from base.auth.roles.tutor import Tutor
from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_builder import ResponsableDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model._unite_enseignement_identite import UniteEnseignementIdentite
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import IdentiteFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import IdentiteResponsableDeNotes, \
    ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import EnseignantDTO
from ddd.logic.encodage_des_notes.soumission.dtos import ResponsableDeNotesFromRepositoryDTO, \
    UniteEnseignementIdentiteFromRepositoryDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from learning_unit.models.learning_class_year import LearningClassYear
from osis_common.ddd.interface import ApplicationService


class ResponsableDeNotesRepository(IResponsableDeNotesRepository):
    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteResponsableDeNotes']] = None,
            codes_unites_enseignement: List[str] = None,
            annee_academique: Optional[int] = None,
            feuille_notes_identities: List['IdentiteFeuilleDeNotes'] = None,
            **kwargs
    ) -> List['ResponsableDeNotes']:
        qs = _fetch_responsable_de_notes()

        filter = {}
        if entity_ids:
            filter["global_id__in"] = {str(entity_id.matricule_fgs_enseignant) for entity_id in entity_ids}

        if codes_unites_enseignement:
            filter["acronym__in"] = codes_unites_enseignement

        if annee_academique:
            filter["year"] = annee_academique

        if not filter:
            return []

        rows = qs.filter(**filter)
        rows_grouped_by_global_id = itertools.groupby(rows, key=lambda row: row.global_id)

        return [
            ResponsableDeNotesBuilder.build_from_repository_dto(cls._rows_to_dto(global_id, rows_grouped))
            for global_id, rows_grouped in rows_grouped_by_global_id
        ]

    @classmethod
    def _rows_to_dto(cls, global_id: str, rows_grouped_by_global_id):
        return ResponsableDeNotesFromRepositoryDTO(
            matricule_fgs_enseignant=global_id,
            unites_enseignements=[
                UniteEnseignementIdentiteFromRepositoryDTO(
                    code_unite_enseignement=row.acronym,
                    annee_academique=row.year
                )
                for row in rows_grouped_by_global_id
            ]
        )

    @classmethod
    def delete(cls, entity_id: 'IdentiteResponsableDeNotes', **kwargs: ApplicationService) -> None:
        cls._delete(entity_id)

    @classmethod
    def _delete(
            cls,
            entity_id: 'IdentiteResponsableDeNotes',
            unite_enseignement_to_exclude: List['UniteEnseignementIdentite'] = None
    ):
        unite_enseignement_filters = functools.reduce(
            operator.or_,
            [
                Q(acronym=identite_ue.code_unite_enseignement, year=identite_ue.annee_academique)
                for identite_ue in unite_enseignement_to_exclude
            ]
        ) if unite_enseignement_to_exclude else None
        qs_base_score_responsible = ScoreResponsible.objects.annotate(
            acronym=Concat(
                'learning_unit_year__acronym',
                'learning_class_year__acronym',
                output_field=CharField()
            ),
            year=F('learning_unit_year__academic_year__year')
        ).filter(
            tutor__person__global_id=entity_id.matricule_fgs_enseignant
        )
        if unite_enseignement_filters:
            qs_base_score_responsible = qs_base_score_responsible.exclude(unite_enseignement_filters)

        for score_responsible in qs_base_score_responsible:
            score_responsible.delete()

    @classmethod
    def save(cls, entity: 'ResponsableDeNotes') -> None:
        if not entity.unites_enseignements:
            cls.delete(entity.entity_id)
            return

        for unite_enseignement in entity.unites_enseignements:
            cls._save_for_unite_enseignement(entity.entity_id, unite_enseignement)

        cls._delete(entity.entity_id, unite_enseignement_to_exclude=entity.unites_enseignements)

    @classmethod
    def _save_for_unite_enseignement(
            cls,
            entity_id: 'IdentiteResponsableDeNotes',
            unite_enseignement: 'UniteEnseignementIdentite'
    ):
        is_class = unite_enseignement.code_unite_enseignement[-1] in string.ascii_letters
        tutor = Tutor.objects.get(person__global_id=entity_id.matricule_fgs_enseignant)
        if is_class:
            luy = LearningUnitYear.objects.get(
                acronym=unite_enseignement.code_unite_enseignement[:-1],
                academic_year__year=unite_enseignement.annee_academique
            )
            class_year = LearningClassYear.objects.get(
                acronym=unite_enseignement.code_unite_enseignement[-1],
                learning_component_year__learning_unit_year=luy
            )
        else:
            luy = LearningUnitYear.objects.get(
                acronym=unite_enseignement.code_unite_enseignement,
                academic_year__year=unite_enseignement.annee_academique
            )
            class_year = None
        ScoreResponsible.objects.update_or_create(
            tutor=tutor,
            learning_unit_year=luy,
            learning_class_year=class_year,
        )

    @classmethod
    def get_all_identities(cls) -> List['IdentiteResponsableDeNotes']:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'IdentiteResponsableDeNotes') -> 'ResponsableDeNotes':
        return cls.search([entity_id])[0]

    @classmethod
    def get_for_unite_enseignement(cls, code_unite_enseignement: 'str', annee_academique: int) -> 'ResponsableDeNotes':
        return cls.search(code_unite_enseignement=code_unite_enseignement, annee_academique=annee_academique)[0]

    @classmethod
    def get_detail_enseignant(cls, entity_id: 'IdentiteResponsableDeNotes') -> 'EnseignantDTO':
        detail_enseignant_as_values = ScoreResponsible.objects.filter(
            tutor__person__global_id=entity_id.matricule_fgs_enseignant,
        ).annotate(
            nom=F('tutor__person__last_name'),
            prenom=F('tutor__person__first_name'),
        ).values(
            'nom',
            'prenom',
        ).get()
        return EnseignantDTO(**detail_enseignant_as_values)


def _fetch_responsable_de_notes():
    return ScoreResponsible.objects.annotate(
        global_id=F('tutor__person__global_id'),
        acronym=Concat('learning_unit_year__acronym', 'learning_class_year__acronym', output_field=CharField()),  # FIXME :: quid si learning_class_year__acronym n'existe pas ?
        year=F('learning_unit_year__academic_year__year'),
    ).values_list(
        'global_id',
        'acronym',
        'year',
        named=True
    ).order_by(
        'global_id'
    )
