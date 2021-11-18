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
from datetime import date

from rest_framework import serializers


class LearningUnitProgressSerializer(serializers.Serializer):
    code = serializers.CharField(source='code_unite_enseignement')
    full_title = serializers.CharField(source='intitule_complet_unite_enseignement')
    due_dates = serializers.SerializerMethodField()
    score_responsible = serializers.SerializerMethodField(source='responsable_note')
    has_peps = serializers.BooleanField(source='a_etudiants_peps')

    def get_due_dates(self, obj):
        return [date(d.annee, d.mois, d.jour) for d in obj.dates_echeance]

    def get_score_responsible(self, obj):
        return "{} {}".format(
            obj.responsable_note.nom, obj.responsable_note.prenom
        ) if obj.responsable_note.nom else None  # EnseignantDTO is not nullable


class ProgressOverviewSerializer(serializers.Serializer):
    academic_year = serializers.IntegerField(source='annee_academique')
    session_number = serializers.IntegerField(source='numero_session')
    learning_units_progress = serializers.ListSerializer(
        source='progression_generale', child=LearningUnitProgressSerializer()
    )
