##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db.models import F
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.enums.education_group_categories import Categories
from education_group.api.serializers.group_element_year import EducationGroupRootNodeTreeSerializer
from program_management.ddd.domain import link
from program_management.ddd.repositories import load_tree
from program_management.models.element import Element


class EducationGroupTreeView(LanguageContextSerializerMixin, generics.RetrieveAPIView):
    serializer_class = EducationGroupRootNodeTreeSerializer
    filter_backends = []
    paginator = None

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        version_name = self.kwargs.pop('version_name', '')
        filter_kwargs = {
            lookup_field: self.kwargs[lookup_url_kwarg]
            for lookup_field, lookup_url_kwarg in zip(self.lookup_fields, self.lookup_url_kwargs)
        }

        element = get_object_or_404(
            queryset,
            **filter_kwargs,
            group_year__educationgroupversion__version_name=version_name
        )
        self.check_object_permissions(self.request, element.education_group_year_obj)

        tree = load_tree.load(element.id)
        return link.factory.get_link(parent=None, child=tree.root_node)


class TrainingTreeView(EducationGroupTreeView):
    """
        Return the tree of the training
    """
    name = 'trainings_tree'
    lookup_fields = (
        'group_year__academic_year__year', 'group_year__educationgroupversion__offer__acronym__iexact',
    )
    lookup_url_kwargs = ('year', 'acronym')
    queryset = Element.objects.filter(
        group_year__education_group_type__category=Categories.TRAINING.name,
        group_year__educationgroupversion__is_transition=False
    ).annotate(
        education_group_year_obj=F('group_year__educationgroupversion__offer')
    ).select_related('education_group_year')


class MiniTrainingTreeView(EducationGroupTreeView):
    """
        Return the tree of the mini-training
    """
    name = 'minitrainings_tree'
    lookup_fields = ('group_year__academic_year__year', 'group_year__partial_acronym__iexact',)
    lookup_url_kwargs = ('year', 'partial_acronym',)
    queryset = Element.objects.filter(
        group_year__education_group_type__category=Categories.MINI_TRAINING.name,
        group_year__educationgroupversion__is_transition=False
    ).annotate(
        education_group_year_obj=F('group_year__educationgroupversion__offer')
    ).select_related('education_group_year')


class GroupTreeView(EducationGroupTreeView):
    """
        Return the tree of the group
    """
    name = 'groups_tree'
    lookup_fields = ('group_year__academic_year__year', 'group_year__partial_acronym__iexact',)
    lookup_url_kwargs = ('year', 'partial_acronym',)
    queryset = Element.objects.filter(
        group_year__education_group_type__category=Categories.GROUP.name
    ).annotate(
        education_group_year_obj=F('group_year__educationgroupversion__offer')
    ).select_related('education_group_year')
