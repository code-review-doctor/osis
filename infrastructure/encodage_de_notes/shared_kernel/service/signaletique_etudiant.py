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
from typing import Set, List, Dict

from django.db.models import F

from base.models.student import Student
from ddd.logic.encodage_des_notes.shared_kernel.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EtudiantPepsDTO


class SignaletiqueEtudiantTranslator(ISignaletiqueEtudiantTranslator):

    @classmethod
    def search(
            cls,
            nomas: List[str],
            nom: str = None,
            prenom: str = None,
    ) -> Set['SignaletiqueEtudiantDTO']:
        filter_qs = cls._build_filter(nomas, nom, prenom)
        if not filter_qs:
            return set()

        qs_as_values = Student.objects.filter(
            **filter_qs
        ).annotate(
            noma=F('registration_id'),
            nom=F('person__last_name'),
            prenom=F('person__first_name'),
            type_peps=F('studentspecificprofile__type'),
            tiers_temps=F('studentspecificprofile__arrangement_additional_time'),
            copie_adaptee=F('studentspecificprofile__arrangement_appropriate_copy'),
            local_specifique=F('studentspecificprofile__arrangement_specific_locale'),
            autre_amenagement=F('studentspecificprofile__arrangement_other'),
            details_autre_amenagement=F('studentspecificprofile__arrangement_comment'),
            accompagnateur=F('studentspecificprofile__guide'),
        ).values(
            'noma',
            'nom',
            'prenom',
            'type_peps',
            'tiers_temps',
            'copie_adaptee',
            'local_specifique',
            'autre_amenagement',
            'details_autre_amenagement',
            'accompagnateur',
        ).distinct()
        result = set()
        for values in qs_as_values:
            noma = values.pop('noma')
            nom = values.pop('nom')
            prenom = values.pop('prenom')
            peps = None
            if any(values.values()):
                peps = EtudiantPepsDTO(**values)
            result.add(
                SignaletiqueEtudiantDTO(
                    noma=noma,
                    nom=nom,
                    prenom=prenom,
                    peps=peps,
                )
            )
        return result

    @classmethod
    def _build_filter(
            cls,
            nomas: List[str],
            nom: str = None,
            prenom: str = None
    ) -> Dict:
        filter = {}

        if nomas:
            filter["registration_id__in"] = set(nomas)
        if nom:
            filter["person__last_name__icontains"] = nom
        if prenom:
            filter["person__first_name__icontains"] = prenom
        return filter
