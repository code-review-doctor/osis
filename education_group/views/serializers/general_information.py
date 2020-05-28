from typing import List

from django.conf import settings
from django.db.models import OuterRef, Subquery, fields, F

from base.business.education_groups import general_information_sections
from base.models.education_group_publication_contact import EducationGroupPublicationContact
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import GroupType
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from education_group.models.group_year import GroupYear
from program_management.ddd.domain.node import NodeGroupYear


def get_sections_of_common(year: int, language_code: str):
    reference_pk = EducationGroupYear.objects.get_common(academic_year__year=year).pk
    labels = general_information_sections.SECTIONS_PER_OFFER_TYPE['common']['specific']

    translated_labels = __get_translated_labels(reference_pk, labels, language_code)
    sections = {}
    for section in general_information_sections.SECTION_LIST:
        for label in filter(lambda l: l in labels, section.labels):
            translated_label = translated_labels.get(label)
            sections.setdefault(section.title, []).append(translated_label)
    return sections


def get_sections(node: NodeGroupYear, language_code: str):
    translated_labels = __get_specific_translated_labels(node, language_code)
    common_translated_labels = __get_common_translated_labels(node, language_code)
    labels = set(__get_common_labels(node) + __get_specific_labels(node))

    sections = {}
    for section in general_information_sections.SECTION_LIST:
        for label in filter(lambda l: l in labels, section.labels):
            common_translated_label = common_translated_labels.get(label)
            translated_label = translated_labels.get(label)

            if common_translated_label:
                common_translated_label['common_label'] = True
                sections.setdefault(section.title, []).append(common_translated_label)
            if translated_label:
                sections.setdefault(section.title, []).append(translated_label)
    return sections


def __get_specific_translated_labels(node: NodeGroupYear, language_code: str):
    labels = __get_specific_labels(node)
    reference_pk = __get_reference_pk(node)

    return __get_translated_labels(reference_pk, labels, language_code)


def __get_reference_pk(node: NodeGroupYear):
    if node.category.name in GroupType.get_names():
        return GroupYear.objects.get(element__pk=node.pk).pk
    else:
        return EducationGroupYear.objects.get(educationgroupversion__root_group__element__pk=node.pk).pk


def __get_specific_labels(node: NodeGroupYear) -> List[str]:
    return general_information_sections.SECTIONS_PER_OFFER_TYPE[node.category.name]['specific']


def __get_common_translated_labels(node: NodeGroupYear, language_code: str):
    labels = __get_common_labels(node)
    try:
        reference_pk = EducationGroupYear.objects.get_common(academic_year__year=node.year).pk
        translated_labels = __get_translated_labels(reference_pk, labels, language_code)
    except EducationGroupYear.DoesNotExist:
        translated_labels = {}
    return translated_labels


def __get_common_labels(node: NodeGroupYear) -> List[str]:
    return general_information_sections.SECTIONS_PER_OFFER_TYPE[node.category.name]['common']


def __get_translated_labels(reference_pk: int, labels: List[str], language_code: str):
    subqstranslated_fr = TranslatedText.objects.filter(reference=reference_pk, text_label=OuterRef('pk'),
                                                       language=settings.LANGUAGE_CODE_FR).values('text')[:1]
    subqstranslated_en = TranslatedText.objects.filter(reference=reference_pk, text_label=OuterRef('pk'),
                                                       language=settings.LANGUAGE_CODE_EN).values('text')[:1]
    subqslabel = TranslatedTextLabel.objects.filter(
        text_label=OuterRef('pk'),
        language=language_code
    ).values('label')[:1]

    qs = TextLabel.objects.filter(
        label__in=labels
    ).annotate(
        label_id=F('label'),
        label_translated=Subquery(subqslabel, output_field=fields.CharField()),
        text_fr=Subquery(subqstranslated_fr, output_field=fields.CharField()),
        text_en=Subquery(subqstranslated_en, output_field=fields.CharField())
    ).values('label_id', 'label_translated', 'text_fr', 'text_en')

    return {label['label_id']: label for label in qs}


def get_contacts(node: NodeGroupYear):
    qs = EducationGroupPublicationContact.objects.filter(
        education_group_year__educationgroupversion__root_group__element__pk=node.pk
    )
    contacts_by_type = {}
    for publication_contact in qs:
        contact_formated = __get_contact_formated(publication_contact)
        contacts_by_type.setdefault(publication_contact.type, []).append(contact_formated)
    return contacts_by_type


def __get_contact_formated(publication_contact):
    return {
        "pk": publication_contact.pk,
        "email": publication_contact.email,
        "description": publication_contact.description,
        "role_fr": publication_contact.role_fr,
        "role_en": publication_contact.role_en,
    }
