# Partie 1

## Appliquer les validateurs avant ou après exécution d'une action métier de l'objet du domaine ?

- Effectuer toujours les checks AVANT d'effectuer l'action métier sur l'objet
    - évite d'avoir un objet du domaine en état inconsistant (garantit qu'un objet du domaine tjr consistant)
    - facilite les tests unitaires
    - exemple : je ne peux modifier une UE que si son année académique est >= 2019
        - si validation après : 
            - UE modifiée --> état inconsistant --> difficulté de maintenance

- Note : un validateur ne peut jamais modifier les arguments qu'il reçoit pour sa propre validation
    - Exemple (à éviter) : self.transition_name = "TRANSITION " + transitionname (https://github.com/uclouvain/osis/pull/9680/files#)
    - Utiliser la librairie [python attrs](https://www.attrs.org/en/stable/) pour les validateurs

```python
import attr
from base.ddd.utils.business_validator import BusinessValidator


@attr.s(frozen=True, slots=True)
class MyBusinessValidator(BusinessValidator):
    object_used_for_validation = attr.ib(type=object)
    other_object_used_for_validation = attr.ib(type=object)

    def validate(self):
        if self.object_used_for_validation != self.other_object_used_for_validation:
            raise MyOwnValidatorBusinessException()

```



<br/><br/><br/><br/><br/><br/><br/><br/>



## Quid des validateurs dans les forms par rapport aux validateurs du domaine ?

### "Two steps validation" : Input Validation VS Contract Precondition

- "Input Validation" (precondition)
    - Mécanisme protégeant notre système contre les infiltrations de données invalides
    - Données autorisées en état invalides
    - "Bouclier de protection contre le monde extérieur"

- "Invariant validation" (code contract)
    - Suppose que les données à l'intérieur du système sont dans un état valide
    - Validation des invariants
    - "Bouclier" de prévention pour s'asurer de la consistance de nos objets

- Validateurs des Django forms == validateurs métier
     - Exception : pas de validateur sur les types de données
        - Assuré par les couches supérieures (ici, Django forms)

- Exemples de validateurs (domaine):
    - MyForm.credits doit être > 0
    - MyForm.sigle doit respecter le format `^[BEGLMTWX][A-Z]{2,4}[1-9]\d{3}`



<br/><br/><br/><br/><br/><br/><br/><br/>



## Comment afficher les BusinessExceptions dans les champs des forms ? Et comment génération un rapport avec toutes les erreurs ? Comment éviter de s'arrêter à la 1ère exception ?

### Principe du "Fail fast"

- Stopper l'opération en cours dès qu'une erreur inattendue se produit
- Objectif : application plus stable
    - Limite le temps de réaction pour corriger un bug
        - Erreur rapide = stacktrace = rollback (si activé) = information d'une erreur au plus tôt (à l'utilisateur)
    - Empêche de stocker des données en état inconsistant
    - Principe opposé : fail-silently (try-except)
- Exemple dans Osis : les validateurs



<br/><br/><br/><br/><br/><br/><br/><br/>



### ValidatorList + TwoStepsMultipleBusinessExceptionListValidator + DisplayExceptionsByFieldNameMixin

- Faire hériter `ValidatorList` de TwoStepsMultipleBusinessExceptionListValidator (implémentation ci-dessous)
    - Toute règle métier raise une BusinessException
    - Toute action métier raise une MultipleBusinessExceptions
    - toute MultipleBusinessExceptions gérable par le client (view, API...)

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

    # If True, exceptions that are not configured in `field_name_by_exception` will be displayed.
    # If False, exceptions that are not configured in `field_name_by_exception` will be ignored.
    display_exceptions_by_default = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.field_name_by_exception is None:
            self.field_name_by_exception = {}

    def call_application_service(self):
        raise NotImplementedError

    def save(self):
        try:
            if self.is_valid():  # to clean data
                return self.call_application_service()
        except MultipleBusinessExceptions as multiple_exceptions:
            self.display_exceptions(multiple_exceptions)

    def display_exceptions(self, exceptions_to_display: MultipleBusinessExceptions):
        """
        Add the exception messages in the fields specified in the 'field_name_by_exception' attribute.
        Add a generic error by default if no fields are defined.
        :param exceptions_to_display: MultipleBusinessExceptions
        :return: 
        """
        copied_list = list(exceptions_to_display.exceptions)
        for exception in copied_list:
            field_names = self.field_name_by_exception.get(type(exception), [])
            if self.display_exceptions_by_default and not field_names:
                self.add_error('', exception.message)
            else:
                for field_name in field_names:
                    self.add_error(field_name, exception.message)
            exceptions_to_display.exceptions.remove(exception)


#-------------------------------------------------------------------------------------------------------------------

@attr.s(slots=True)
class TwoStepsMultipleBusinessExceptionListValidator(BusinessListValidator):

    def get_input_validators(self) -> List[BusinessValidator]:
        raise NotImplementedError()

    def get_invariants_validators(self) -> List[BusinessValidator]:
        raise NotImplementedError()

    def __validate_inputs(self):
        self.__validate(self.get_input_validators())

    def __validate_invariants(self):
        self.__validate(self.get_invariants_validators())

    @staticmethod
    def __validate(business_validators):
        exceptions = set()
        for validator in business_validators:
            try:
                validator.validate()
            except MultipleBusinessExceptions as e:
                exceptions |= e.exceptions
            except BusinessException as e:
                exceptions.add(e)

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)

    def validate(self):
        self.__validate_inputs()
        self.__validate_invariants()




#-------------------------------------------------------------------------------------------------------------------
# ddd/service/write 
def update_training_service(command: UpdateTrainingCommand) -> 'TrainingIdentity':
    """Uniquement dans le cas d'un rapport"""
    identity = TrainingIdentity(acronym=command.acronym, year=command.year)
    
    training = TrainingRepository().get(identity)
    training.update(command)
    
    TrainingRepository().update(training)
    
    return identity



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
        return update_training_service(command)


#-------------------------------------------------------------------------------------------------------------------
# Django View
class View(...):

    def post(self, *args, **kwargs):
        form = CreateTrainingForm(request.POST)
        # if form.is_valid():
        form.save()
        if form.errors:
            redirect()
        else:
            pass

``` 


<br/><br/><br/><br/><br/><br/><br/><br/>



## Avantages

- Domaine complet : pas de duplication : logique métier encapsulée à un seul endroit
- Plus besoin de solutions compliquées côté "client" (Parsley)
- Pas d'ambiguïté sur quelle règle placer où : tout va dans le domaine
- Facilité de testing (toute la logique est au même endroit)

## Inconvénients

- Demande un mapping de nos types de BusinessException avec les clients des ApplicationService (django Forms, API...)
- Nécessite de mettre tous les champs required=False dans les forms

<br/><br/><br/><br/><br/><br/><br/><br/>



## Validateurs génériques

- (à implémenter et à intégrer dans la lib DDD)
    - RequiredFieldsValidator
    - MaximumValueValidator
    - MinimumValueValidator
    - MaximumLengthValidator
    - MinimumLengthValidator
    - StringFormatValidator (regex)
    - ... à compléter ? 
