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

from django.http import Http404
from django.views.generic import TemplateView

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormulaireInscriptionCoursDTO
from education_group.ddd import command as command_education_group
from education_group.ddd.domain.exception import GroupNotFoundException
from education_group.ddd.service.read import get_group_service
from infrastructure.messages_bus import message_bus_instance
from program_management.forms.education_groups import STANDARD


class FormulaireInscriptionCoursView(TemplateView):
    permission_required = 'preparation_programme.view_formulaire_inscription_cours'
    raise_exception = True

    template_name = "onglets.html"

    def get_context_data(
            self,
            year: int,
            acronym: str,
            version_name: str = '',
            transition_name: str = '',
            **kwargs
    ):
        context = super().get_context_data(**kwargs)
        sigle = self.get_group_obj().abbreviated_title
        context.update(contexte_commun_preparation_inscription(sigle, transition_name, version_name, year))

        return context

    def get_group_obj(self) -> 'Group':
        try:
            get_cmd = command_education_group.GetGroupCommand(
                code=self.kwargs["acronym"],
                year=self.kwargs["year"]
            )
            return get_group_service.get_group(get_cmd)
        except GroupNotFoundException:
            raise Http404


def _get_formation_inscription_cours(year: int, acronym: str, version_name: str, transition_name: str) \
        -> FormulaireInscriptionCoursDTO:
    cmd = GetFormulaireInscriptionCoursCommand(
        annee_formation=year,
        sigle_formation=acronym,
        version_formation=version_name if version_name != STANDARD else '',
        transition_formation=transition_name if transition_name else '',
    )
    return message_bus_instance.invoke(cmd)


def contexte_commun_preparation_inscription(sigle, transition_name, version_name, year) -> dict:
    formulaire = _get_formation_inscription_cours(year, sigle, version_name, transition_name)
    return {
        'code': "{}{}".format(
            formulaire.sigle_formation,
            formulaire.version_formation if formulaire.version_formation != STANDARD else ''
        ),
        'title': formulaire.intitule_complet_formation,
        'formulaire_inscription_cours': formulaire,
        'year': year,
        }
