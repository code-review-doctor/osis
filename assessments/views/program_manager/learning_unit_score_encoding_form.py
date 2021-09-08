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
from django.utils.functional import cached_property

from assessments.views.common.learning_unit_score_encoding_form import LearningUnitScoreEncodingBaseFormView
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNoteCommand, GetFeuilleDeNotesGestionnaireCommand, \
    EncoderNotesCommand
from infrastructure.messages_bus import message_bus_instance


class LearningUnitScoreEncodingProgramManagerFormView(LearningUnitScoreEncodingBaseFormView):
    # TemplateView
    template_name = "assessments/program_manager/learning_unit_score_encoding_form.html"

    @cached_property
    def feuille_de_notes(self):
        cmd = GetFeuilleDeNotesGestionnaireCommand(
            matricule_fgs_gestionnaire=self.person.global_id,
            code_unite_enseignement=self.kwargs['learning_unit_code'].upper()
        )
        return message_bus_instance.invoke(cmd)

    def form_valid(self, formset):
        cmd = EncoderNotesCommand(
            matricule_fgs_gestionnaire=self.person.global_id,
            notes_encodees=[
                EncoderNoteCommand(
                    noma=form.cleaned_data['noma'],
                    email=self.feuille_de_notes.get_email_for_noma(form.cleaned_data['noma']),
                    code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
                    note=form.cleaned_data['note']
                ) for form in formset if form.has_changed()
            ]
        )

        if cmd.notes_encodees:
            try:
                message_bus_instance.invoke(cmd)
            except MultipleBusinessExceptions as e:
                for exception in e.exceptions:
                    form = next(
                        form for form in formset
                        if form.has_changed() and form.cleaned_data['noma'] == exception.note_id.noma
                    )
                    form.add_error('note', exception.message)

        if formset.is_valid():
            return self.get_success_url()
        return self.render_to_response(self.get_context_data(form=formset))

    def get_initial(self):
        formeset_initial = []
        for note_etudiant in self.feuille_de_notes.notes_etudiants:
            if not note_etudiant.date_echeance_atteinte:
                formeset_initial.append({'note': note_etudiant.note, 'noma': note_etudiant.noma})
            else:
                formeset_initial.append({})
        return formeset_initial
