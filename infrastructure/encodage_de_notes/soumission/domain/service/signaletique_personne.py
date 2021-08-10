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

from django.db.models import F, Prefetch, CharField, Value, Case, When

from base.models.enums.person_address_type import PersonAddressType
from base.models.person import Person
from base.models.person_address import PersonAddress
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import DetailContactDTO, AdresseDTO


class SignaletiquePersonneTranslator(ISignaletiquePersonneTranslator):

    @classmethod
    def search(
            cls,
            matricules_fgs: Set[str]
    ) -> Set['DetailContactDTO']:
        # qs = Person.objects.filter(
        #     global_id__in=matricules_fgs,
        #     personaddress__label=PersonAddressType.PROFESSIONAL.name,
        # ).annotate(
        #     matricule_fgs=F('global_id'),
        #     code_postal=Case(
        #         When(
        #             personaddress__isnull=False,
        #             then='personaddress__postal_code',
        #         ),
        #         default=Value(''),
        #         output_field=CharField(),
        #     ),
        #     ville=Case(
        #         When(
        #             personaddress__isnull=False,
        #             then='personaddress__city',
        #         ),
        #         default=Value(''),
        #         output_field=CharField(),
        #     ),
        #     rue_numero_boite=Case(
        #         When(
        #             personaddress__isnull=False,
        #             then='personaddress__location',
        #         ),
        #         default=Value(''),
        #         output_field=CharField(),
        #     ),
        # ).values(
        #     'matricule_fgs',
        #     'email',
        #     'code_postal',
        #     'ville',
        #     'rue_numero_boite',
        # ).distinct()
        qs = Person.objects.filter(
            global_id__in=matricules_fgs,
        ).prefetch_related(
            Prefetch(
                'personaddress_set',
                queryset=PersonAddress.objects.filter(label=PersonAddressType.PROFESSIONAL.name).only(
                    'postal_code',
                    'city',
                    'location',
                )
            )
        ).annotate(
            matricule_fgs=F('global_id'),
        )
        result = set()
        for obj in qs:
            adresses = list(obj.personaddress_set.all())
            adresse = adresses[0] if adresses else None
            dto = DetailContactDTO(
                matricule_fgs=obj.matricule_fgs,
                email=obj.email,
                adresse_professionnelle=AdresseDTO(
                    code_postal=adresse.postal_code,
                    ville=adresse.city,
                    rue_numero_boite=adresse.location,
                ) if adresse else None
            )
            result.add(dto)
        return result
