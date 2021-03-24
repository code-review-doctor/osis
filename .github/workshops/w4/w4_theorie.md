# Partie 1

## Appliquer les validateurs avant ou après exécution d'une action métier de l'objet du domaine ?

- Effectuer toujours les checks AVANT d'effectuer l'action métier sur l'objet
    - évite d'avoir un objet du domaine en état inconsistant (garantit qu'un objet du domaine est toujours consistant)
    - facilite les tests unitaires
    - exemple : je ne peux modifier une UE que si son année académique est >= 2019
        - si validation après : 
            - UE modifiée --> état inconsistant --> difficulté de maintenance

- Note : un validateur ne peut jamais modifier les arguments qu'il reçoit pour sa propre validation
    - Exemple (à éviter) : `self.transition_name = "TRANSITION " + transition_name` (https://github.com/uclouvain/osis/pull/9680/files#)
    - Exemple (à éviter) : `self.field_to_validate = str(field_to_validate)`
    - Solution : Utiliser la librairie [python attrs](https://www.attrs.org/en/stable/) pour les validateurs


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

### "Two steps validation" : Input Validation VS Invariant Validation

- "Input Validation" (precondition)
    - Validation des entrées utilisateur ou tout processus externe
    - Mécanisme protégeant notre système contre les infiltrations de données invalides
    - Données autorisées en état invalides
    - "Bouclier de protection contre le monde extérieur"

- "Invariant validation" (code contract)
    - Validation des invariants
    - Suppose que les données à l'intérieur du système sont dans un état valide
    - "Bouclier" de prévention pour s'asurer de la consistance de nos objets

- Validateurs des Django forms == validateurs métier
     - Exception : pas de validateur sur les types de données
        - Assuré par les couches supérieures - internes à notre application (ici, Django forms)
        - Pourquoi ? 
            - Notre interface graphique empêche d'envoyer des données mal formatées
            - Si données mal formatées, c'est l'utilisateur qui corromp délibérément le système client
            - Notre système est protégé de toute façon : si les données entrées sont corrompues, une exception sera levée
                - exemple : champs crédits de type `str`, remarque de type "int"...
            - Pas nécessaire d'afficher une erreur bien formatée


<br/><br/><br/><br/><br/><br/><br/><br/>


### Exercices

Input validator ou invariant validator ? 
- Les crédits doivent être > 0
- Le sigle doit respecter le format `^[BEGLMTWX][A-Z]{2,4}[1-9]\d{3}`
- L'entité de charge doit être la même que l'entité d'attribution pour les types X, Y, Z
- Les champs A, B, C sont des champs obligatoires
- Le champ E doit être un entier, le champ F un décimal, le champ G une chaine de caractères
- Je ne peux pas modifier une UE < 2019-20
- Le campus sélectionné doit faire partie d'un campus appartenant à l'organisation "UCLouvain"
- Je ne peux pas attacher un groupement de type "liste au choix mineures" dans un groupement de type "tronc commun" 
- L'intitulé ne peut pas dépasser 255 caractères



<br/><br/><br/><br/><br/><br/><br/><br/>



## Comment afficher les BusinessExceptions dans les champs des forms ? Comment éviter de s'arrêter à la 1ère exception ? Et comment afficher toutes les erreurs au client ?

### Principe du "Fail fast"

- Stopper l'opération en cours dès qu'une erreur inattendue se produit
- Objectif : application plus stable
    - Limite le temps de réaction pour corriger un bug
        - Erreur rapide = stacktrace = rollback (si activé) = information d'une erreur au plus tôt (à l'utilisateur)
    - Empêche de stocker des données en état inconsistant
    - Principe opposé : fail-silently (try-except)
- Exemple dans Osis : les validateurs



<br/><br/><br/><br/><br/><br/><br/><br/>



### Solution : ValidatorList + TwoStepsMultipleBusinessExceptionListValidator + DisplayExceptionsByFieldNameMixin

- Faire hériter nos ValidatorLists de `TwoStepsMultipleBusinessExceptionListValidator` (implémentation ci-dessous)
    - Toute règle métier raise une BusinessException
    - Toute action métier (application service) raise une MultipleBusinessExceptions
    - Toute MultipleBusinessExceptions gérable par le client (view, API...)

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
    identity = TrainingIdentity(acronym=command.acronym, year=command.year)
    
    training = TrainingRepository().get(identity)
    training.update(command)
    
    TrainingRepository().save(training)
    
    return identity


#-------------------------------------------------------------------------------------------------------------------
# ddd/validators/validators_by_business_action.py
@attr.s(frozen=True, slots=True)
class UpdateTrainingValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    command = attr.ib(type=CommandRequest)
    existing_training = attr.ib(type=Training)
    existing_training_identities = attr.ib(type=List[TrainingIdentity])

    def get_input_validators(self) -> List[BusinessValidator]:
        return [
            AcronymRequiredValidator(self.command),
            TitleRequiredValidator(self.command),
            # ...
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            HopsValuesValidator(self.existing_training),
            StartYearEndYearValidator(self.existing_training),
            UniqueAcronymValidator(self.command.acronym, self.existing_training_identities),
            # ...
        ]



#-------------------------------------------------------------------------------------------------------------------
# Django Form
class UpdateTrainingForm(DisplayExceptionsByFieldNameMixin, forms.Form):
    code = UpperCaseCharField(label=_("Code"), required=False)
    min_constraint = forms.IntegerField(label=_("minimum constraint").capitalize(), required=False)
    max_constraint = forms.IntegerField(label=_("maximum constraint").capitalize(), required=False)

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


## Et si mon domaine ne peut pas être complet à cause des performances ?

- Utiliser un DomainService


```python

class UpdateTraining(interface.DomainService):
    def update(
            self,
            training: Training,
            command: UpdateTrainingCommand,
            repository: TrainingRepository
    ) -> None:
        business_exceptions = []
        if repository.acronym_exists(command.acronym):
            business_exceptions.append(AcronymAlreadyExistsException())

        try:
            training.update(command)
        except MultipleBusinessExceptions as e:
            business_exceptions += e.exceptions
        if business_exceptions:
            raise MultipleBusinessExceptions(exceptions=business_exceptions)


```


<br/><br/><br/><br/><br/><br/><br/><br/>


## Et les validation rules ? Et field reference ? Dans quelle(s) couche(s) devraient-ils se trouver ?

- Rappel : Validation rules = validation de certains champs selon le type de données

- Rappel : Field reference = accès ou non à certains champs selon le rôle de l'utilisateur


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
