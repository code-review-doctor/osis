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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import factory

from base.models.enums.entity_type import EntityType
from ddd.logic.shared_kernel.entite.domain.model._adresse_entite import AdresseEntite
from ddd.logic.shared_kernel.entite.domain.model.entiteucl import IdentiteUCLEntite, EntiteUCL


class _IdentiteEntiteFactory(factory.Factory):
    class Meta:
        model = IdentiteUCLEntite
        abstract = False

    sigle = "EPL"


class _AdresseEntiteFactory(factory.Factory):
    class Meta:
        model = AdresseEntite
        abstract = False

    rue_numero = ""
    code_postal = "1348"
    ville = "Louvain-la-Neuve"
    pays = "Belgique"
    telephone = ""
    fax = ""


class _EntiteUCLFactory(factory.Factory):
    class Meta:
        model = EntiteUCL
        abstract = False

    entity_id = factory.SubFactory(_IdentiteEntiteFactory)
    parent = None
    type = EntityType.FACULTY
    intitule = "Ecole Polytechnique"
    adresse = factory.SubFactory(_AdresseEntiteFactory)


class INFOEntiteFactory(_EntiteUCLFactory):
    entity_id = factory.SubFactory(_IdentiteEntiteFactory, sigle='INFO')
    parent = factory.SubFactory(_IdentiteEntiteFactory, sigle='EPL')
    type = EntityType.SCHOOL
    intitule = "Ecole Informatique"


class EPLEntiteFactory(_EntiteUCLFactory):
    entity_id = factory.SubFactory(_IdentiteEntiteFactory)
    parent = factory.SubFactory(_IdentiteEntiteFactory, sigle='SST')


class SSTEntiteFactory(_EntiteUCLFactory):
    entity_id = factory.SubFactory(_IdentiteEntiteFactory, sigle='SST')
    parent = factory.SubFactory(_IdentiteEntiteFactory, sigle='UCL')
    type = EntityType.SECTOR
    intitule = "Secteur des Sciences et Technologies"


