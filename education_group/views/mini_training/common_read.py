import functools
import json
from collections import OrderedDict
from enum import Enum

from django.http import Http404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base import models as mdl
from base.business.education_groups import general_information_sections
from base.business.education_groups.general_information_sections import \
    MIN_YEAR_TO_DISPLAY_GENERAL_INFO_AND_ADMISSION_CONDITION
from base.models import academic_year
from base.models.enums.education_group_types import MiniTrainingType
from base.views.common import display_warning_messages
from education_group.forms.academic_year_choices import get_academic_year_choices
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.domain.node import NodeIdentity, NodeNotFoundException
from program_management.ddd.repositories import load_tree
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element
from program_management.serializers.program_tree_view import program_tree_view_serializer


class Tab(Enum):
    IDENTIFICATION = 0
    CONTENT = 1
    UTILIZATION = 2
    GENERAL_INFO = 3
    SKILLS_ACHIEVEMENTS = 4
    ADMISSION_CONDITION = 5


class MiniTrainingRead(PermissionRequiredMixin, TemplateView):
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
                group_year__partial_acronym=self.kwargs['code']
            )
            path = str(root_element.pk)
        return path

    @cached_property
    def node_identity(self) -> 'NodeIdentity':
        return NodeIdentity(code=self.kwargs['code'], year=self.kwargs['year'])

    @functools.lru_cache()
    def get_current_academic_year(self):
        return academic_year.starting_academic_year()

    @functools.lru_cache()
    def get_education_group_version(self):
        try:
            root_element_id = self.get_path().split("|")[0]
            return EducationGroupVersion.objects.select_related(
                'offer', 'root_group'
            ).get(root_group__element__pk=root_element_id)
        except (EducationGroupVersion.DoesNotExist, Element.DoesNotExist):
            raise Http404

    @functools.lru_cache()
    def get_tree(self):
        root_element_id = self.get_path().split("|")[0]
        return load_tree.load(int(root_element_id))

    @functools.lru_cache()
    def get_object(self):
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
            "node": self.get_object(),
            "tab_urls": self.get_tab_urls(),
            "tree": json.dumps(program_tree_view_serializer(self.get_tree())),
            "education_group_version": self.get_education_group_version(),
            "academic_year_choices": get_academic_year_choices(
                self.node_identity,
                self.get_path(),
                _get_view_name_from_tab(self.active_tab),
            ),
            # TODO: Remove when finished reoganized tempalate
            "group_year": self.get_education_group_version().root_group
        }

    def get_permission_object(self):
        return self.get_education_group_version().offer

    def get_tab_urls(self):
        return OrderedDict({
            Tab.IDENTIFICATION: {
                'text': _('Identification'),
                'active': Tab.IDENTIFICATION == self.active_tab,
                'display': True,
                'url': _get_tab_urls(Tab.IDENTIFICATION, self.node_identity, self.get_path()),
            },
            Tab.CONTENT: {
                'text': _('Content'),
                'active': Tab.CONTENT == self.active_tab,
                'display': True,
                'url': _get_tab_urls(Tab.CONTENT, self.node_identity, self.get_path()),
            },
            Tab.UTILIZATION: {
                'text': _('Utilizations'),
                'active': Tab.UTILIZATION == self.active_tab,
                'display': True,
                'url': _get_tab_urls(Tab.UTILIZATION, self.node_identity, self.get_path()),
            },
            Tab.GENERAL_INFO: {
                'text': _('General informations'),
                'active': Tab.GENERAL_INFO == self.active_tab,
                'display': self._have_general_information_tab(),
                'url': _get_tab_urls(Tab.GENERAL_INFO, self.node_identity, self.get_path()),
            },
            Tab.SKILLS_ACHIEVEMENTS: {
                'text': capfirst(_('skills and achievements')),
                'active': Tab.SKILLS_ACHIEVEMENTS == self.active_tab,
                'display': self._have_skills_and_achievements_tab(),
                'url': _get_tab_urls(Tab.SKILLS_ACHIEVEMENTS, self.node_identity, self.get_path()),
            },
            Tab.ADMISSION_CONDITION: {
                'text': _('Conditions'),
                'active': Tab.ADMISSION_CONDITION == self.active_tab,
                'display': self._have_admission_condition_tab(),
                'url': _get_tab_urls(Tab.ADMISSION_CONDITION, self.node_identity, self.get_path()),
            },
        })

    def _have_general_information_tab(self):
        node_category = self.get_object().category
        return node_category.name in general_information_sections.SECTIONS_PER_OFFER_TYPE and \
            self._is_general_info_and_condition_admission_in_display_range

    def _have_skills_and_achievements_tab(self):
        node_category = self.get_object().category
        return node_category.name in MiniTrainingType.with_skills_achievements() and \
            self._is_general_info_and_condition_admission_in_display_range

    def _have_admission_condition_tab(self):
        node_category = self.get_object().category
        return node_category.name in MiniTrainingType.with_admission_condition() and \
            self._is_general_info_and_condition_admission_in_display_range

    def _is_general_info_and_condition_admission_in_display_range(self):
        return MIN_YEAR_TO_DISPLAY_GENERAL_INFO_AND_ADMISSION_CONDITION <= self.get_object().year < \
               self.get_current_academic_year().year + 2


def _get_view_name_from_tab(tab: Tab):
    return {
        Tab.IDENTIFICATION: 'mini_training_identification',
        Tab.CONTENT: 'mini_training_content',
        Tab.UTILIZATION: 'mini_training_utilization',
        Tab.GENERAL_INFO: 'mini_training_general_information',
        Tab.SKILLS_ACHIEVEMENTS: 'mini_training_skills_achievements',
        Tab.ADMISSION_CONDITION: 'mini_training_admission_condition',
    }[tab]


def _get_tab_urls(tab: Tab, node_identity: 'NodeIdentity', path: 'Path' = None) -> str:
    path = path or ""
    return reverse(
        _get_view_name_from_tab(tab),
        args=[node_identity.year, node_identity.code]
    ) + "?path={}".format(path)
