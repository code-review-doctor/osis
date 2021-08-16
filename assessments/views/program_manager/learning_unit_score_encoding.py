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
from assessments.views.common.learning_unit_score_encoding import LearningUnitScoreEncodingBaseView
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand
from infrastructure.messages_bus import message_bus_instance


class LearningUnitScoreEncodingProgramManagerView(LearningUnitScoreEncodingBaseView):
    # TemplateView
    template_name = "assessments/program_manager/learning_unit_score_encoding.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(),
            'feuille_de_notes': self.get_feuille_de_notes(),
        }

    def get_feuille_de_notes(self):
        cmd = GetFeuilleDeNotesCommand(
            matricule_fgs_enseignant=self.person.global_id,
            code_unite_enseignement=self.kwargs['learning_unit_code'].upper()
        )
        return message_bus_instance.invoke(cmd)
