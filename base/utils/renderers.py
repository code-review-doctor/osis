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
import bootstrap3.renderers
import dal_select2.widgets


# Exclude ModelSelect2Multiple from inheriting bootstrap 3 "form_control" class.
# Otherwise the text and the clear button were not aligned inside the input.
class OsisBootstrap3FieldRenderer(bootstrap3.renderers.FieldRenderer):
    WIDGETS_NO_FORM_CONTROL = bootstrap3.renderers.FieldRenderer.WIDGETS_NO_FORM_CONTROL + \
                              (dal_select2.widgets.ModelSelect2Multiple, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_empty_warning_field_as_warning()

    def display_empty_warning_field_as_warning(self):
        if getattr(self.field.field, "warning", False) and self.field.form.is_bound and not self.field.value():
            self.form_group_class = " ".join([self.form_group_class, "has-warning"])
