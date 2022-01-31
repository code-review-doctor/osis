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
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.db.models import Value
from django.db.models.functions import Concat, Lower
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from osis_document.contrib import FileField

from base.models.enums import person_source_type
from base.models.enums.civil_state import CivilState
from base.models.enums.groups import CENTRAL_MANAGER_GROUP, FACULTY_MANAGER_GROUP, SIC_GROUP, \
    UE_FACULTY_MANAGER_GROUP, CATALOG_VIEWER_GROUP, PROGRAM_MANAGER_GROUP, UE_CENTRAL_MANAGER_GROUP
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin, SerializableModelManager
from osis_common.utils.models import get_object_or_none

FILE_MAX_SIZE = None  # TODO : ??


class PersonAdmin(SerializableModelAdmin):
    list_display = ('get_first_name', 'middle_name', 'last_name', 'username', 'email', 'gender', 'global_id',
                    'changed', 'source', 'employee')
    search_fields = ['first_name', 'middle_name', 'last_name', 'user__username', 'email', 'global_id']
    list_filter = ('gender', 'language')
    exclude = ('id_card', 'passport', 'id_photo',)


class EmployeeManager(SerializableModelManager):
    def get_queryset(self):
        return super().get_queryset().filter(employee=True).order_by("last_name", "first_name")


class Person(SerializableModel):
    GENDER_CHOICES = (
        ('F', pgettext_lazy("female gender", "Female")),
        ('H', pgettext_lazy("gender male", "Male")),
        ('X', _('Other'))
    )
    SEX_CHOICES = (
        ('F', _('Female')),
        ('M', _('Male'))
    )

    YEAR_REGEX = RegexValidator(
        regex=r'^[1-2]\d{3}$',
        message=_('Birth year must be between 1000 and 2999'),
        code='invalid_birth_year'
    )

    objects = SerializableModelManager()
    employees = EmployeeManager()

    external_id = models.CharField(max_length=100, blank=True, default='', db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    global_id = models.CharField(max_length=10, blank=True, default='', db_index=True)
    gender = models.CharField(max_length=1, blank=True, default='', choices=GENDER_CHOICES)

    first_name = models.CharField(max_length=50, blank=True, default='', db_index=True)
    middle_name = models.CharField(max_length=50, blank=True, default='')
    last_name = models.CharField(max_length=50, blank=True, default='', db_index=True)
    email = models.EmailField(max_length=255, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    phone_mobile = models.CharField(max_length=30, blank=True, default='')
    language = models.CharField(max_length=30, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    birth_date = models.DateField(blank=True, null=True)

    civil_state = models.CharField(max_length=30, blank=True, default='', choices=CivilState.choices())
    sex = models.CharField(max_length=1, blank=True, default='', choices=SEX_CHOICES)
    first_name_in_use = models.CharField(max_length=50, default='', blank=True)
    birth_year = models.IntegerField(blank=True, null=True, validators=[YEAR_REGEX])
    birth_country = models.ForeignKey(
        'reference.Country',
        blank=True, null=True,
        verbose_name=_('Birth country'),
        on_delete=models.PROTECT,
        related_name='birth_persons'
    )
    birth_place = models.CharField(max_length=255, default='', blank=True)
    country_of_citizenship = models.ForeignKey(
        'reference.Country', verbose_name=_('Country of citizenship'), on_delete=models.PROTECT, blank=True, null=True
    )
    id_card = FileField(
        mimetypes=['image/jpeg', 'image/png', 'application/pdf'],
        max_size=FILE_MAX_SIZE,
        max_files=2,
        min_files=1,
        null=True
    )
    passport = FileField(
        mimetypes=['image/jpeg', 'image/png', 'application/pdf'],
        max_size=FILE_MAX_SIZE,
        max_files=2,
        min_files=1,
        null=True
    )
    last_registration_year = models.ForeignKey(
        'base.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    national_number = models.CharField(max_length=255, default='', blank=True)
    id_card_number = models.CharField(max_length=255, default='', blank=True)
    passport_number = models.CharField(max_length=255, default='', blank=True)
    passport_expiration_date = models.DateField(null=True, blank=True)
    id_photo = FileField(
        mimetypes=['image/jpeg', 'image/png'],
        max_size=FILE_MAX_SIZE,
        max_files=1,
        min_files=1,
        null=True
    )

    source = models.CharField(
        max_length=25, blank=True, null=True,
        choices=person_source_type.CHOICES,
        default=person_source_type.BASE
    )
    employee = models.BooleanField(default=False)
    managed_entities = models.ManyToManyField("Entity", through="EntityManager")

    def save(self, **kwargs):
        # When person is created by another application this rule can be applied.
        if hasattr(settings, 'INTERNAL_EMAIL_SUFFIX'):
            if settings.INTERNAL_EMAIL_SUFFIX.strip():
                # It limits the creation of person with external emails. The domain name is case insensitive.
                if self.source and self.source != person_source_type.BASE \
                        and settings.INTERNAL_EMAIL_SUFFIX in str(self.email).lower():
                    raise AttributeError('Invalid email for external person.')

        super(Person, self).save()

    def username(self):
        if self.user is None:
            return None
        return self.user.username

    def get_first_name(self):
        if self.first_name:
            return self.first_name
        elif self.user:
            return self.user.first_name
        return "-"

    @cached_property
    def is_central_manager(self):
        return self.user.groups.filter(name=CENTRAL_MANAGER_GROUP).exists() or self.is_central_manager_for_ue

    @cached_property
    def is_central_manager_for_ue(self):
        return self.user.groups.filter(name=UE_CENTRAL_MANAGER_GROUP).exists()

    @cached_property
    def is_faculty_manager(self):
        return self.user.groups.filter(name=FACULTY_MANAGER_GROUP).exists() or self.is_faculty_manager_for_ue

    @cached_property
    def is_faculty_manager_for_ue(self):
        return self.user.groups.filter(name=UE_FACULTY_MANAGER_GROUP).exists()

    @cached_property
    def is_catalog_viewer(self):
        return self.user.groups.filter(name=CATALOG_VIEWER_GROUP).exists()

    @cached_property
    def is_program_manager(self):
        return self.user.groups.filter(name=PROGRAM_MANAGER_GROUP).exists()

    @cached_property
    def is_sic(self):
        return self.user.groups.filter(name=SIC_GROUP).exists()

    @property
    def full_name(self):
        return " ".join([self.last_name or "", self.first_name or ""]).strip()

    def __str__(self):
        return self.get_str(self.first_name, self.last_name)

    @staticmethod
    def get_str(first_name, last_name):
        return " ".join([
            ("{},".format(last_name) if last_name else "").upper(),
            first_name or ""
        ]).strip()

    class Meta:
        permissions = (
            ("is_administrator", "Is administrator"),
            ("is_institution_administrator", "Is institution administrator "),
            ("can_edit_education_group_administrative_data", "Can edit education group administrative data"),
            ("can_add_charge_repartition", "Can add charge repartition"),
            ("can_change_attribution", "Can change attribution"),
            ('can_read_persons_roles', 'Can read persons roles'),
        )

    # TODO: Remove this property in dissertation app
    @cached_property
    def linked_entities(self):
        from learning_unit.auth.roles.central_manager import CentralManager
        from learning_unit.auth.roles.faculty_manager import FacultyManager
        from osis_role.contrib.helper import EntityRoleHelper

        return EntityRoleHelper.get_all_entities(self, {CentralManager.group_name, FacultyManager.group_name})

    # TODO: Remove this method in dissertation app
    def is_linked_to_entity_in_charge_of_learning_unit_year(self, learning_unit_year):
        requirement_entity_id = learning_unit_year.learning_container_year.requirement_entity_id
        if not requirement_entity_id:
            return False
        return requirement_entity_id in self.linked_entities


def find_by_id(person_id):
    return get_object_or_none(Person, id=person_id)


def find_by_user(user: User):
    try:
        return user.person
    except Person.DoesNotExist:
        return None


def get_user_interface_language(user: User) -> str:
    user_language = settings.LANGUAGE_CODE
    person = find_by_user(user)

    if person and person.language:
        user_language = person.language
    return user_language


def change_language(user, new_language):
    if new_language in (l[0] for l in settings.LANGUAGES):
        person = find_by_user(user)
        if person:
            person.language = new_language
            person.save()


def find_by_global_id(global_id):
    return Person.objects.filter(global_id=global_id).first() if global_id else None


def find_by_last_name_or_email(query):
    return Person.objects.filter(Q(email__icontains=query) | Q(last_name__icontains=query))


# FIXME Returns queryset.none() in place of None And Only used in tests !!!
# Also reuse search method and filter by employee then
def search_employee(full_name):
    queryset = annotate_with_first_last_names()
    if full_name:
        return queryset.filter(employee=True) \
            .filter(Q(begin_by_first_name__iexact='{}'.format(full_name.lower())) |
                    Q(begin_by_last_name__iexact='{}'.format(full_name.lower())) |
                    Q(first_name__icontains=full_name) |
                    Q(last_name__icontains=full_name))
    return None


def annotate_with_first_last_names():
    queryset = Person.objects.annotate(begin_by_first_name=Lower(Concat('first_name', Value(' '), 'last_name')))
    queryset = queryset.annotate(begin_by_last_name=Lower(Concat('last_name', Value(' '), 'first_name')))
    return queryset


def calculate_age(person):
    if person.birth_date is None:
        return None
    today = date.today()
    return today.year - person.birth_date.year - ((today.month, today.day) < (person.birth_date.month,
                                                                              person.birth_date.day))
