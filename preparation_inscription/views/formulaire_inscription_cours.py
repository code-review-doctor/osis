##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.http import Http404
from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from base.utils.htmx import HtmxMixin
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormulaireInscriptionCoursDTO
from infrastructure.messages_bus import message_bus_instance
from program_management.forms.education_groups import STANDARD
from osis_role.contrib.views import PermissionRequiredMixin


class FormulaireInscriptionCoursView(PermissionRequiredMixin, HtmxMixin, LoginRequiredMixin, TemplateView):
    name = "pae_formulaire_inscription_view"
    permission_required = 'preparation_inscription.view_formulaire_inscription_cours'
    raise_exception = True

    template_name = "preparation_inscription/blocks/formulaire_inscription.html"
    htmx_template_name = "preparation_inscription/blocks/formulaire_inscription.html"

    def get_context_data(
            self,
            year: int,
            acronym: str,
            version_name: str = '',
            transition_name: str = '',
            **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context.update(
            contexte_commun_preparation_inscription(
                self.kwargs['acronym'],
                transition_name if transition_name else '',
                version_name if version_name != STANDARD else '',
                year
            )
        )

        return context


def _get_formation_inscription_cours(year: int, acronym: str, version_name: str, transition_name: str) \
        -> FormulaireInscriptionCoursDTO:
    cmd = GetFormulaireInscriptionCoursCommand(
        annee_formation=year,
        sigle_formation=acronym,
        version_formation=version_name,
        transition_formation=transition_name,
    )
    return message_bus_instance.invoke(cmd)


def contexte_commun_preparation_inscription(sigle, transition_name, version_name, year) -> dict:
    formulaire = _get_formation_inscription_cours(year, sigle, version_name, transition_name)
    return {
        'code': "{}{}".format(
            formulaire.sigle_formation,
            formulaire.version_formation if formulaire.version_formation != STANDARD else ''
        ),
        'acronym': sigle,
        'title': formulaire.intitule_formation,
        'formulaire_inscription_cours': formulaire,
        'year': year,
        }
