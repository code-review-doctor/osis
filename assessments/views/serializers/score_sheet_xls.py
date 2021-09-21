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
import operator

import attr
from django.template.defaultfilters import floatformat
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from base.models.enums.peps_type import PepsTypes, HtmSubtypes, SportSubtypes
from ddd.logic.encodage_des_notes.shared_kernel.dtos import NoteEtudiantDTO
from education_group.templatetags.academic_year_display import display_as_academic_year


class _NoteEtudiantRowSerializer(serializers.Serializer):
    noma = serializers.CharField(read_only=True, default='')
    nom = serializers.CharField(read_only=True, default='')
    prenom = serializers.CharField(read_only=True, default='')
    note = serializers.SerializerMethodField()
    nom_cohorte = serializers.CharField(read_only=True, default='')
    email = serializers.CharField(read_only=True, default='')
    date_remise_de_notes = serializers.DateField(
        read_only=True, source='date_remise_de_notes.to_date', format="%d/%m/%Y"
    )
    est_soumise = serializers.BooleanField(read_only=True, default=False)
    inscrit_tardivement = serializers.BooleanField(read_only=True, default=False)
    desinscrit_tardivement = serializers.BooleanField(read_only=True, default=False)
    type_peps = serializers.SerializerMethodField()
    tiers_temps = serializers.SerializerMethodField()
    copie_adaptee = serializers.SerializerMethodField()
    local_specifique = serializers.SerializerMethodField()
    autre_amenagement = serializers.SerializerMethodField()
    details_autre_amenagement = serializers.SerializerMethodField()
    accompagnateur = serializers.SerializerMethodField()
    enrollment_state_color = serializers.SerializerMethodField()

    def get_type_peps(self, note_etudiant: NoteEtudiantDTO):
        try:
            type_peps = operator.attrgetter("peps.type_peps")(note_etudiant)
            if not type_peps:
                return "-"

            type_peps_str = str(PepsTypes.get_value(type_peps))
            sous_type_peps = operator.attrgetter("peps.sous_type_peps")(note_etudiant)
            if type_peps == PepsTypes.DISABILITY.name:
                return "{} - {}".format(
                    type_peps_str,
                    str(HtmSubtypes.get_value(sous_type_peps)) if sous_type_peps else '-'
                )
            elif type_peps == PepsTypes.SPORT.name:
                return "{} - {}".format(
                    type_peps_str,
                    str(SportSubtypes.get_value(sous_type_peps)) if sous_type_peps else '-'
                )
            elif type_peps == PepsTypes.NOT_DEFINED.name:
                return "-"
            return type_peps_str
        except AttributeError:
            return "-"

    def get_tiers_temps(self, note_etudiant: NoteEtudiantDTO):
        try:
            is_tiers_temps = operator.attrgetter("peps.tiers_temps")(note_etudiant)
            return str(_('Yes')) if is_tiers_temps else '-'
        except AttributeError:
            return "-"

    def get_copie_adaptee(self, note_etudiant: NoteEtudiantDTO):
        try:
            is_copie_adaptee = operator.attrgetter("peps.tiers_temps")(note_etudiant)
            return str(_('Yes')) if is_copie_adaptee else '-'
        except AttributeError:
            return "-"

    def get_local_specifique(self, note_etudiant: NoteEtudiantDTO):
        try:
            local_specifique = operator.attrgetter("peps.local_specifique")(note_etudiant)
            return str(_('Yes')) if local_specifique else '-'
        except AttributeError:
            return "-"

    def get_autre_amenagement(self, note_etudiant: NoteEtudiantDTO):
        try:
            autre_amenagement = operator.attrgetter("peps.autre_amenagement")(note_etudiant)
            return str(_('Yes')) if autre_amenagement else '-'
        except AttributeError:
            return "-"

    def get_details_autre_amenagement(self, note_etudiant: NoteEtudiantDTO):
        try:
            return operator.attrgetter("peps.details_autre_amenagement")(note_etudiant)
        except AttributeError:
            return "-"

    def get_accompagnateur(self, note_etudiant: NoteEtudiantDTO):
        try:
            return operator.attrgetter("peps.accompagnateur")(note_etudiant)
        except AttributeError:
            return "-"

    def get_enrollment_state_color(self, note_etudiant: NoteEtudiantDTO) -> str:
        if note_etudiant.inscrit_tardivement:
            return '#dff0d8'
        elif note_etudiant.desinscrit_tardivement:
            return '#f2dede'
        return ''

    def get_note(self, note_etudiant: NoteEtudiantDTO) -> str:
        try:
            note_format = "2" if self.context['note_decimale_est_autorisee'] else "0"
            return floatformat(float(note_etudiant.note), note_format)
        except ValueError:
            return note_etudiant.note


class ScoreSheetXLSSerializer(serializers.Serializer):
    numero_session = serializers.IntegerField(read_only=True, source='feuille_de_notes.numero_session', default='')
    titre = serializers.SerializerMethodField()
    code_unite_enseignement = serializers.CharField(
        read_only=True, source='feuille_de_notes.code_unite_enseignement', default=''
    )
    annee_academique = serializers.SerializerMethodField()
    note_decimale_est_autorisee = serializers.BooleanField(
        read_only=True,
        source='feuille_de_notes.note_decimale_est_autorisee',
        default=False
    )
    contact_emails = serializers.SerializerMethodField()
    rows = serializers.SerializerMethodField()

    def get_annee_academique(self, obj) -> str:
        return display_as_academic_year(obj['feuille_de_notes'].annee_academique)

    def get_titre(self, obj) -> str:
        return "{} - {}".format(
            self.get_annee_academique(obj),
            obj['feuille_de_notes'].intitule_complet_unite_enseignement
        )

    def get_contact_emails(self, obj) -> str:
        return ""

    def get_rows(self, obj):
        notes_etudiants_avec_date_echeance_non_atteinte = filter(
            lambda n: not n.date_echeance_atteinte, obj['feuille_de_notes'].notes_etudiants
        )
        serializer = _NoteEtudiantRowSerializer(
            instance=notes_etudiants_avec_date_echeance_non_atteinte,
            context={'note_decimale_est_autorisee': obj['feuille_de_notes'].note_decimale_est_autorisee},
            many=True
        )
        return serializer.data

    def to_representation(self, instance):
        """
        Need in order to ensure backward compatibility with voluptuous library
        """
        representation = super().to_representation(instance)
        json_str = json.dumps(representation)
        return json.loads(json_str)


class TutorScoreSheetXLSSerializer(ScoreSheetXLSSerializer):
    def get_rows(self, obj):
        notes_etudiants_filtered = filter(
            lambda n: not n.date_echeance_atteinte and not n.est_soumise,
            obj['feuille_de_notes'].notes_etudiants
        )

        notes_etudiants_without_value = map(lambda n: attr.evolve(n, note=''), notes_etudiants_filtered)
        serializer = _NoteEtudiantRowSerializer(
            instance=notes_etudiants_without_value,
            context={'note_decimale_est_autorisee': obj['feuille_de_notes'].note_decimale_est_autorisee},
            many=True
        )
        return serializer.data

    def get_contact_emails(self, obj) -> str:
        return ";".join({
            d_admin.contact_feuille_de_notes.email for d_admin in obj['donnees_administratives']
            if d_admin.contact_feuille_de_notes.email
        })
