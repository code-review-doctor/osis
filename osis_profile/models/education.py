# ##############################################################################
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
# ##############################################################################
from functools import partial

from django.db import models

from osis_document.contrib import FileField
from osis_profile.models import FILE_MAX_SIZE


class Education(models.Model):
    person = models.OneToOneField('base.Person', on_delete=models.CASCADE)
    last_diploma_year = models.ForeignKey('base.AcademicYear', on_delete=models.SET_NULL, null=True)
    # belge ou étranger
    foreign_diploma = models.BooleanField(null=True)
    # Type de baccalauréat
    diploma_type = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    # Pays organisateur
    diploma_country = models.ForeignKey('reference.Country', on_delete=models.SET_NULL, null=True)
    # Equivalence
    equivalence = models.CharField(choices=(('TODO', 'tidi'),), null=True, max_length=250)
    # Régime linguistique
    linguistic_system = models.CharField(null=True, max_length=250)
    # Autre régime linguistique
    other_linguistic_system = models.CharField(null=True, max_length=250)
    # Résultat obtenu
    results = models.CharField(null=True, max_length=250)

    # Communauté F/Fl/G
    belgian_community = models.CharField(null=True, max_length=250)
    # Type d'enseignement
    education_type = models.CharField(null=True, max_length=250)
    # Autre type d'enseignement
    other_education_type = models.CharField(default='', max_length=250)
    # Redoublement
    repeated = models.NullBooleanField()
    # Changement d'orientation
    changed_orientation = models.NullBooleanField()
    # Localité
    # Code postal
    # Identification établissement
    belgian_school = models.ForeignKey('base.Entity', on_delete=models.SET_NULL, null=True)
    # Autre établissement
    other_school = models.CharField(default='', max_length=250)

    # Langues anciennes, latin
    # Langues anciennes, grec
    # Langues modernes, allemand
    # Langues modernes, néerlandais
    # Langues modernes, anglais
    # Langues modernes, français
    # Langues modernes, autres
    # Mathématique
    # Informatique
    # Sciences sociales
    # Sciences économiques
    # Autre option
    # Chimie
    # Physique
    # Biologie

    curriculum_file = FileField(
        mimetypes=['application/pdf'],
        max_size=FILE_MAX_SIZE,
        max_files=1,
    )


class LanguageKnowledge(models.Model):
    person = models.ForeignKey('base.Person', on_delete=models.CASCADE)
    language = models.ForeignKey('reference.Language', on_delete=models.CASCADE)
    hearing_level = ComprehensionLevelField()
    speaking_level = ComprehensionLevelField()
    writing_level = ComprehensionLevelField()


ComprehensionLevelField = partial(models.CharField, choices=(
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),
    ('C1', 'C1'),
    ('C2', 'C2'),
), max_length=2)
