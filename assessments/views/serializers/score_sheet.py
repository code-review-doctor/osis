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
import contextlib
import itertools
import json

from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from base.models import exam_enrollment
from ddd.logic.encodage_des_notes.shared_kernel.dtos import NoteEtudiantDTO
from education_group.templatetags.academic_year_display import display_as_academic_year


class _EnrollmentSerializer(serializers.Serializer):
    registration_id = serializers.CharField(read_only=True, source='noma')
    last_name = serializers.CharField(read_only=True, source='nom')
    first_name = serializers.CharField(read_only=True, source='prenom')
    score = serializers.SerializerMethodField()
    deadline = serializers.SerializerMethodField()
    enrollment_state_color = serializers.SerializerMethodField()

    def get_enrollment_state_color(self, note_etudiant: NoteEtudiantDTO) -> str:
        if note_etudiant.inscrit_tardivement:
            return '#dff0d8'
        elif note_etudiant.desinscrit_tardivement:
            return '#f2dede'
        return ''

    def get_score(self, note_etudiant) -> str:
        with contextlib.suppress(ValueError, TypeError):
            note_format = "2" if self.context['note_decimale_est_autorisee'] else "0"
            return floatformat(float(note_etudiant.note), note_format)

        if note_etudiant.note == 'T':
            return str(_('Cheating'))
        elif note_etudiant.note == 'A':
            return str(_('Absent'))
        elif note_etudiant.note == 'S':
            return str(_('Absence unjustified'))
        elif note_etudiant.note == 'M':
            return str(_('Absence justified'))
        return note_etudiant.note

    def get_deadline(self, note_etudiant: NoteEtudiantDTO) -> str:
        if note_etudiant.date_remise_de_notes and not note_etudiant.desinscrit_tardivement:
            return note_etudiant.date_remise_de_notes.to_date().strftime("%d/%m/%Y")
        return ""


class _ProgramAddressSerializer(serializers.Serializer):
    recipient = serializers.CharField(read_only=True, source='destinataire', default='')
    location = serializers.CharField(read_only=True,  source='rue_numero', default='')
    postal_code = serializers.CharField(read_only=True, source='code_postal', default='')
    city = serializers.CharField(read_only=True, source='ville', default='')
    country = serializers.CharField(read_only=True, source='pays', default='')
    phone = serializers.CharField(read_only=True, source='telephone', default='')
    fax = serializers.CharField(read_only=True, default='')
    email = serializers.CharField(read_only=True, default='')


class _ProgramSerializer(serializers.Serializer):
    deliberation_date = serializers.SerializerMethodField()
    acronym = serializers.SerializerMethodField()
    address = _ProgramAddressSerializer(source='donnees_administratives_cohorte.contact_feuille_de_notes')
    enrollments = serializers.SerializerMethodField()

    def get_deliberation_date(self, obj):
        return obj['donnees_administratives_cohorte'].date_deliberation.to_date().strftime("%d/%m/%Y")  \
            if obj['donnees_administratives_cohorte'].date_deliberation else str(_('Not passed'))

    def get_acronym(self, obj):
        return obj['nom_cohorte']

    def get_enrollments(self, obj):
        serializer = _EnrollmentSerializer(instance=obj['notes_etudiants_cohorte'], many=True, context=self.context)
        return serializer.data


class _ScoreResponsibleAddressSerializer(serializers.Serializer):
    location = serializers.CharField(read_only=True, source='rue_numero_boite', default='')
    postal_code = serializers.CharField(read_only=True, source='code_postal', default='')
    city = serializers.CharField(read_only=True, source='ville', default='')


class _ScoreResponsibleSerializer(serializers.Serializer):
    first_name = serializers.CharField(read_only=True, source='feuille_de_notes.responsable_note.prenom', default='')
    last_name = serializers.CharField(read_only=True, source='feuille_de_notes.responsable_note.nom', default='')
    address = serializers.SerializerMethodField()

    def get_address(self, obj):
        instance = {}
        if obj['feuille_de_notes'].contact_responsable_notes:
            instance = obj['feuille_de_notes'].contact_responsable_notes.adresse_professionnelle
        return _ScoreResponsibleAddressSerializer(instance=instance).data


class _LearningUnitYearsSerializer(serializers.Serializer):
    session_number = serializers.IntegerField(read_only=True, source='feuille_de_notes.numero_session')
    title = serializers.CharField(read_only=True, source='feuille_de_notes.intitule_complet_unite_enseignement')
    academic_year = serializers.SerializerMethodField()
    acronym = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    decimal_scores = serializers.BooleanField(read_only=True, source='feuille_de_notes.note_decimale_est_autorisee')
    scores_responsible = _ScoreResponsibleSerializer(source="*")
    programs = serializers.SerializerMethodField()

    def get_academic_year(self, obj) -> str:
        return display_as_academic_year(obj['feuille_de_notes'].annee_academique)

    def get_programs(self, obj):
        programs = []
        rows_sorted_by_cohorte = sorted(obj['feuille_de_notes'].notes_etudiants, key=lambda note: note.nom_cohorte)
        for nom_cohorte, notes_etudiants_cohorte \
                in itertools.groupby(rows_sorted_by_cohorte, key=lambda note: note.nom_cohorte):
            donnees_administratives_cohorte = next((
                donnee_administrative for donnee_administrative in obj['donnees_administratives'] if
                donnee_administrative.sigle_formation == nom_cohorte
            ), None)

            serializer = _ProgramSerializer(instance={
                'notes_etudiants_cohorte': notes_etudiants_cohorte,
                'nom_cohorte': nom_cohorte,
                'donnees_administratives_cohorte': donnees_administratives_cohorte,
            }, context={'note_decimale_est_autorisee': obj['feuille_de_notes'].note_decimale_est_autorisee},)
            programs.append(serializer.data)
        return programs


class ScoreSheetPDFSerializer(serializers.Serializer):
    institution = serializers.SerializerMethodField()
    link_to_regulation = serializers.SerializerMethodField()
    publication_date = serializers.SerializerMethodField()
    justification_legend = serializers.SerializerMethodField()
    tutor_global_id = serializers.SerializerMethodField()
    learning_unit_years = serializers.SerializerMethodField()

    def get_institution(self, obj) -> str:
        return "Université catholique de Louvain"

    def get_link_to_regulation(self, obj) -> str:
        return "https://www.uclouvain.be/enseignement-reglements.html"

    def get_publication_date(self, obj) -> str:
        now = timezone.now()
        return '%s/%s/%s' % (now.day, now.month, now.year)

    def get_justification_legend(self, obj) -> str:
        return _('Justification legend: %(justification_label_authorized)s') % \
               {'justification_label_authorized': exam_enrollment.justification_label_authorized()}

    def get_tutor_global_id(self, obj) -> str:
        return self.context['person'].global_id

    def get_learning_unit_years(self, obj):
        return [_LearningUnitYearsSerializer(instance=item).data for item in obj]

    def to_representation(self, instance):
        """
        Need in order to ensure backward compatibility with voluptuous library
        """
        representation = super().to_representation(instance)
        json_str = json.dumps(representation)
        return json.loads(json_str)
