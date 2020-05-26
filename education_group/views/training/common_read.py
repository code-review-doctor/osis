import functools
import json
from collections import OrderedDict
from enum import Enum

from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base import models as mdl
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.repositories import load_tree
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element
from program_management.serializers.program_tree_view import program_tree_view_serializer
from program_management.forms.custom_xls import CustomXlsForm

from program_management.ddd.business_types import *


class Tab(Enum):
    IDENTIFICATION = 0
    DIPLOMAS_CERTIFICATES = 1
    CONTENT = 2
    UTILIZATION = 3
    GENERAL_INFO = 4
    SKILLS_ACHIEVEMENTS = 5
    ADMISSION_CONDITION = 6


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
    def education_group_version(self):
        root_element_id = self.get_path().split("|")[-1]
        return EducationGroupVersion.objects.select_related(
            'offer__academic_year', 'root_group'
        ).get(root_group__element__pk=root_element_id)

    @functools.lru_cache()
    def get_tree(self):
        root_element_id = self.get_path().split("|")[0]
        return load_tree.load(int(root_element_id))

    def get_object(self) -> 'Node':
        return self.get_tree().get_node(self.get_path())

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "person": self.request.user.person,
            "enums": mdl.enums.education_group_categories,
            "tab_urls": self.get_tab_urls(),
            "node": self.get_object(),
            "tree": json.dumps(program_tree_view_serializer(self.get_tree())),
            "education_group_version": self.education_group_version,
            # TODO: Remove when finished reoganized tempalate
            "group_year": self.education_group_version.root_group,
            "form_xls_custom": CustomXlsForm(path=self.get_path()),
        }

    def get_permission_object(self):
        return self.education_group_version.offer

    def get_tab_urls(self):
        node = self.get_object()
        return OrderedDict({
            Tab.IDENTIFICATION: {
                'text': _('Identification'),
                'active': Tab.IDENTIFICATION == self.active_tab,
                'display': True,
                'url': reverse('training_identification', args=[node.year, node.code]) +
                "?path={}".format(self.get_path())
            },
            Tab.DIPLOMAS_CERTIFICATES: {
                'text': _('Diplomas /  Certificates'),
                'active': Tab.DIPLOMAS_CERTIFICATES == self.active_tab,
                'display': True,
                'url': reverse('training_diplomas', args=[node.year, node.code]) + "?path={}".format(self.get_path())
            },
            Tab.CONTENT: {
                'text': _('Content'),
                'active': Tab.CONTENT == self.active_tab,
                'display': True,
                'url': reverse('training_content', args=[node.year, node.code]) + "?path={}".format(self.get_path())
            },
            Tab.UTILIZATION: {
                'text': _('Utilizations'),
                'active': Tab.UTILIZATION == self.active_tab,
                'display': True,
                'url': reverse('training_utilization', args=[node.year, node.code]) +
                "?path={}".format(self.get_path()),
            },
            Tab.GENERAL_INFO: {
                'text': _('General informations'),
                'active': Tab.GENERAL_INFO == self.active_tab,
                'display': True,
                'url': reverse('training_general_information', args=[node.year, node.code]) +
                "?path={}".format(self.get_path()),
            },
            Tab.SKILLS_ACHIEVEMENTS: {
                'text': capfirst(_('skills and achievements')),
                'active': Tab.SKILLS_ACHIEVEMENTS == self.active_tab,
                'display': True,
                'url': reverse('training_skills_achievements', args=[node.year, node.code]) +
                "?path={}".format(self.get_path()),
            },
            Tab.ADMISSION_CONDITION: {
                'text': _('Conditions'),
                'active': Tab.ADMISSION_CONDITION == self.active_tab,
                'display': True,
                'url': reverse('training_admission_condition', args=[node.year, node.code]) +
                "?path={}".format(self.get_path()),
            },
        })
