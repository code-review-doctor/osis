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
import json

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from base.models import exam_enrollment
from ddd.logic.encodage_des_notes.soumission.dtos import NoteEtudiantDTO
from education_group.templatetags.academic_year_display import display_as_academic_year


class _EnrollmentSerializer(serializers.Serializer):
    registration_id = serializers.CharField(read_only=True, source='noma')
    last_name = serializers.CharField(read_only=True, source='nom')
    first_name = serializers.CharField(read_only=True, source='prenom')
    score = serializers.CharField(read_only=True, source='note')
    justification = serializers.CharField(read_only=True, source='note')
    deadline = serializers.DateField(read_only=True, source='date_remise_de_notes.to_date')
    enrollment_state_color = serializers.SerializerMethodField()

    def get_enrollment_state_color(self, note_etudiant: NoteEtudiantDTO) -> str:
        if note_etudiant.inscrit_tardivement:
            return '#dff0d8'
        elif note_etudiant.desinscrit_tardivement:
            return '#f2dede'
        return ''


class _ProgramAddressSerializer(serializers.Serializer):
    # TODO: Use data from administrative data service
    recipient = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    location = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    postal_code = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    city = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    country = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    phone = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    fax = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    email = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')


class _ProgramSerializer(serializers.Serializer):
    deliberation_date = serializers.SerializerMethodField()
    acronym = serializers.SerializerMethodField()
    address = _ProgramAddressSerializer(source='*')
    enrollments = serializers.SerializerMethodField()

    def get_deliberation_date(self, obj):
        return str(_('Not passed'))

    def get_acronym(self, obj):
        return "MISSING"

    def get_enrollments(self, obj):
        notes_etudiants = obj['feuille_de_notes'].notes_etudiants
        serializer = _EnrollmentSerializer(instance=notes_etudiants, many=True)
        return serializer.data


class _ScoreResponsibleAddressSerializer(serializers.Serializer):
    location = serializers.SerializerMethodField()
    postal_code = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    def get_location(self, obj) -> str:
        return ""

    def get_postal_code(self, obj) -> str:
        return ""

    def get_city(self, obj) -> str:
        return ""


class _ScoreResponsibleSerializer(serializers.Serializer):
    first_name = serializers.CharField(read_only=True, source='feuille_de_notes.responsable_note.prenom')
    last_name = serializers.CharField(read_only=True, source='feuille_de_notes.responsable_note.nom')
    address = _ScoreResponsibleAddressSerializer(source='*')


class _LearningUnitYearsSerializer(serializers.Serializer):
    session_number = serializers.IntegerField(read_only=True, source='feuille_de_notes.numero_session')
    title = serializers.CharField(read_only=True, source='feuille_de_notes.intitule_complet_unite_enseignement')
    academic_year = serializers.SerializerMethodField()
    acronym = serializers.CharField(read_only=True, source='feuille_de_notes.code_unite_enseignement')
    decimal_scores = serializers.SerializerMethodField()
    scores_responsible = _ScoreResponsibleSerializer(source="*")
    programs = serializers.SerializerMethodField()

    def get_academic_year(self, obj) -> str:
        return display_as_academic_year(obj['feuille_de_notes'].annee_academique)

    def get_decimal_scores(self, obj) -> bool:
        return False

    def get_programs(self, obj):
        serializer = _ProgramSerializer(instance=obj)
        return [serializer.data]


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
        serializer = _LearningUnitYearsSerializer(instance=obj)
        return [serializer.data]

    def to_representation(self, instance):
        """
        Need in order to ensure backward compatibility with voluptuous library
        """
        representation = super().to_representation(instance)
        json_str = json.dumps(representation)
        return json.loads(json_str)
