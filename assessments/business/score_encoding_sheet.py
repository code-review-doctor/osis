##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import List, Dict

from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from assessments.business.enrollment_state import get_line_color
from assessments.business.score_encoding_list import sort_encodings
from assessments.models import score_sheet_address
from assessments.models.enums.score_sheet_address_choices import *
from attribution.models import attribution
from base.models import entity as entity_model, entity_version as entity_version, person_address, \
    session_exam_calendar, \
    offer_year_entity
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.models.enums import exam_enrollment_state as enrollment_states
from base.models.enums.organization_type import MAIN
from base.models.enums.person_address_type import PersonAddressType
from base.models.exam_enrollment import justification_label_authorized, get_deadline

OfferYearEntityType = str  # cf. offer_year_entity_type
EntityId = int


def get_score_sheet_address(educ_group_year: 'EducationGroupYear'):
    address = score_sheet_address.get_from_education_group_id(educ_group_year.education_group_id)
    entity_id = None
    if address is None:
        address = educ_group_year.education_group_id
    else:
        if address and not address.customized:
            map_offer_year_entity_type_with_entity_id = _get_map_entity_type_with_entity(educ_group_year)
            entity_id = map_offer_year_entity_type_with_entity_id[address.entity_address_choice]
            ent_version = entity_version.get_last_version(entity_id)
            entity = entity_model.get_by_internal_id(entity_id)
            if not entity:  # Case no address found for this entity
                entity = entity_model.Entity()
            email = address.email
            address = entity
            address.recipient = '{} - {}'.format(ent_version.acronym, ent_version.title)
            address.email = email
    return {'entity_id_selected': entity_id,
            'address': _get_address_as_dict(address)}


def _get_address_as_dict(address):
    field_names = ['recipient', 'location', 'postal_code', 'city', 'country', 'phone', 'fax', 'email']
    if address:
        return {f_name: getattr(address, f_name, '') for f_name in field_names}
    else:
        return {f_name: None for f_name in field_names}


def _get_map_entity_type_with_entity(educ_group_year: 'EducationGroupYear') -> Dict[OfferYearEntityType, EntityId]:
    management_entity = educ_group_year.management_entity
    administration_entity = educ_group_year.administration_entity
    administration_entity_parent_id = None
    if administration_entity:
        version = entity_version.get_last_version(administration_entity)
        administration_entity_parent_id = version.parent_id if version else None
    return {
        ENTITY_MANAGEMENT: management_entity.id,
        ENTITY_MANAGEMENT_PARENT: entity_version.get_last_version(management_entity).parent_id,
        ENTITY_ADMINISTRATION: administration_entity.id if administration_entity else None,
        ENTITY_ADMINISTRATION_PARENT: administration_entity_parent_id,
    }


def get_map_entity_with_entity_type(educ_group_year: 'EducationGroupYear') -> Dict[EntityId, OfferYearEntityType]:
    return {value: key for key, value in _get_map_entity_type_with_entity(educ_group_year).items()}


def _save_address_from_entity(educ_group_year: 'EducationGroupYear', entity_version_id_selected, email):
    entity_id = entity_version.find_by_id(entity_version_id_selected).entity_id
    entity_id_mapped_with_type = get_map_entity_with_entity_type(educ_group_year)
    entity_address_choice = entity_id_mapped_with_type.get(entity_id)
    new_address = score_sheet_address.ScoreSheetAddress(
        education_group=educ_group_year.education_group,
        entity_address_choice=entity_address_choice,
        email=email,
    )
    address = score_sheet_address.get_from_education_group_id(educ_group_year.education_group_id)
    if address:
        new_address.id = address.id
    new_address.save()


def get_entity_version_choices(education_group_year: 'EducationGroupYear') -> List['EntityVersion']:
    entity_ids = [education_group_year.management_entity_id, education_group_year.administration_entity_id]
    cte = EntityVersion.objects.with_children('acronym', 'title', entity_id__in=entity_ids)
    qs = cte.queryset().with_cte(cte).exclude(acronym="UCL").distinct('acronym').order_by('acronym')
    return list(qs)


# TODO :: to refactor inside Osis-protal + osis-common
def scores_sheet_data(exam_enrollments, tutor=None):
    date_format = str(_('date_format'))
    exam_enrollments = sort_encodings(exam_enrollments)
    data = {'tutor_global_id': tutor.person.global_id if tutor else ''}
    now = timezone.now()
    data['publication_date'] = '%s/%s/%s' % (now.day, now.month, now.year)
    data['institution'] = 'Université catholique de Louvain'
    data['link_to_regulation'] = 'https://www.uclouvain.be/enseignement-reglements.html'
    data['justification_legend'] = \
        _('Justification legend: %(justification_label_authorized)s') % \
        {'justification_label_authorized': justification_label_authorized()}

    # Will contain lists of examEnrollments splitted by learningUnitYear
    enrollments_by_learn_unit = _group_by_learning_unit_year_id(
        exam_enrollments)  # {<learning_unit_year_id> : [<ExamEnrollment>]}

    learning_unit_years = []
    for exam_enrollments in enrollments_by_learn_unit.values():
        # exam_enrollments contains all ExamEnrollment for a learningUnitYear
        learn_unit_year_dict = {}
        # We can take the first element of the list 'exam_enrollments' to get the learning_unit_yr
        # because all exam_enrollments have the same learningUnitYear
        learning_unit_yr = exam_enrollments[0].session_exam.learning_unit_year
        scores_responsible = attribution.find_responsible(learning_unit_yr.id)
        scores_responsible_address = None
        person = None
        if scores_responsible:
            person = scores_responsible.person
            scores_responsible_address = person_address.get_by_label(scores_responsible.person,
                                                                     PersonAddressType.PROFESSIONAL.name)

        learn_unit_year_dict['academic_year'] = str(learning_unit_yr.academic_year)

        learn_unit_year_dict['scores_responsible'] = {
            'first_name': person.first_name if person and person.first_name else '',
            'last_name': person.last_name if person and person.last_name else ''}

        learn_unit_year_dict['scores_responsible']['address'] = {'location': scores_responsible_address.location
                                                                 if scores_responsible_address else '',
                                                                 'postal_code': scores_responsible_address.postal_code
                                                                 if scores_responsible_address else '',
                                                                 'city': scores_responsible_address.city
                                                                 if scores_responsible_address else ''}
        learn_unit_year_dict['session_number'] = exam_enrollments[0].session_exam.number_session
        learn_unit_year_dict['acronym'] = learning_unit_yr.acronym
        learn_unit_year_dict['title'] = learning_unit_yr.complete_title
        learn_unit_year_dict['decimal_scores'] = learning_unit_yr.decimal_scores

        programs = []

        # Will contain lists of examEnrollments by offerYear (=Program)
        enrollments_by_program = {}  # {<offer_year_id> : [<ExamEnrollment>]}
        for exam_enroll in exam_enrollments:
            key = exam_enroll.learning_unit_enrollment.offer_enrollment.education_group_year.id
            if key not in enrollments_by_program.keys():
                enrollments_by_program[key] = [exam_enroll]
            else:
                enrollments_by_program[key].append(exam_enroll)

        for list_enrollments in enrollments_by_program.values():  # exam_enrollments by OfferYear
            exam_enrollment = list_enrollments[0]
            educ_group_year = exam_enrollment.learning_unit_enrollment.offer_enrollment.education_group_year
            number_session = exam_enrollment.session_exam.number_session
            deliberation_date = session_exam_calendar.find_deliberation_date(number_session, educ_group_year)
            if deliberation_date:
                deliberation_date = deliberation_date.strftime(date_format)
            else:
                deliberation_date = _('Not passed')

            program = {'acronym': educ_group_year.acronym,
                       'deliberation_date': deliberation_date,
                       'address': _get_serialized_address(educ_group_year)}
            enrollments = []
            for exam_enrol in list_enrollments:
                student = exam_enrol.learning_unit_enrollment.student

                enrollments.append({
                    "registration_id": student.registration_id,
                    "last_name": student.person.last_name,
                    "first_name": student.person.first_name,
                    "score": _format_score(exam_enrol, learning_unit_yr),
                    "justification": _(exam_enrol.get_justification_final_display())
                    if exam_enrol.justification_final else '',
                    "deadline": _get_formatted_deadline(date_format, exam_enrol),
                    "enrollment_state_color": get_line_color(exam_enrol),
                })
            program['enrollments'] = enrollments
            programs.append(program)
            programs = sorted(programs, key=lambda k: k['acronym'])
        learn_unit_year_dict['programs'] = programs
        learning_unit_years.append(learn_unit_year_dict)
    learning_unit_years = sorted(learning_unit_years, key=lambda k: k['acronym'])
    data['learning_unit_years'] = learning_unit_years
    return data


def _get_serialized_address(educ_group_year: 'EducationGroupYear'):
    address = get_score_sheet_address(educ_group_year)['address']
    country = address.get('country')
    address['country'] = country.name if country else ''
    return address


def _group_by_learning_unit_year_id(exam_enrollments):
    """
    :param exam_enrollments: List of examEnrollments to regroup by earningunitYear.id
    :return: A dictionary where the key is LearningUnitYear.id and the value is a list of examEnrollment
    """
    enrollments_by_learn_unit = {}  # {<learning_unit_year_id> : [<ExamEnrollment>]}
    for exam_enroll in exam_enrollments:
        key = exam_enroll.session_exam.learning_unit_year.id
        if key not in enrollments_by_learn_unit.keys():
            enrollments_by_learn_unit[key] = [exam_enroll]
        else:
            enrollments_by_learn_unit[key].append(exam_enroll)
    return enrollments_by_learn_unit


def _get_formatted_deadline(date_format, exam_enrol):
    # Compute deadline score encoding
    if exam_enrol.enrollment_state == enrollment_states.ENROLLED:
        deadline = get_deadline(exam_enrol)
        if deadline:
            return deadline.strftime(date_format)
    return ''


def _format_score(exam_enrol, learning_unit_yr):
    if exam_enrol.score_final is not None:
        if learning_unit_yr.decimal_scores:
            return str(exam_enrol.score_final)
        else:
            return str(int(exam_enrol.score_final))
    return ''
