# Partie 1

## Appliquer les validateurs avant ou après modification de l'objet du domaine ?

- Effectuer toujours les checks AVANT d'effectuer l'action métier sur l'objet
    - évite d'avoir un objet du domaine en état inconsistant (garantit qu'un objet du domaine tjr consistant)
    - facilite les tests unitaires

- Question : qqn voit-il un avantage à faire le check après validation ? 


## Quid des validateurs dans les forms par rapport aux validateurs du domaine ?

- Validateurs des Django forms == validateurs métier. Exemples :
    - MyForm.credits doit être > 0
    - MyForm.sigle doit respecter le format `^[BEGLMTWX][A-Z]{2,4}[1-9]\d{3}`

## Comment afficher les BusinessExceptions dans les champs des forms ? Et comment génération un rapport avec toutes les erreurs ? Comment éviter de s'arrêter à la 1ère exception ?

### Fail fast

- [à développer] https://enterprisecraftsmanship.com/posts/fail-fast-principle/

### ValidatorList + MultipleExceptionBusinessListValidator + DisplayExceptionsByFieldNameMixin

- Faire hériter `ValidatorList` de [MultipleExceptionBusinessListValidator](https://github.com/uclouvain/osis/blob/dev/base/ddd/utils/business_validator.py#L122)
    - Toute action métier raise une MultipleBusinessExceptions, qui peuvent être catchées côté client
- Créer un service (read) qui effectue l'action métier à checker (DomainObject.business_action())
    - Nomenclature : check_<application_service_name>
- Utiliser `DisplayExceptionsByFieldNameMixin` dans nos Django forms

```python
class DisplayExceptionsByFieldNameMixin:
    """
    This Mixin provides a fonction 'display_exceptions' used to display business validation messages (business Exceptions)
    inside defined fields in the attribute 'field_name_by_exception'
    """

    # Dict[Exception, Tuple[FormFieldNameStr]]
    # Example : {CodeAlreadyExistException: ('code',), AcronymAlreadyExist: ('acronym',)}
    field_name_by_exception = None

    # If True, exceptions that are not configured in `field_name_by_exception` will be displayed as "default errors".
    # If False, exceptions that are not configured in `field_name_by_exception` will be ignored.
    display_exceptions_by_default = True

    def __init__(self):
        if self.field_name_by_exception is None:
            self.field_name_by_exception = {}

    def is_valid(self):
        try:
            self.call_application_service()
        except MultipleBusinessExceptions as multiple_exceptions:
            self.display_exceptions(multiple_exceptions)

        return super().is_valid()
    
    def call_application_service(self):
        raise NotImplementedError()

    def display_exceptions(self, exceptions_to_display: MultipleBusinessExceptions):
        """
        Add the exception messages in the fields specified in the 'field_name_by_exception' attribute.
        Add a generic error by default if no fields are defined.
        :param exceptions_to_display: MultipleBusinessExceptions
        :return: 
        """
        copied_list = list(exceptions_to_display.exceptions)
        for exception in copied_list:
            field_names = self.field_name_by_exception.get(exception, [])
            if self.display_exceptions_by_default and not field_names:
                self.add_error('', exception.message)
            else:
                for field_name in field_names:
                    self.add_error(field_name, exception.message)
            exceptions_to_display.exceptions.remove(exception)


#-------------------------------------------------------------------------------------------------------------------
# ddd/service/read 
def check_update_training_service(check_command: CheckUpdateTrainingCommand) -> None:
    identity = TrainingIdentity(acronym=check_command.acronym, year=check_command.year)
    
    training = TrainingRepository().get(identity)
    
    training.update(check_command)




#-------------------------------------------------------------------------------------------------------------------
# Django Form
class CreateTrainingForm(DisplayExceptionsByFieldNameMixin, forms.Form):
    code = UpperCaseCharField(label=_("Code"))
    min_constraint = forms.IntegerField(label=_("minimum constraint").capitalize())
    max_constraint = forms.IntegerField(label=_("maximum constraint").capitalize())

    field_name_by_exception = {
        CodeAlreadyExistException: ('code',),
        ContentConstraintMinimumMaximumMissing: ('min_constraint', 'max_constraint'),
        ContentConstraintMaximumShouldBeGreaterOrEqualsThanMinimum: ('min_constraint', 'max_constraint'),
        ContentConstraintMinimumInvalid: ('min_constraint',),
        ContentConstraintMaximumInvalid: ('max_constraint',),
    }

    def call_application_service(self):
        command = ...
        check_update_training_service.check_update_training(command)

``` 


## Validateurs génériques

- (à implémenter et à intégrer dans la lib DDD)
    - RequiredFieldsValidator
    - MaximumValueValidator
    - MinimumValueValidator
    - MaximumLengthValidator
    - MinimumLengthValidator
    - StringFormatValidator (regex)
    - ... à compléter ? 
