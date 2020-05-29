import functools
import json
from collections import OrderedDict
from enum import Enum
from typing import List

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base.views.common import display_warning_messages
from education_group.forms import tree_version_choices
from education_group.forms.academic_year_choices import get_academic_year_choices
from program_management.ddd.business_types import *
from education_group.ddd.business_types import *

from base import models as mdl
from education_group.ddd.domain.service.identity_search import TrainingIdentitySearch
from base.business.education_groups import general_information_sections
from base.business.education_groups.general_information_sections import \
    MIN_YEAR_TO_DISPLAY_GENERAL_INFO_AND_ADMISSION_CONDITION
from base.models import academic_year
from base.models.enums.education_group_types import TrainingType
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.domain.node import NodeIdentity, NodeNotFoundException
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch
from program_management.ddd.repositories import load_tree
from program_management.ddd.repositories.load_tree import find_all_versions_academic_year
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element
from program_management.serializers.program_tree_view import program_tree_view_serializer
from program_management.forms.custom_xls import CustomXlsForm


class Tab(Enum):
    IDENTIFICATION = 0
    DIPLOMAS_CERTIFICATES = 1
    ADMINISTRATIVE_DATA = 2
    CONTENT = 3
    UTILIZATION = 4
    GENERAL_INFO = 5
    SKILLS_ACHIEVEMENTS = 6
    ADMISSION_CONDITION = 7


class TrainingRead(PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = 'base.view_educationgroup'
    raise_exception = True
    active_tab = None

    @functools.lru_cache()
    def get_path(self):
        path = self.request.GET.get('path')
        if path is None:
            root_element = Element.objects.get(
                group_year__academic_year__year=self.kwargs['year'],
                group_year__partial_acronym=self.kwargs['code'].upper()
            )
            path = str(root_element.pk)
        return path

    @cached_property
    def node_identity(self) -> 'NodeIdentity':
        return NodeIdentity(code=self.kwargs['code'], year=self.kwargs['year'])

    @cached_property
    def training_identity(self) -> 'TrainingIdentity':
        return TrainingIdentitySearch().get_from_program_tree_version_identity(self.program_tree_version_identity)

    @cached_property
    def program_tree_version_identity(self) -> 'ProgramTreeVersionIdentity':
        return ProgramTreeVersionIdentitySearch().get_from_node_identity(self.node_identity)

    @cached_property
    def current_version(self) -> 'ProgramTreeVersion':
        return ProgramTreeVersionRepository.get(self.program_tree_version_identity)

    @cached_property
    def education_group_version(self):
        root_element_id = self.get_object().pk
        return EducationGroupVersion.objects.select_related(
            'offer__academic_year', 'root_group'
        ).get(root_group__element__pk=root_element_id)

    @functools.lru_cache()
    def get_tree(self):
        root_element_id = self.get_path().split("|")[0]
        return load_tree.load(int(root_element_id))

    @functools.lru_cache()
    def get_object(self) -> 'Node':
        try:
            return self.get_tree().get_node(self.get_path())
        except NodeNotFoundException:
            root_node = self.get_tree().root_node
            message = _(
                "The formation you work with doesn't exist (or is not at the same position) "
                "in the tree {root.title} in {root.year}."
                "You've been redirected to the root {root.code} ({root.year})"
            ).format(root=root_node)
            display_warning_messages(self.request, message)
            return root_node

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "person": self.request.user.person,
            "enums": mdl.enums.education_group_categories,
            "tab_urls": self.get_tab_urls(),
            "node": self.get_object(),
            "tree": json.dumps(program_tree_view_serializer(self.get_tree())),
            "form_xls_custom": CustomXlsForm(path=self.get_path()),
            "academic_year_choices": get_academic_year_choices(
                self.node_identity,
                self.get_path(),
                _get_view_name_from_tab(self.active_tab),
            ),
            "current_version": self.current_version,
            "versions_choices": tree_version_choices.get_tree_versions_choices(self.node_identity),

            # TODO: Two lines below to remove when finished reorganized templates
            "education_group_version": self.education_group_version,
            "group_year": self.education_group_version.root_group,
        }

    @cached_property
    def all_versions_available(self) -> List['ProgramTreeVersion']:
        return ProgramTreeVersionRepository.search_all_versions_from_root_node(
            NodeIdentity(self.get_tree().root_node.code, self.get_tree().root_node.year)
        )

    def get_permission_object(self):
        return self.education_group_version.offer

    def __display_administrative_data_tab(self):
        return not self.get_object().is_master_2m() and self.current_version.is_standard

    def get_tab_urls(self):
        node_identity = self.get_object().entity_id
        return OrderedDict({
            Tab.IDENTIFICATION: {
                'text': _('Identification'),
                'active': Tab.IDENTIFICATION == self.active_tab,
                'display': True,
                'url': _get_tab_urls(Tab.IDENTIFICATION, node_identity, self.get_path()),
            },
            Tab.DIPLOMAS_CERTIFICATES: {
                'text': _('Diplomas /  Certificates'),
                'active': Tab.DIPLOMAS_CERTIFICATES == self.active_tab,
                'display': True,
                'url': _get_tab_urls(Tab.DIPLOMAS_CERTIFICATES, node_identity, self.get_path()),
            },
            Tab.ADMINISTRATIVE_DATA: {
                'text': _('Administrative data'),
                'active': Tab.ADMINISTRATIVE_DATA == self.active_tab,
                'display': self.__display_administrative_data_tab(),
                'url': _get_tab_urls(Tab.ADMINISTRATIVE_DATA, node_identity, self.get_path()),
            },
            Tab.CONTENT: {
                'text': _('Content'),
                'active': Tab.CONTENT == self.active_tab,
                'display': True,
                'url': _get_tab_urls(Tab.CONTENT, node_identity, self.get_path()),
            },
            Tab.UTILIZATION: {
                'text': _('Utilizations'),
                'active': Tab.UTILIZATION == self.active_tab,
                'display': True,
                'url': _get_tab_urls(Tab.UTILIZATION, node_identity, self.get_path()),
            },
            Tab.GENERAL_INFO: {
                'text': _('General informations'),
                'active': Tab.GENERAL_INFO == self.active_tab,
                'display': self._have_general_information_tab(),
                'url': _get_tab_urls(Tab.GENERAL_INFO, node_identity, self.get_path()),
            },
            Tab.SKILLS_ACHIEVEMENTS: {
                'text': capfirst(_('skills and achievements')),
                'active': Tab.SKILLS_ACHIEVEMENTS == self.active_tab,
                'display': self._have_skills_and_achievements_tab(),
                'url': _get_tab_urls(Tab.SKILLS_ACHIEVEMENTS, node_identity, self.get_path()),
            },
            Tab.ADMISSION_CONDITION: {
                'text': _('Conditions'),
                'active': Tab.ADMISSION_CONDITION == self.active_tab,
                'display': self._have_admission_condition_tab(),
                'url': _get_tab_urls(Tab.ADMISSION_CONDITION, node_identity, self.get_path()),
            },
        })

    @functools.lru_cache()
    def get_current_academic_year(self):
        return academic_year.starting_academic_year()

    def _have_general_information_tab(self):
        node_category = self.get_object().category
        return node_category.name in general_information_sections.SECTIONS_PER_OFFER_TYPE and \
            self._is_general_info_and_condition_admission_in_display_range

    def _have_skills_and_achievements_tab(self):
        node_category = self.get_object().category
        return node_category.name in TrainingType.with_skills_achievements() and \
            self._is_general_info_and_condition_admission_in_display_range

    def _have_admission_condition_tab(self):
        node_category = self.get_object().category
        return node_category.name in TrainingType.with_admission_condition() and \
            self._is_general_info_and_condition_admission_in_display_range

    def _is_general_info_and_condition_admission_in_display_range(self):
        return MIN_YEAR_TO_DISPLAY_GENERAL_INFO_AND_ADMISSION_CONDITION <= self.get_object().year < \
               self.get_current_academic_year().year + 2


def _get_view_name_from_tab(tab: Tab):
    return {
        Tab.IDENTIFICATION: 'training_identification',
        Tab.DIPLOMAS_CERTIFICATES: 'training_diplomas',
        Tab.ADMINISTRATIVE_DATA: 'training_administrative_data',
        Tab.CONTENT: 'training_content',
        Tab.UTILIZATION: 'training_utilization',
        Tab.GENERAL_INFO: 'training_general_information',
        Tab.SKILLS_ACHIEVEMENTS: 'training_skills_achievements',
        Tab.ADMISSION_CONDITION: 'training_admission_condition',
    }[tab]


def _get_tab_urls(tab: Tab, node_identity: 'NodeIdentity', path: 'Path' = None) -> str:
    path = path or ""
    return reverse(_get_view_name_from_tab(tab), args=[node_identity.year, node_identity.code]) + "?path={}".format(path)
