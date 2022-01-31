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
            annee: int,
            code_programme: str,
            **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context.update(
            contexte_commun_preparation_inscription(
                self.kwargs['code_programme'],
                annee
            )
        )

        return context


def _get_formation_inscription_cours(annee: int, code_programme: str) -> FormulaireInscriptionCoursDTO:
    cmd = GetFormulaireInscriptionCoursCommand(
        annee=annee,
        code_programme=code_programme,
    )
    return message_bus_instance.invoke(cmd)


def contexte_commun_preparation_inscription(code_programme: str, annee: int) -> dict:
    formulaire = _get_formation_inscription_cours(annee, code_programme)
    return {
        'code': "{}{}".format(
            formulaire.sigle_formation,
            formulaire.version_formation if formulaire.version_formation != STANDARD else ''
        ),
        'acronym': code_programme,
        'title': formulaire.intitule_formation,
        'formulaire_inscription_cours': formulaire,
        'year': annee,
    }
