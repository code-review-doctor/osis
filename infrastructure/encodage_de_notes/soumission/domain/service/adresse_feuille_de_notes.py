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
from typing import Set

from django.db.models import F, Subquery, OuterRef

from assessments.models.score_sheet_address import ScoreSheetAddress
from base.models.education_group_year import EducationGroupYear
from ddd.logic.encodage_des_notes.soumission.domain.service.i_contact_feuille_de_notes import \
    IAdresseFeuilleDeNotesTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO


class AdresseFeuilleDeNotesTranslator(IAdresseFeuilleDeNotesTranslator):

    @classmethod
    def search(
            cls,
            noms_cohortes: Set[str]
    ) -> Set['AdresseFeuilleDeNotesDTO']:
        # TODO :: migrer les données des adresses des Entités dans ScoreSheetAddress (actuellement, c'est calculé à chaque fois à la volée...)
        # TODO :: implémenter le filtre sur les 11BA
        qs = ScoreSheetAddress.objects.filter(
            education_group__educationgroupyear__acronym__in=noms_cohortes,
        ).annotate(
            nom_cohorte=Subquery(
                EducationGroupYear.objects.filter(
                    education_group_id=OuterRef('education_group_id'),
                ).order_by('-academic_year__year').values('acronym')[:1]
            ),
            destinataire=F('recipient'),
            rue_et_numero=F('location'),
            code_postal=F('postal_code'),
            ville=F('city'),
            pays=F('country__name'),
            telephone=F('phone'),
        ).values(
            'nom_cohorte',
            'destinataire',
            'rue_et_numero',
            'code_postal',
            'ville',
            'pays',
            'telephone',
            'fax',
            'email',
        ).distinct()

        return {AdresseFeuilleDeNotesDTO(**values) for values in qs}
