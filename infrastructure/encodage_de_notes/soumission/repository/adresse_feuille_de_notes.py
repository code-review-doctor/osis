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
import itertools
from typing import List, Optional

from django.db.models import F, Value, Subquery, OuterRef, Case, When, CharField, IntegerField
from django.db.models.functions import Replace, Coalesce

from assessments.models.enums.score_sheet_address_choices import ScoreSheetAddressEntityType
from assessments.models.score_sheet_address import ScoreSheetAddress
from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear
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

        annee_academique = next(entity_id.annee_academique for entity_id in entity_ids)
        return get_addresse_feuille_notes(cohortes, annee_academique)

    @classmethod
    def _convert_row_to_dto(cls, row, flat_entity_hierarchy) -> AdresseFeuilleDeNotesDTO:
        if row['type_entite']:
            entite_data = cls._get_corresponding_entite(row, flat_entity_hierarchy)
            return AdresseFeuilleDeNotesDTO(
                nom_cohorte=row["nom_cohorte"],
                annee_academique=row["annee_academique"],
                type_entite=row["type_entite"],
                destinataire='{} - {}'.format(entite_data['acronym'], entite_data['title']),
                rue_numero=entite_data["entity__location"] or "",
                code_postal=entite_data["entity__postal_code"] or "",
                ville=entite_data["entity__city"] or "",
                pays=entite_data["entity__country__name"] or "",
                telephone=entite_data["entity__phone"] or "",
                fax=entite_data["entity__fax"] or "",
                email=row["email"] or ""
            )
        else:
            return AdresseFeuilleDeNotesDTO(
                nom_cohorte=row["nom_cohorte"],
                annee_academique=row["annee_academique"],
                type_entite="",
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
    def _get_corresponding_entite(cls, row, flat_entity_hierarchy):
        if row['type_entite'] == ScoreSheetAddressEntityType.ENTITY_ADMINISTRATION.value:
            return next(
                entity for entity in flat_entity_hierarchy
                if entity['entity_id'] == int(row['entite_administration'])
            )
        if row['type_entite'] == ScoreSheetAddressEntityType.ENTITY_ADMINISTRATION_PARENT.value:
            return next(
                (entity for entity in flat_entity_hierarchy
                 if entity['entity_id'] != int(row['entite_administration']) and int(row['entite_administration']) in
                 entity['children']),
                dict()
            )
        if row['type_entite'] == ScoreSheetAddressEntityType.ENTITY_MANAGEMENT.value:
            return next(
                entity for entity in flat_entity_hierarchy
                if entity['entity_id'] == int(row['entite_gestion'])
            )
        if row['type_entite'] == ScoreSheetAddressEntityType.ENTITY_MANAGEMENT_PARENT.value:
            return next(
                (entity for entity in flat_entity_hierarchy
                 if entity['entity_id'] != int(row['entite_gestion']) and int(row['entite_gestion']) in
                 entity['children']),
                dict()
            )
        return dict()

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

        try:
            ScoreSheetAddress.objects.get(
                education_group=education_group,
                cohort_name=cohort_name
            ).delete()
        except ScoreSheetAddress.DoesNotExist:
            pass

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

        if entity.type_entite:
            ScoreSheetAddress.objects.update_or_create(
                education_group=education_group,
                cohort_name=cohort_name,
                defaults={
                    "entity_address_choice": entity.type_entite.name,
                    "recipient": "",
                    "location": "",
                    "postal_code": "",
                    "city": "",
                    "country": None,
                    "phone": "",
                    "fax": "",
                    "email": entity.email
                }
            )
        else:
            ScoreSheetAddress.objects.update_or_create(
                education_group=education_group,
                cohort_name=cohort_name,
                defaults={
                    "entity_address_choice": None,
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


def get_addresse_feuille_notes(cohortes: List[str], year: int):
    flat_entity_hierarchy = _get_flat_entity_hierarchy(cohortes, year)

    nom_cohorte_subqs = EducationGroupYear.objects.filter(
        education_group=OuterRef('education_group'),
        academic_year__year=year
    ).exclude(
        acronym__contains="11BA"
    ).values('acronym')
    administration_entity_subqs = EducationGroupYear.objects.filter(
        education_group=OuterRef('education_group'),
        academic_year__year=year
    ).exclude(
        acronym__contains="11BA"
    ).values('administration_entity')
    cohort_administration_entity_subqs = CohortYear.objects.filter(
        education_group_year__education_group=OuterRef('education_group'),
        education_group_year__academic_year__year=year
    ).annotate(
        cohort_administration_entity=Coalesce("administration_entity", "education_group_year__administration_entity")
    ).values('cohort_administration_entity')
    management_entity_subqs = EducationGroupYear.objects.filter(
        education_group=OuterRef('education_group'),
        academic_year__year=year
    ).exclude(
        acronym__contains="11BA"
    ).values('management_entity')
    nom_cohorte_first_year_bachelor_subqs = EducationGroupYear.objects.filter(
        education_group=OuterRef('education_group'),
        academic_year__year=year
    ).annotate(
        nom_cohorte=Replace('acronym', Value('1BA'), Value('11BA'))
    ).values('nom_cohorte')

    first_year_cohort_without_scoresheet_address_subqs = CohortYear.objects.exclude(
        education_group_year__education_group__scoresheetaddress__cohort_name=CohortName.FIRST_YEAR.name
    ).values(
        "education_group_year__education_group"
    )

    qs_1 = ScoreSheetAddress.objects.annotate(
        nom_cohorte=Case(
            When(cohort_name=CohortName.FIRST_YEAR.name, then=Subquery(nom_cohorte_first_year_bachelor_subqs[:1])),
            default=Subquery(nom_cohorte_subqs[:1]),
            output_field=CharField()
        ),
        entite_administration=Case(
            When(cohort_name=CohortName.FIRST_YEAR.name, then=Subquery(cohort_administration_entity_subqs[:1])),
            default=Subquery(administration_entity_subqs[:1]),
            output_field=IntegerField()
        ),
        entite_gestion=Subquery(management_entity_subqs[:1]),
        destinataire=F('recipient'),
        rue_numero=F("location"),
        code_postal=F("postal_code"),
        ville=F("city"),
        pays=F("country__name"),
        telephone=F("phone"),
        type_entite=F('entity_address_choice'),
        annee_academique=Value(year, output_field=IntegerField())
    ).filter(
        nom_cohorte__in=cohortes
    ).values(
        "nom_cohorte",
        "type_entite",
        "destinataire",
        "rue_numero",
        "code_postal",
        "ville",
        "pays",
        "telephone",
        "fax",
        "email",
        "entite_administration",
        "entite_gestion",
        "annee_academique"
    )

    qs_2 = ScoreSheetAddress.objects.filter(
            education_group__in=first_year_cohort_without_scoresheet_address_subqs
        ).annotate(
            nom_cohorte=Subquery(nom_cohorte_first_year_bachelor_subqs[:1], output_field=CharField()),
            entite_administration=Subquery(administration_entity_subqs[:1]),
            entite_gestion=Subquery(management_entity_subqs[:1]),
        ).annotate(
            destinataire=F('recipient'),
            rue_numero=F("location"),
            code_postal=F("postal_code"),
            ville=F("city"),
            pays=F("country__name"),
            telephone=F("phone"),
            type_entite=F('entity_address_choice'),
            annee_academique=Value(year, output_field=IntegerField())
        ).filter(
            nom_cohorte__in=cohortes
        ).values(
            "nom_cohorte",
            "type_entite",
            "destinataire",
            "rue_numero",
            "code_postal",
            "ville",
            "pays",
            "telephone",
            "fax",
            "email",
            "entite_administration",
            "entite_gestion",
            "annee_academique"
        )
    rows = list(itertools.chain(qs_1, qs_2))

    return [AdresseFeuilleDeNotesRepository._convert_row_to_dto(row, flat_entity_hierarchy) for row in rows]


def _get_flat_entity_hierarchy(cohortes: List[str], year: int):
    entity_ids_qs = EducationGroupYear.objects.filter(
        acronym__in=cohortes,
        academic_year__year=year
    ).values_list("administration_entity", "management_entity")
    cohort_entity_ids_qs = CohortYear.objects.filter(
        education_group_year__academic_year__year=year
    ).annotate(
        acronym=Replace('education_group_year__acronym', Value('1BA'), Value('11BA'))
    ).filter(
        acronym__in=cohortes
    ).annotate(
        cohort_administration_entity=Coalesce(
            'administration_entity', 'education_group_year__administration_entity'
        )
    ).values_list("cohort_administration_entity", "education_group_year__management_entity")
    entity_ids = set(itertools.chain.from_iterable(entity_ids_qs)).union(
        itertools.chain.from_iterable(cohort_entity_ids_qs)
    )

    cte = EntityVersion.objects.with_children(
        'acronym',
        'entity_type',
        'title',
        'entity__location',
        'entity__postal_code',
        'entity__city',
        'entity__country__name',
        'entity__phone',
        'entity__fax',
        entity__id__in=entity_ids
    )
    return cte.queryset().with_cte(cte).order_by('acronym')
