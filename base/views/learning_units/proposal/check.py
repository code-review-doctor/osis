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
from django.http import JsonResponse

from base.models.proposal_learning_unit import ProposalLearningUnit
from osis_common.decorators.ajax import ajax_required


@login_required
@ajax_required
def get_related_partims_by_ue(request):
    selected_proposals_acronym = request.POST.getlist("selected_action", default=[])
    selected_proposals = ProposalLearningUnit.objects.filter(
        learning_unit_year__acronym__in=selected_proposals_acronym
    )
    related_partims_by_ue = []
    for proposal in selected_proposals:
        partims = proposal.learning_unit_year.get_partims_related().values_list('acronym', flat=True)
        if partims:
            related_partims_by_ue.append(
                {
                    'learning_unit_year': proposal.learning_unit_year.acronym,
                    'partims': ', '.join(list(partims))
                }
            )
    return JsonResponse(related_partims_by_ue, safe=False)
