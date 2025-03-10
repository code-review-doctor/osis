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

from base.forms.learning_unit.comparison import SelectComparisonYears
from base.forms.learning_unit.search.service_course import ServiceCourseFilter
from base.utils.search import RenderToExcel
from base.views.learning_units.search.common import _create_xls_with_parameters, \
    _create_xls_attributions, \
    _create_xls_comparison, _create_xls, BaseLearningUnitSearch, _create_xls_educational_specifications, SearchTypes, \
    _create_xls_ue_utilizations_with_one_training_per_line
from learning_unit.api.serializers.learning_unit import LearningUnitSerializer


@RenderToExcel("xls_with_parameters", _create_xls_with_parameters)
@RenderToExcel("xls_attributions", _create_xls_attributions)
@RenderToExcel("xls_comparison", _create_xls_comparison)
@RenderToExcel("xls_educational_specifications", _create_xls_educational_specifications)
@RenderToExcel("xls", _create_xls)
@RenderToExcel("xls_one_pgm_per_line", _create_xls_ue_utilizations_with_one_training_per_line)
class ServiceCourseSearch(BaseLearningUnitSearch):
    template_name = "learning_unit/search/base.html"
    search_type = SearchTypes.SERVICE_COURSES_SEARCH
    filterset_class = ServiceCourseFilter
    serializer_class = LearningUnitSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context["form"]
        select_comparison_form_academic_year = context["proposal_academic_year"].year
        if form.is_valid():
            select_comparison_form_academic_year = form.cleaned_data["academic_year__year"] or \
                                                   select_comparison_form_academic_year

        context.update({
            "form_comparison": SelectComparisonYears(academic_year=select_comparison_form_academic_year),
        })
        return context
