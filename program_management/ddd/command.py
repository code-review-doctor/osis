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
import uuid
from decimal import Decimal
from typing import Optional, List, Tuple

import attr

from base.models.enums.link_type import LinkTypes
from education_group.ddd import command as education_group_command
from education_group.ddd.command import DecreeName, DomainCode
from osis_common.ddd import interface
from program_management.ddd.domain.link import LinkIdentity


@attr.s(frozen=True, slots=True)
class DetachNodeCommand(interface.CommandRequest):
    path = attr.ib(type=str)
    commit = attr.ib(type=bool)


@attr.s(frozen=True, slots=True)
class CreateProgramTreeSpecificVersionCommand(interface.CommandRequest):
    end_year = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    start_year = attr.ib(type=int)
    transition_name = attr.ib(type=str)
    title_en = attr.ib(type=str)
    title_fr = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class CreateProgramTreeTransitionVersionCommand(interface.CommandRequest):
    end_year = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    start_year = attr.ib(type=int)
    transition_name = attr.ib(type=str)
    title_en = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class ExtendProgramTreeVersionCommand(interface.CommandRequest):
    end_year_of_existence = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    year = attr.ib(type=int)
    transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UpdateProgramTreeVersionCommand(interface.CommandRequest):
    end_year = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    year = attr.ib(type=int)
    transition_name = attr.ib(type=str)
    title_en = attr.ib(type=str)
    title_fr = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class ProlongExistingProgramTreeVersionCommand(interface.CommandRequest):
    end_year = attr.ib(type=int)
    updated_year = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)
    title_en = attr.ib(type=str)
    title_fr = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UpdateTrainingVersionCommand(interface.CommandRequest):
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    year = attr.ib(type=int)
    transition_name = attr.ib(type=str)

    title_en = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    end_year = attr.ib(type=int)
    management_entity_acronym = attr.ib(type=Optional[str])
    teaching_campus_name = attr.ib(type=Optional[str])
    teaching_campus_organization_name = attr.ib(type=Optional[str])
    credits = attr.ib(type=int)
    constraint_type = attr.ib(type=Optional[str])
    min_constraint = attr.ib(type=Optional[int])
    max_constraint = attr.ib(type=Optional[int])
    remark_fr = attr.ib(type=Optional[str])
    remark_en = attr.ib(type=Optional[str])


@attr.s(frozen=True, slots=True)
class UpdateMiniTrainingVersionCommand(interface.CommandRequest):
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    year = attr.ib(type=int)
    transition_name = attr.ib(type=str)

    title_en = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    end_year = attr.ib(type=int)
    management_entity_acronym = attr.ib(type=Optional[str])
    teaching_campus_name = attr.ib(type=Optional[str])
    teaching_campus_organization_name = attr.ib(type=Optional[str])
    credits = attr.ib(type=int)
    constraint_type = attr.ib(type=Optional[str])
    min_constraint = attr.ib(type=Optional[int])
    max_constraint = attr.ib(type=Optional[int])
    remark_fr = attr.ib(type=Optional[str])
    remark_en = attr.ib(type=Optional[str])


@attr.s(frozen=True, slots=True)
class CopyElementCommand(interface.CommandRequest):
    user_id = attr.ib(type=int)
    element_code = attr.ib(type=str)
    element_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CutElementCommand(interface.CommandRequest):
    user_id = attr.ib(type=int)
    element_code = attr.ib(type=str)
    element_year = attr.ib(type=int)
    path_to_detach = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class PasteElementCommand(interface.CommandRequest):
    node_to_paste_code = attr.ib(type=str)
    node_to_paste_year = attr.ib(type=int)
    path_where_to_paste = attr.ib(type='Path')
    access_condition = attr.ib(type=bool, default=False)
    is_mandatory = attr.ib(type=bool, default=True)
    block = attr.ib(type=Optional[int], default=None)
    link_type = attr.ib(type=Optional[LinkTypes], default=None)
    comment = attr.ib(type=str, factory=str)
    comment_english = attr.ib(type=str, factory=str)
    relative_credits = attr.ib(type=Optional[int], default=None)
    path_where_to_detach = attr.ib(type=Optional['Path'], default=None)


@attr.s(frozen=True, slots=True)
class CheckPasteNodeCommand(interface.CommandRequest):
    root_id = attr.ib(type=int)
    node_to_paste_code = attr.ib(type=str)
    node_to_paste_year = attr.ib(type=int)
    path_to_detach = attr.ib(type=str)
    path_to_paste = attr.ib(type=Optional[str])


@attr.s(frozen=True, slots=True)
class OrderUpLinkCommand(interface.CommandRequest):
    path = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class OrderDownLinkCommand(interface.CommandRequest):
    path = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetAllowedChildTypeCommand(interface.CommandRequest):
    category = attr.ib(type=str)
    path_to_paste = attr.ib(type=str, default=None)


@attr.s(frozen=True, slots=True)
class GetDefaultLinkType(interface.CommandRequest):
    path_to_paste = attr.ib(type=str)
    child_code = attr.ib(type=str)
    child_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CreateGroupAndAttachCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    type = attr.ib(type=str)
    abbreviated_title = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    constraint_type = attr.ib(type=str)
    min_constraint = attr.ib(type=str)
    max_constraint = attr.ib(type=str)
    management_entity_acronym = attr.ib(type=str)
    teaching_campus_name = attr.ib(type=str)
    organization_name = attr.ib(type=str)
    remark_fr = attr.ib(type=str)
    remark_en = attr.ib(type=str)
    path_to_paste = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class CreateMiniTrainingAndPasteCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    type = attr.ib(type=str)
    abbreviated_title = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    keywords = attr.ib(type=str)
    status = attr.ib(type=str)
    schedule_type = attr.ib(type=str)
    credits = attr.ib(type=int)
    constraint_type = attr.ib(type=str)
    min_constraint = attr.ib(type=int)
    max_constraint = attr.ib(type=int)
    management_entity_acronym = attr.ib(type=str)
    teaching_campus_name = attr.ib(type=str)
    organization_name = attr.ib(type=str)
    remark_fr = attr.ib(type=str)
    remark_en = attr.ib(type=str)
    start_year = attr.ib(type=int)
    end_year = attr.ib(type=Optional[int])
    path_to_paste = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetLastExistingVersionCommand(interface.CommandRequest):
    version_name = attr.ib(type=str)
    offer_acronym = attr.ib(type=str)
    transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetLastExistingTransitionVersionNameCommand(interface.CommandRequest):
    version_name = attr.ib(type=str)
    offer_acronym = attr.ib(type=str)
    transition_name = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetEndPostponementYearCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetVersionMaxEndYear(interface.CommandRequest):
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetNodeIdentityFromElementId(interface.CommandRequest):
    element_id = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class SearchAllVersionsFromRootNodesCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetProgramTree(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetProgramTreeFromRootElementIdCommand(interface.CommandRequest):
    root_element_id = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class UpdateLinkCommand(interface.CommandRequest):
    parent_node_code = attr.ib(type=str)
    parent_node_year = attr.ib(type=int)

    child_node_code = attr.ib(type=str)
    child_node_year = attr.ib(type=int)

    access_condition = attr.ib(type=bool)
    is_mandatory = attr.ib(type=bool)
    block = attr.ib(type=str)
    link_type = attr.ib(type=str)
    comment = attr.ib(type=str)
    comment_english = attr.ib(type=str)
    relative_credits = attr.ib(type=int)

    @property
    def link_identity(self) -> 'LinkIdentity':
        return LinkIdentity(
            parent_code=self.parent_node_code,
            parent_year=self.parent_node_year,
            child_code=self.child_node_code,
            child_year=self.child_node_year,
        )


@attr.s(frozen=True, slots=True)
class BulkUpdateLinkCommand(interface.CommandRequest):
    working_tree_code = attr.ib(type=str)
    working_tree_year = attr.ib(type=int)

    update_link_cmds = attr.ib(factory=list, type=UpdateLinkCommand)  # type: List['UpdateLinkCommand']


@attr.s(frozen=True, slots=True)
class CreateStandardVersionCommand(interface.CommandRequest):
    offer_acronym = attr.ib(type=str)
    code = attr.ib(type=str)
    start_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class PostponeProgramTreeCommand(interface.CommandRequest):
    from_code = attr.ib(type=str)
    from_year = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class CopyProgramTreeToNextYearCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class PostponeProgramTreeVersionCommand(interface.CommandRequest):
    from_offer_acronym = attr.ib(type=str)
    from_version_name = attr.ib(type=str)
    from_year = attr.ib(type=int)
    from_transition_name = attr.ib(type=str)

    # FIXME :: to remove, the code can be found when converting ProgramTreeVersionIdentity to GroupIdentity
    from_code = attr.ib(type=str, default=None)


@attr.s(frozen=True, slots=True)
class CopyTreeVersionToNextYearCommand(interface.CommandRequest):
    from_year = attr.ib(type=int)
    from_offer_acronym = attr.ib(type=str)
    # FIXME :: to remove, the code can be found when converting ProgramTreeVersionIdentity to GroupIdentity
    from_offer_code = attr.ib(type=str)

    from_version_name = attr.ib(type=str)
    from_transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class CreateAndAttachTrainingCommand(education_group_command.CreateTrainingCommand):
    path_to_paste = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DeleteStandardProgramTreeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteProgramTreeVersionCommand(interface.CommandRequest):
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)
    from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteTrainingWithProgramTreeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)
    from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteTrainingStandardVersionCommand(interface.CommandRequest):
    offer_acronym = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteMiniTrainingWithStandardVersionCommand(interface.CommandRequest):
    mini_training_acronym = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteMiniWithProgramTreeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)
    from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteMiniTrainingWithProgramTreeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)
    from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteProgramTreeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeleteAllProgramTreeCommand(interface.CommandRequest):
    code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DeleteStandardVersionCommand(interface.CommandRequest):
    acronym = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeletePermanentlyTreeVersionCommand(interface.CommandRequest):
    acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DeleteSpecificVersionCommand(interface.CommandRequest):
    acronym = attr.ib(type=str)
    year = attr.ib(type=int)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DeleteNodeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    acronym = attr.ib(type=str)
    node_type = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetProgramTreesFromNodeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetProgramTreeVersionFromNodeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetProgramTreesVersionFromNodeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


# Necessary because 'None' is a correct value that could be used to override the default end date
DO_NOT_OVERRIDE = -1


@attr.s(frozen=True, slots=True)
class DuplicateProgramTree(interface.CommandRequest):
    from_root_code = attr.ib(type=str)
    from_root_year = attr.ib(type=int)
    duplicate_to_transition = attr.ib(type=bool)
    override_end_year_to = attr.ib(type=int, default=DO_NOT_OVERRIDE)
    override_start_year_to = attr.ib(type=int, default=DO_NOT_OVERRIDE)


@attr.s(frozen=True, slots=True)
class DeletePermanentlyTrainingStandardVersionCommand(interface.CommandRequest):
    acronym = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DeletePermanentlyMiniTrainingStandardVersionCommand(interface.CommandRequest):
    acronym = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class PublishProgramTreesVersionUsingNodeCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class PostponeMiniTrainingAndRootGroupModificationWithProgramTreeCommand(interface.CommandRequest):
    abbreviated_title = attr.ib(type=str)
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    status = attr.ib(type=str)
    credits = attr.ib(type=int)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=Optional[str])
    keywords = attr.ib(type=Optional[str])
    management_entity_acronym = attr.ib(type=Optional[str])
    end_year = attr.ib(type=Optional[int])
    teaching_campus_name = attr.ib(type=Optional[str])
    teaching_campus_organization_name = attr.ib(type=Optional[str])
    constraint_type = attr.ib(type=Optional[str])
    min_constraint = attr.ib(type=Optional[int])
    max_constraint = attr.ib(type=Optional[int])
    remark_fr = attr.ib(type=Optional[str])
    remark_en = attr.ib(type=Optional[str])
    organization_name = attr.ib(type=str)
    schedule_type = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class PostponeTrainingAndRootGroupModificationWithProgramTreeCommand(interface.CommandRequest):
    postpone_from_acronym = attr.ib(type=str)
    postpone_from_year = attr.ib(type=int)

    code = attr.ib(type=str)
    status = attr.ib(type=str)
    credits = attr.ib(type=int)
    duration = attr.ib(type=int)
    title_fr = attr.ib(type=str)
    partial_title_fr = attr.ib(type=Optional[str])
    title_en = attr.ib(type=Optional[str])
    partial_title_en = attr.ib(type=Optional[str])
    keywords = attr.ib(type=Optional[str])
    internship_presence = attr.ib(type=Optional[str])
    is_enrollment_enabled = attr.ib(type=Optional[bool])
    has_online_re_registration = attr.ib(type=Optional[bool])
    has_partial_deliberation = attr.ib(type=Optional[bool])
    has_admission_exam = attr.ib(type=Optional[bool])
    has_dissertation = attr.ib(type=Optional[bool])
    produce_university_certificate = attr.ib(type=Optional[bool])
    main_language = attr.ib(type=Optional[str])
    english_activities = attr.ib(type=Optional[str])
    other_language_activities = attr.ib(type=Optional[str])
    internal_comment = attr.ib(type=Optional[str])
    main_domain_code = attr.ib(type=Optional[str])
    main_domain_decree = attr.ib(type=Optional[str])
    secondary_domains = attr.ib(type=Optional[List[Tuple[DecreeName, DomainCode]]])
    isced_domain_code = attr.ib(type=Optional[str])
    management_entity_acronym = attr.ib(type=Optional[str])
    administration_entity_acronym = attr.ib(type=Optional[str])
    end_year = attr.ib(type=Optional[int])
    teaching_campus_name = attr.ib(type=Optional[str])
    teaching_campus_organization_name = attr.ib(type=Optional[str])
    enrollment_campus_name = attr.ib(type=Optional[str])
    enrollment_campus_organization_name = attr.ib(type=Optional[str])
    other_campus_activities = attr.ib(type=Optional[str])
    can_be_funded = attr.ib(type=Optional[bool])
    funding_orientation = attr.ib(type=Optional[str])
    can_be_international_funded = attr.ib(type=Optional[bool])
    international_funding_orientation = attr.ib(type=Optional[str])
    ares_code = attr.ib(type=Optional[int])
    ares_graca = attr.ib(type=Optional[int])
    ares_authorization = attr.ib(type=Optional[int])
    code_inter_cfb = attr.ib(type=Optional[str])
    coefficient = attr.ib(type=Optional[Decimal])
    duration_unit = attr.ib(type=Optional[str])
    leads_to_diploma = attr.ib(type=Optional[bool])
    printing_title = attr.ib(type=Optional[str])
    professional_title = attr.ib(type=Optional[str])
    constraint_type = attr.ib(type=Optional[str])
    min_constraint = attr.ib(type=Optional[int])
    max_constraint = attr.ib(type=Optional[int])
    remark_fr = attr.ib(type=Optional[str])
    remark_en = attr.ib(type=Optional[str])
    organization_name = attr.ib(type=str)
    schedule_type = attr.ib(type=str)
    decree_category = attr.ib(type=str)
    rate_code = attr.ib(type=Optional[str])


@attr.s(frozen=True, slots=True)
class UpdateProgramTreeVersionEndDateCommand(interface.CommandRequest):
    from_offer_acronym = attr.ib(type=str)
    from_version_name = attr.ib(type=str)
    from_year = attr.ib(type=int)
    from_transition_name = attr.ib(type=str)
    end_date = attr.ib(type=Optional[int])


@attr.s(frozen=True, slots=True)
class PostponeGroupVersionCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    postpone_from_year = attr.ib(type=int)

    abbreviated_title = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    constraint_type = attr.ib(type=str)
    min_constraint = attr.ib(type=int)
    max_constraint = attr.ib(type=int)
    management_entity_acronym = attr.ib(type=str)
    teaching_campus_name = attr.ib(type=str)
    organization_name = attr.ib(type=str)
    remark_fr = attr.ib(type=str)
    remark_en = attr.ib(type=str)
    end_year = attr.ib(type=Optional[int])

    from_offer_acronym = attr.ib(type=str)
    from_version_name = attr.ib(type=str)
    from_transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class CheckVersionNameCommand(interface.CommandRequest):
    year = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class CheckTransitionNameCommand(interface.CommandRequest):
    from_year = attr.ib(type=int)
    from_offer_acronym = attr.ib(type=str)
    from_version_name = attr.ib(type=str)
    new_transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class FillProgramTreeVersionContentFromProgramTreeVersionCommand(interface.CommandRequest):
    from_year = attr.ib(type=int)
    from_offer_acronym = attr.ib(type=str)
    from_version_name = attr.ib(type=str)
    from_transition_name = attr.ib(type=str)
    to_year = attr.ib(type=int)
    to_offer_acronym = attr.ib(type=str)
    to_version_name = attr.ib(type=str)
    to_transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class FillProgramTreeContentFromLastYearCommand(interface.CommandRequest):
    to_year = attr.ib(type=int)
    to_code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetProgramTreeVersionCommand(interface.CommandRequest):
    year = attr.ib(type=int)
    acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetProgramTreeVersionOriginCommand(interface.CommandRequest):
    year = attr.ib(type=int)
    offer_acronym = attr.ib(type=str)
    version_name = attr.ib(type=str)
    transition_name = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetReportCommand(interface.CommandRequest):
    from_transaction_id = attr.ib(type=uuid.UUID)


@attr.s(frozen=True, slots=True)
class PostponeProgramTreesUntilNPlus6Command(interface.CommandRequest):
    pass


@attr.s(frozen=True, slots=True)
class PostponeProgramTreeVersionsUntilNPlus6Command(interface.CommandRequest):
    pass


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetContenuGroupementCatalogueCommand(interface.CommandRequest):
    code_formation: str
    code: str
    annee: int


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetUnitesEnseignementContenuesDansProgrammeCommand(interface.CommandRequest):
    code_programme: str
    annee: int
