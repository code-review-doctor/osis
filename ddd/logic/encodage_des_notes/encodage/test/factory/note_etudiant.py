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
import datetime
import random

import factory

from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.encodage.domain.model._note import NoteChiffree, Justification, NoteManquante
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO


def generate_noma() -> str:
    first_digit = str(random.randint(1, 9))
    other_digits = [str(random.randint(0, 9)) for _ in range(8)]
    return "".join([first_digit] + other_digits)


def generate_note_chiffree() -> 'NoteChiffree':
    return NoteChiffree(
        value=random.randint(0, 20)
    )


def generate_note_justification() -> 'Justification':
    return Justification(
        value=random.choice(JustificationTypes.all())
    )


class _IdentiteNoteEtudiantFactory(factory.Factory):
    class Meta:
        model = IdentiteNoteEtudiant
        abstract = False

    noma = factory.LazyFunction(generate_noma)
    numero_session = 2
    code_unite_enseignement = 'LDROI1001'
    annee_academique = 2020


class NoteManquanteEtudiantFactory(factory.Factory):
    class Meta:
        model = NoteEtudiant
        abstract = False

    entity_id = factory.SubFactory(_IdentiteNoteEtudiantFactory)
    note = NoteManquante()
    email = factory.Faker('email')
    nom_cohorte = 'DROI1BA'
    echeance_gestionnaire = factory.LazyFunction(lambda: DateDTO.build_from_date(datetime.date.today()))
    echeance_enseignant = factory.LazyFunction(lambda: DateDTO.build_from_date(datetime.date.today()))
    note_decimale_autorisee = False

    class Params:
        date_remise_hier = factory.Trait(
            echeance_gestionnaire=factory.LazyFunction(
                lambda: DateDTO.build_from_date(datetime.date.today() - datetime.timedelta(days=1))
            )
        )
        date_remise_aujourdhui = factory.Trait(
            echeance_gestionnaire=factory.LazyFunction(lambda: DateDTO.build_from_date(datetime.date.today()))
        )
        for_class = factory.Trait(
            entity_id=factory.SubFactory(
                _IdentiteNoteEtudiantFactory,
                code_unite_enseignement='LDROI1001-A'
            )
        )


class NoteManquanteEtudiantDateLimiteDepasseeFactory(NoteManquanteEtudiantFactory):
    date_limite_de_remise = DateDTO.build_from_date(datetime.date.today() - datetime.timedelta(days=1))


class NoteEtudiantChiffreeFactory(NoteManquanteEtudiantFactory):
    note = generate_note_chiffree()


class NoteEtudiantJustificationFactory(NoteManquanteEtudiantFactory):
    note = generate_note_justification()


class NoteDecimalesAuthorisees(NoteManquanteEtudiantFactory):
    note_decimale_autorisee = True
