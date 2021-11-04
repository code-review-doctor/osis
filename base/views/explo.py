from django import forms
from django.forms.utils import ErrorList
from django.views.generic import TemplateView, DetailView
from django_filters import filters

from base.models.learning_unit_year import LearningUnitYear
from dal import autocomplete


class CodeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        print('ici')
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return LearningUnitYear.objects.none()

        qs = LearningUnitYear.objects.all()

        if self.q:
            qs = qs.filter(acronym__istartswith=self.q)

        return qs


class ExploForm(forms.ModelForm):

    codes = forms.ModelChoiceField(
        queryset=LearningUnitYear.objects.all(),
        widget=autocomplete.ModelSelect2(url='code-autocomplete')
    )

    class Meta:
        model = LearningUnitYear
        fields = ('__all__')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
        print('init')
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute, renderer)
        # self.fields['codes'].initial = LearningUnitYear.objects.all()


#
# class ExploForm(forms.Form):
#
#     codes = filters.ModelChoiceFilter(
#         queryset=LearningUnitYear.objects.filter(id__in=([1,2,3,4,5,6,7,8,])),
#         required=True,
#         label='Code',
#         widget=autocomplete.ModelSelect2Multiple(
#             url='education_group_type_autocomplete',
#             forward=['category'],
#         ),
#     )
#
#     def send_email(self):
#         # send email using the self.cleaned_data dictionary
#         pass


class Explo(TemplateView):
    template_name = "explo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = "test"
        context['form'] = ExploForm()
        return context
