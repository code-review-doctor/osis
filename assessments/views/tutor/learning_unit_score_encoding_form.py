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
from gettext import ngettext

import attr
from django.utils.translation import gettext_lazy as _

from django.contrib import messages
from django.utils.functional import cached_property

from assessments.views.common.learning_unit_score_encoding_form import LearningUnitScoreEncodingBaseFormView
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand, EncoderNoteCommand, \
    EncoderNotesEtudiantCommand
from infrastructure.messages_bus import message_bus_instance


class LearningUnitScoreEncodingTutorFormView(LearningUnitScoreEncodingBaseFormView):
    # TemplateView
    template_name = "assessments/tutor/learning_unit_score_encoding_form.html"

    @cached_property
    def feuille_de_notes(self):
        cmd = GetFeuilleDeNotesCommand(
            matricule_fgs_enseignant=self.person.global_id,
            code_unite_enseignement=self.kwargs['learning_unit_code'].upper()
        )
        feuille_de_notes = message_bus_instance.invoke(cmd)
        if self.echeance_enseignant_filter:
            feuille_de_notes = attr.evolve(
                feuille_de_notes,
                notes_etudiants=[
                    n for n in feuille_de_notes.notes_etudiants
                    if n.echeance_enseignant.to_date() == self.echeance_enseignant_filter
                    and not n.desinscrit_tardivement
                ]
            )
        return feuille_de_notes

    def form_valid(self, formset):
        cmd = EncoderNotesEtudiantCommand(
            code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=self.feuille_de_notes.annee_academique,
            numero_session=self.feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.person.global_id,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=form.cleaned_data['noma'],
                    email_etudiant=self.feuille_de_notes.get_email_for_noma(form.cleaned_data['noma']),
                    note=form.cleaned_data['note']
                ) for form in formset if form.has_changed()
            ]
        )

        if cmd.notes:
            try:
                message_bus_instance.invoke(cmd)
            except MultipleBusinessExceptions as e:
                for exception in e.exceptions:
                    form = next(
                        form for form in formset
                        if form.has_changed() and form.cleaned_data['noma'] == exception.note_id.noma
                    )
                    form.add_error('note', exception.message)

        self.display_success_error_counter(cmd, formset)
        if formset.is_valid():
            return self.get_success_url()
        return self.render_to_response(self.get_context_data(form=formset))

    def display_success_error_counter(self, cmd, formset):
        error_counter = sum(1 for form in formset if form.has_changed() and not form.is_valid())
        success_counter = len(cmd.notes) - error_counter
        if error_counter > 0:
            messages.error(
                self.request,
                ngettext(
                    "There is %(error_counter)s error in form",
                    "There are %(error_counter)s errors in form",
                    error_counter
                ) % {'error_counter': error_counter}
            )
        if success_counter > 0:
            messages.success(self.request, '%s %s' % (str(success_counter), _('Score(s) saved')))

    def get_initial(self):
        formset_initial = []
        for note_etudiant in self.feuille_de_notes.notes_etudiants:
            if not note_etudiant.est_soumise and not note_etudiant.date_echeance_atteinte and \
                    not note_etudiant.desinscrit_tardivement:
                initial_note_etudiant = self._get_initial_note_etudiant(note_etudiant)
                formset_initial.append(initial_note_etudiant)
            else:
                formset_initial.append({})
        return formset_initial
