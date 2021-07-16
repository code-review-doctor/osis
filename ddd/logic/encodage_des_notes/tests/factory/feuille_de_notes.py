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

import factory

from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes, \
    IdentiteFeuilleDeNotes, CREDITS_MIN_POUR_NOTE_DECIMALE
from ddd.logic.encodage_des_notes.tests.factory._note_etudiant import NoteManquanteEtudiantFactory, \
    NoteChiffreEtudiantFactory, NoteJustificationEtudiantFactory


class _IdentiteFeuilleDeNotesFactory(factory.Factory):
    class Meta:
        model = IdentiteFeuilleDeNotes
        abstract = False

    numero_session = 2
    code_unite_enseignement = 'LOSIS1452'
    annee_academique = 2020


class _FeuilleDeNotesFactory(factory.Factory):
    class Meta:
        model = FeuilleDeNotes
        abstract = True

    entity_id = factory.SubFactory(_IdentiteFeuilleDeNotesFactory)
    credits_unite_enseignement = CREDITS_MIN_POUR_NOTE_DECIMALE - 5.0  # Non autorisé par défaut
    notes = set()

    class Params:
        for_class = factory.SubFactory(
            _IdentiteFeuilleDeNotesFactory,
            code_unite_enseignement='LOSIS1452A'
        )


class FeuilleDeNotesAvecNotesManquantes(_FeuilleDeNotesFactory):
    notes = {
        NoteManquanteEtudiantFactory(),
        NoteManquanteEtudiantFactory(),
        NoteManquanteEtudiantFactory()
    }


class FeuilleDeNotesAvecNotesEncodees(_FeuilleDeNotesFactory):
    notes = {
        NoteChiffreEtudiantFactory(),
        NoteChiffreEtudiantFactory(),
        NoteJustificationEtudiantFactory(),
        NoteManquanteEtudiantFactory()
    }


class FeuilleDeNotesAvecNotesSoumises(_FeuilleDeNotesFactory):
    notes = {
        NoteChiffreEtudiantFactory(est_soumise=True),
        NoteChiffreEtudiantFactory(),
        NoteJustificationEtudiantFactory(est_soumise=True),
        NoteManquanteEtudiantFactory()
    }


class FeuilleDeNotesAvecToutesNotesSoumises(_FeuilleDeNotesFactory):
    notes = {
        NoteManquanteEtudiantFactory(est_soumise=True),
        NoteManquanteEtudiantFactory(est_soumise=True),
        NoteManquanteEtudiantFactory(est_soumise=True),
    }


class FeuilleDeNotesDecimalesAutorisees(_FeuilleDeNotesFactory):
    credits_unite_enseignement = CREDITS_MIN_POUR_NOTE_DECIMALE
    notes = {
        NoteManquanteEtudiantFactory(),
    }


class FeuilleDeNotesDateLimiteRemiseAujourdhui(_FeuilleDeNotesFactory):
    credits_unite_enseignement = CREDITS_MIN_POUR_NOTE_DECIMALE
    notes = {
        NoteManquanteEtudiantFactory(date_limite_de_remise=datetime.date.today()),
    }


class FeuilleDeNotesDateLimiteRemiseHier(_FeuilleDeNotesFactory):
    credits_unite_enseignement = CREDITS_MIN_POUR_NOTE_DECIMALE
    notes = {
        NoteManquanteEtudiantFactory(date_limite_de_remise=datetime.date.today() - datetime.timedelta(days=1)),
    }
