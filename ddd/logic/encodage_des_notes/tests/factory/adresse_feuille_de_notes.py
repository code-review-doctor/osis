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

from assessments.models.enums.score_sheet_address_choices import ScoreSheetAddressEntityType
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import \
    IdentiteAdresseFeuilleDeNotes, \
    AdresseFeuilleDeNotes
from ddd.logic.shared_kernel.entite.tests.factory.entiteucl import _IdentiteEntiteFactory


class _IdentiteAdresseFeuilleDeNotesFactory(factory.Factory):
    class Meta:
        model = IdentiteAdresseFeuilleDeNotes
        abstract = False

    nom_cohorte = "DROI1BA"


class AdresseFeuilleDeNotesVideFactory(factory.Factory):
    class Meta:
        model = AdresseFeuilleDeNotes
        abstract = False

    entity_id = factory.SubFactory(_IdentiteAdresseFeuilleDeNotesFactory)
    type_entite = None
    destinataire = ""
    rue_numero = ""
    code_postal = ""
    ville = ""
    pays = ""
    telephone = ""
    fax = ""
    email = ""


class AdresseFeuilleDeNotesSpecifiqueFactory(AdresseFeuilleDeNotesVideFactory):
    entity_id = factory.SubFactory(_IdentiteAdresseFeuilleDeNotesFactory)
    type_entite = None
    destinataire = "Faculté de Droit"
    rue_numero = "Rue de la Fac, 19"
    code_postal = "1321"
    ville = "Louvain-La-Neuve"
    pays = "Belgique"
    telephone = "0106601122"
    fax = "0106601123"
    email = "email-fac-droit@email.be"


class PremiereAnneeBachelierAdresseFeuilleDeNotesSpecifiqueFactory(AdresseFeuilleDeNotesSpecifiqueFactory):
    entity_id = factory.SubFactory(_IdentiteAdresseFeuilleDeNotesFactory, nom_cohorte="ECGE11BA")
    pays = "France"


class AdresseFeuilleDeNotesBaseeSurEntiteFactory(AdresseFeuilleDeNotesVideFactory):
    entity_id = factory.SubFactory(_IdentiteAdresseFeuilleDeNotesFactory)
    type_entite = ScoreSheetAddressEntityType.ENTITY_ADMINISTRATION
    destinataire = "EPL - Faculté de EPL"
    rue_numero = "Rue de EPL, 19"
    code_postal = "1321"
    ville = "Louvain-La-Neuve"
    pays = "Belgique"
    telephone = "0106605122"
    fax = "0106601123"
    email = "email-epl@email.be"


class PremiereAnneeBachelierAdresseFeuilleDeNotesBaseeSurEntiteFactory(AdresseFeuilleDeNotesBaseeSurEntiteFactory):
    entity_id = factory.SubFactory(_IdentiteAdresseFeuilleDeNotesFactory, nom_cohorte="ECGE11BA")
