##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from base.models.enums import link_type
from base.models.enums.proposal_type import ProposalType
from program_management.ddd.business_types import *
from program_management.models.enums.node_type import NodeType


class ChildrenField(serializers.Serializer):
    def to_representation(self, value: 'Link'):
        context = {
            **self.context,
            'path': "|".join([self.context['path'], str(value.child.pk)])
        }
        if value.child.type == NodeType.LEARNING_UNIT:
            return LeafViewSerializer(value, context=context).data
        return NodeViewSerializer(value, context=context).data


class NodeViewAttributeSerializer(serializers.Serializer):
    href = serializers.SerializerMethodField()
    root = serializers.SerializerMethodField()
    group_element_year = serializers.IntegerField(source='pk')  # TODO :: rename this arg (impact javascript)
    element_id = serializers.IntegerField(source='child.pk')
    element_type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    attach_url = serializers.SerializerMethodField()
    detach_url = serializers.SerializerMethodField()
    modify_url = serializers.SerializerMethodField()
    attach_disabled = serializers.BooleanField(default=False)  # TODO : To implement in OSIS-3954
    attach_msg = serializers.CharField(default=None)  # TODO : To implement in OSIS-3954
    detach_disabled = serializers.BooleanField(default=False)  # TODO : To implement in OSIS-3954
    detach_msg = serializers.CharField(default=None)  # TODO : To implement in OSIS-3954
    modification_disabled = serializers.BooleanField(default=False)  # TODO : To implement in OSIS-3954
    modification_msg = serializers.CharField(default=None)  # TODO : To implement in OSIS-3954
    search_url = serializers.SerializerMethodField()

    def get_element_type(self, obj: 'Link'):
        return obj.child.type.name

    def get_root(self, obj: 'Link'):
        return self.context['root'].pk

    def get_title(self, obj: 'Link'):
        return obj.child.code

    def get_href(self, obj: 'Link'):
        # TODO: add table_to_show....
        return reverse('education_group_read', args=[self.get_root(obj), obj.child.pk])

    def get_attach_url(self, obj: 'Link'):
        return reverse('education_group_attach', args=[self.get_root(obj), obj.child.pk])

    def get_detach_url(self, obj: 'Link'):
        return reverse('group_element_year_delete', args=[
            self.get_root(obj), obj.child.pk, obj.pk
        ])

    def get_modify_url(self, obj: 'Link'):
        return reverse('group_element_year_update', args=[
            self.get_root(obj), obj.child.pk, obj.pk
        ])

    def get_search_url(self, obj: 'Link'):
        # if attach.can_attach_learning_units(self.education_group_year):  # TODO :: to implement in OSIS-3954
        #     return reverse('quick_search_learning_unit', args=[self.root.pk, self.education_group_year.pk])
        return reverse('quick_search_education_group', args=[self.get_root(obj), obj.child.pk])


class LeafViewAttributeSerializer(NodeViewAttributeSerializer):
    has_prerequisite = serializers.BooleanField(source='child.has_prerequisite')
    is_prerequisite = serializers.BooleanField(source='child.is_prerequisite')
    css_class = serializers.SerializerMethodField()

    def get_href(self, obj: 'Link'):
        # TODO: add table_to_show....
        return reverse('learning_unit_utilization', args=[self.get_root(obj), obj.child.pk])

    def get_element_type(self, obj):
        return NodeType.LEARNING_UNIT.name

    def get_title(self, obj: 'Link'):
        title = obj.child.title
        if obj.child.has_prerequisite and obj.child.is_prerequisite:
            title = "%s\n%s" % (title, _("The learning unit has prerequisites and is a prerequisite"))
        elif obj.child.has_prerequisite:
            title = "%s\n%s" % (title, _("The learning unit has prerequisites"))
        elif obj.child.is_prerequisite:
            title = "%s\n%s" % (title, _("The learning unit is a prerequisite"))
        return title

    def get_css_class(self, obj: 'Link'):
        return {
            ProposalType.CREATION.name: "proposal proposal_creation",
            ProposalType.MODIFICATION.name: "proposal proposal_modification",
            ProposalType.TRANSFORMATION.name: "proposal proposal_transformation",
            ProposalType.TRANSFORMATION_AND_MODIFICATION.name: "proposal proposal_transformation_modification",
            ProposalType.SUPPRESSION.name: "proposal proposal_suppression"
        }.get(obj.child.proposal_type) or ""


class CommonNodeViewSerializer(serializers.Serializer):
    path = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    def get_path(self, obj: 'Link'):
        return self.context['path']

    def get_icon(self, obj: 'Link'):
        return None


class NodeViewSerializer(CommonNodeViewSerializer):
    text = serializers.SerializerMethodField()
    children = ChildrenField(source='child.children', many=True)
    a_attr = NodeViewAttributeSerializer(source='*')

    def get_icon(self, obj: 'Link'):
        if obj.link_type == link_type.LinkTypes.REFERENCE.name:
            return static('img/reference.jpg')
        return None

    def get_text(self, obj: 'Link'):
        return '%(code)s - %(title)s' % {'code': obj.child.code, 'title': obj.child.title}


class LeafViewSerializer(CommonNodeViewSerializer):
    text = serializers.SerializerMethodField()
    a_attr = LeafViewAttributeSerializer(source='*')

    def get_text(self, obj: 'Link'):
        text = obj.child.code
        if self.context['root'].year != obj.child.year:
            text += '|{}'.format(obj.child.year)
        return text

    def get_icon(self, obj: 'Link'):
        if obj.child.has_prerequisite and obj.child.is_prerequisite:
            return "fa fa-exchange-alt"
        elif obj.child.has_prerequisite:
            return "fa fa-arrow-left"
        elif obj.child.is_prerequisite:
            return "fa fa-arrow-right"
        return "far fa-file"
