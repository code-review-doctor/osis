##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import zipfile

from django import forms
from django.forms import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from openpyxl import load_workbook, Workbook


class ScoreFileForm(forms.Form):
    file = forms.FileField(
        error_messages={'required': _("You have to select a file to upload.")},
        widget=ClearableFileInput(attrs={
            'onchange': "$('#upload-file-info').text(this.files[0].name)"
        })
    )

    def clean_file(self) -> Workbook:
        file = self.cleaned_data['file']
        content_type = file.content_type.split('/')[1]
        valid_content_type = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type
        xls_error = forms.ValidationError(_("The file must be a valid 'XLSX' excel file"), code='invalid')
        if ".xlsx" not in file.name or not valid_content_type:
            self.add_error('file', xls_error)
            return None

        try:
            workbook = load_workbook(file, read_only=True, data_only=True)
            return workbook
        except (KeyError, zipfile.BadZipFile,):
            self.add_error('file', xls_error)
