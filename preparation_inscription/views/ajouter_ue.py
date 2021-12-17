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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from base.forms.learning_unit.search.simple import LearningUnitFilter
from base.views.common import display_success_messages
from base.views.learning_units.search.common import BaseLearningUnitSearch, SearchTypes
from learning_unit.api.serializers.learning_unit import LearningUnitSerializer
from preparation_inscription.views.formulaire_par_defaut import contexte_commun_preparation_inscription


class RechercherUeView(BaseLearningUnitSearch):
    template_name = "onglets.html"
    search_type = SearchTypes.SIMPLE_SEARCH
    filterset_class = LearningUnitFilter
    serializer_class = LearningUnitSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(contexte_commun_preparation_inscription('ECGE1BA', None, 'STANDARD', 2021))
        return context


@login_required
@permission_required('preparation_programme.can_add_unites_enseignement_au_programme', raise_exception=True)
def ajouterUeView(request, year: int):
    unites_enseignement_selectionnees = request.POST.getlist('selected_ue', default=[])
    # year est actuellement inutilisé, mais sera amené à la devenir dans la suite

    success_msg = _('The following learning units have been successfully added to program : %(ues)s') % {
        "ues": ', '.join(unites_enseignement_selectionnees)
    }
    display_success_messages(request, success_msg)
    return redirect('search_ue_to_program')
