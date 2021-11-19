##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from base.business.learning_units.pedagogy import is_pedagogy_data_must_be_postponed
from base.models import learning_unit_year
from base.models.learning_unit_year import LearningUnitYear
from base.models.proposal_learning_unit import ProposalLearningUnit
from base.views import learning_unit
from base.views.common import display_success_messages
from learning_unit.views.utils import learning_unit_year_getter
from osis_role.contrib.views import permission_required


@login_required
@require_http_methods(["POST"])
@permission_required('base.can_edit_summary_locked_field', fn=learning_unit_year_getter, raise_exception=True)
def toggle_summary_locked(request, learning_unit_year_id):
    luy = learning_unit_year.toggle_summary_locked(learning_unit_year_id)
    success_msg = "Update for teacher locked" if luy.summary_locked else "Update for teacher unlocked"
    display_success_messages(request, success_msg)
    return redirect(reverse("learning_unit_pedagogy", kwargs={'learning_unit_year_id': learning_unit_year_id}))


def build_success_message(last_luy_reported: LearningUnitYear, luy: LearningUnitYear) -> str:
    default_message = _("The learning unit has been updated (without report).")
    proposal = ProposalLearningUnit.objects.filter(learning_unit_year__learning_unit=luy.learning_unit).first()

    if last_luy_reported and is_pedagogy_data_must_be_postponed(luy):
        msg = "{} {}.".format(
            _("The learning unit has been updated"),
            _("and postponed until %(year)s") % {
                "year": last_luy_reported.academic_year
            }
        )
    elif proposal and learning_unit.proposal_is_on_same_year(proposal=proposal, base_luy=luy):
        msg = "{}. {}.".format(
            _("The learning unit has been updated"),
            _("The learning unit is in proposal, the report from %(proposal_year)s will be done at "
              "consolidation") % {
                'proposal_year': proposal.learning_unit_year.academic_year
            }
        )
    elif proposal and learning_unit.proposal_is_on_future_year(proposal=proposal, base_luy=luy):
        msg = "{} ({}).".format(
            _("The learning unit has been updated"),
            _("the report has not been done from %(proposal_year)s because the LU is in proposal") % {
                'proposal_year': proposal.learning_unit_year.academic_year
            }
        )
    else:
        msg = "{}".format(default_message)

    return msg
