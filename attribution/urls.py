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
from django.conf.urls import url, include

from attribution.views.attribution import LearningUnitAttributions
from attribution.views.charge_repartition.create import SelectAttributionView, AddChargeRepartition
from attribution.views.charge_repartition.update import EditChargeRepartition
from attribution.views.learning_unit.create import CreateAttribution
from attribution.views.learning_unit.delete import DeleteAttribution
from attribution.views.learning_unit.update import UpdateAttributionView
from attribution.views.manage_my_courses.edit_my_educational_information import \
    EditMyEducationalInformationForceMajeure, EditMyEducationalInformation
from attribution.views.manage_my_courses.my_attributions_summary_editable import MyAttributionsSummaryEditable
from attribution.views.manage_my_courses.my_educational_information import EducationalInformation
from attribution.views.manage_my_courses.my_teaching_material import UpdateMyTeachingMaterial, \
    CreateMyTeachingMaterial, DeleteMyTeachingMaterial

urlpatterns = [
    url(r'^manage_my_courses/', include([
        url(r'^$', MyAttributionsSummaryEditable.as_view(),
            name='list_my_attributions_summary_editable'),
        url(r'^(?P<learning_unit_year_id>[0-9]+)/', include([
            url(r'^educational_information/$', EducationalInformation.as_view(),
                name='view_educational_information'),
            url(r'^edit_educational_information/$',
                EditMyEducationalInformation.as_view(),
                name='tutor_edit_educational_information'),
            url(r'^edit_educational_information_force_majeure/$',
                EditMyEducationalInformationForceMajeure.as_view(),
                name='tutor_edit_educational_information_force_majeure'),
            url(r'^teaching_materials/', include([
                url(r'^create', CreateMyTeachingMaterial.as_view(), name="tutor_teaching_material_create"),
                url(r'^(?P<teaching_material_id>[0-9]+)/edit/', UpdateMyTeachingMaterial.as_view(),
                    name="tutor_teaching_material_edit"),
                url(r'^(?P<teaching_material_id>[0-9]+)/delete/', DeleteMyTeachingMaterial.as_view(),
                    name="tutor_teaching_material_delete")
            ])),
        ]))
    ])),
    url(r'^(?P<learning_unit_year_id>[0-9]+)/attributions/', include([
        url(r'^$', LearningUnitAttributions.as_view(),
            name="learning_unit_attributions"),
        url(r'^select/$', SelectAttributionView.as_view(), name="select_attribution"),
        url(r'^update/(?P<attribution_id>[0-9]+)/$', UpdateAttributionView.as_view(),
            name="update_attribution"),
        url(r'^create/$', CreateAttribution.as_view(),
            name="add_attribution"),
        url(r'^remove/(?P<attribution_id>[0-9]+)/$', DeleteAttribution.as_view(),
            name="remove_attribution"),
        url(r'^charge_repartition/', include([
            url(r'^add/(?P<attribution_id>[0-9]+)/$', AddChargeRepartition.as_view(),
                name="add_charge_repartition"),
            url(r'^edit/(?P<attribution_id>[0-9]+)/$', EditChargeRepartition.as_view(),
                name="edit_charge_repartition"),
        ])),
    ])),
    url(r'^(?P<code>[A-Za-z0-9]+)/(?P<year>[0-9]+)/attributions/', include([
        url(r'^$', LearningUnitAttributions.as_view(), name="learning_unit_attributions"),
        url(r'^select/$', SelectAttributionView.as_view(), name="select_attribution"),
    ])),
]
