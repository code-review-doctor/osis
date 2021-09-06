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
import datetime
from typing import List, Optional

from django.db.models import F, Value, Subquery, OuterRef, Case, When, CharField, Q
from django.db.models.functions import Replace

from assessments.models.score_sheet_address import ScoreSheetAddress
from base.models.academic_year import current_academic_year
from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear
from base.models.entity import Entity
from base.models.entity_version import EntityVersion
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_builder import \
    AdresseFeuilleDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import \
    IdentiteAdresseFeuilleDeNotes, \
    AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from education_group.models.cohort_year import CohortYear
from education_group.models.enums.cohort_name import CohortName
from osis_common.ddd.interface import ApplicationService
from reference.models.country import Country


class AdresseFeuilleDeNotesRepository(IAdresseFeuilleDeNotesRepository):
    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteAdresseFeuilleDeNotes']] = None,
            **kwargs
    ) -> List['AdresseFeuilleDeNotes']:
        dtos = cls.search_dtos(entity_ids, **kwargs)

        builder = AdresseFeuilleDeNotesBuilder()
        return [builder.build_from_repository_dto(dto) for dto in dtos]

    @classmethod
    def search_dtos(
            cls,
            entity_ids: Optional[List['IdentiteAdresseFeuilleDeNotes']] = None,
            **kwargs
    ) -> List['AdresseFeuilleDeNotesDTO']:
        cohortes = [entity_id.nom_cohorte for entity_id in entity_ids]
        if not cohortes:
            return []
        rows = get_queryset(cohortes)

        return [cls._convert_row_to_dto(row) for row in rows]

    @classmethod
    def _convert_row_to_dto(cls, row) -> AdresseFeuilleDeNotesDTO:
        return AdresseFeuilleDeNotesDTO(
            nom_cohorte=row["nom_cohorte"],
            entite=row["entite"] or "",
            destinataire=row["destinataire"] or "",
            rue_numero=row["rue_numero"] or "",
            code_postal=row["code_postal"] or "",
            ville=row["ville"] or "",
            pays=row["pays"] or "",
            telephone=row["telephone"] or "",
            fax=row["fax"] or "",
            email=row["email"] or ""
        )

    @classmethod
    def delete(cls, entity_id: 'IdentiteAdresseFeuilleDeNotes', **kwargs: ApplicationService) -> None:
        if "11BA" in entity_id.nom_cohorte:
            cohort_name = CohortName.FIRST_YEAR.name
            education_group = EducationGroup.objects.filter(
                educationgroupyear__acronym=entity_id.nom_cohorte.replace('11BA', '1BA')
            ).first()
        else:
            cohort_name = None
            education_group = EducationGroup.objects.filter(
                educationgroupyear__acronym=entity_id.nom_cohorte
            ).first()

        ScoreSheetAddress.objects.get(
            education_group=education_group,
            cohort_name=cohort_name
        ).delete()

    @classmethod
    def save(cls, entity: 'AdresseFeuilleDeNotes') -> None:
        if "11BA" in entity.nom_cohorte:
            cohort_name = CohortName.FIRST_YEAR.name
            education_group = EducationGroup.objects.filter(
                educationgroupyear__acronym=entity.nom_cohorte.replace('11BA', '1BA')
            ).first()
        else:
            cohort_name = None
            education_group = EducationGroup.objects.filter(
                educationgroupyear__acronym=entity.nom_cohorte
            ).first()

        entity_db = Entity.objects.get(entityversion__acronym=entity.sigle_entite) if entity.sigle_entite else None
        ScoreSheetAddress.objects.update_or_create(
            education_group=education_group,
            cohort_name=cohort_name,
            defaults={
                "entity_address_choice": None,
                "entity": entity_db,
                "recipient": entity.destinataire,
                "location": entity.rue_numero,
                "postal_code": entity.code_postal,
                "city": entity.ville,
                "country": Country.objects.get(name=entity.pays) if entity.pays else None,
                "phone": entity.telephone,
                "fax": entity.fax,
                "email": entity.email
            }
        )

    @classmethod
    def get_all_identities(cls) -> List['IdentiteAdresseFeuilleDeNotes']:
        pass

    @classmethod
    def get(cls, entity_id: 'IdentiteAdresseFeuilleDeNotes') -> 'AdresseFeuilleDeNotes':
        return cls.search([entity_id])[0]


def get_queryset(cohortes: List[str]):
    nom_cohorte_subqs = EducationGroupYear.objects.filter(
        education_group=OuterRef('education_group'),
        academic_year=current_academic_year()
    ).exclude(
        acronym__contains="11BA"
    ).values('acronym')
    nom_cohorte_first_year_bachelor_subqs = EducationGroupYear.objects.filter(
        education_group=OuterRef('education_group'),
        academic_year=current_academic_year()
    ).annotate(
        nom_cohorte=Replace('acronym', Value('1BA'), Value('11BA'))
    ).values('nom_cohorte')

    date = datetime.date.today()
    entity_acronym_subqs = EntityVersion.objects.filter(
        Q(end_date__gte=date) | Q(end_date__isnull=True),
        start_date__lte=date,
        entity=OuterRef('entity'),
    ).values('acronym')
    entity_title_subqs = EntityVersion.objects.filter(
        Q(end_date__gte=date) | Q(end_date__isnull=True),
        start_date__lte=date,
        entity=OuterRef('entity'),
        ).values('title')

    first_year_cohort_without_scoresheet_address_subqs = CohortYear.objects.exclude(
        education_group_year__education_group__scoresheetaddress__cohort_name=CohortName.FIRST_YEAR.name
    ).values(
        "education_group_year__education_group"
    )

    return ScoreSheetAddress.objects.annotate(
        entite=Subquery(entity_acronym_subqs[:1]),
        entite_intitule=Subquery(entity_title_subqs[:1])
    ).annotate(
        nom_cohorte=Case(
            When(cohort_name=CohortName.FIRST_YEAR.name, then=Subquery(nom_cohorte_first_year_bachelor_subqs[:1])),
            default=Subquery(nom_cohorte_subqs[:1]),
            output_field=CharField()
        ),
        destinataire=F('recipient'),
        rue_numero=F("location"),
        code_postal=F("postal_code"),
        ville=F("city"),
        pays=F("country__name"),
        telephone=F("phone"),
    ).filter(
        nom_cohorte__in=cohortes
    ).values(
        "nom_cohorte",
        "entite",
        "destinataire",
        "rue_numero",
        "code_postal",
        "ville",
        "pays",
        "telephone",
        "fax",
        "email",
    ).union(
        ScoreSheetAddress.objects.filter(
            education_group__in=first_year_cohort_without_scoresheet_address_subqs
        ).annotate(
            entite=Subquery(entity_acronym_subqs[:1]),
            entite_intitule=Subquery(entity_title_subqs[:1]),
            nom_cohorte=Subquery(nom_cohorte_first_year_bachelor_subqs[:1], output_field=CharField()),
        ).annotate(
            destinataire=F('recipient'),
            rue_numero=F("location"),
            code_postal=F("postal_code"),
            ville=F("city"),
            pays=F("country__name"),
            telephone=F("phone"),
        ).filter(
            nom_cohorte__in=cohortes
        ).values(
            "nom_cohorte",
            "entite",
            "destinataire",
            "rue_numero",
            "code_postal",
            "ville",
            "pays",
            "telephone",
            "fax",
            "email",
        )
    )
