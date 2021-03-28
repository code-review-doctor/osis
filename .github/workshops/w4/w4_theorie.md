# Partie 1

## Appliquer les validateurs avant ou après exécution d'une action métier de l'objet du domaine ?

- Effectuer toujours les validations **AVANT** d'effectuer l'action métier sur l'objet
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

### Validations effectuées dans les forms

- Types de champs ("nettoyage" des données sérialisées venant du request.POST)
- Champs requis
- Liste de choix / choix multiples


### Proposition 1 : valider ces champs en dehors de nos ApplicationService

Avantages :
- Réutilisation aisée des Django forms et leurs validations

Inconvénients :
- Duplication : ces validations devront être répétées pour chaque client 
- Exemples de client : 
    - Forms / Views Django
    - API
    - Scripts
- Rend notre domaine **incomplet** : la logique métier est séparée de notre domaine
- Difficulté de testing : métier à tester dans 2 couches différentes


### Proposition 2 : valider ces champs dans notre commande

Avantages : 
- Moins de duplication : tout client faisant appel à cette même action (Command) aura les mêmes validations

Inconvénients :
- Duplication : toute action métier (Command) plus large qui englobe cette action devra dupliquer ces mêmes validations
    - Exemple : CreateOrphanGroupCommand, CreateTrainingWithOrphanGroupCommand, CreateMiniTrainingWithOrphanGroupCommand
- Rend notre domaine **incomplet** : la logique métier est séparée de notre domaine
- Nécessite l'implémentation d'un mapping Command.errors <-> Form.errors
- Difficulté de testing : métier à tester dans 2 couches différentes


### Proposition 3 : valider ces champs dans notre domaine (ValidatorList)

Avantages : 
- Aucune duplication
- Domaine complet
- Facilité de testing (toute la logique est au même endroit)

Inconvénients :
- Pas possible de valider l'ensemble des invariants en même temps ("rapport")
    - Exemple : Je ne peux pas valider que mes crédits > 0 si le champ crédits = "Mauvaise donnée" ou crédits = None
- Demande un mapping de nos types de BusinessException avec les clients des ApplicationService (django Forms, API...)



<br/><br/><br/><br/><br/><br/><br/><br/>



### "Two steps validation" : Data contracts VS Invariant Validation

- "Data contract" (Input Validation)
    - Validation des données entrées par le client (tout processus externe)
    - Mécanisme protégeant notre système contre les infiltrations de données invalides
    - Données autorisées en état invalides
    - "Bouclier de protection contre le monde extérieur"
    - Inclus **uniquement** les validations suivantes : 
        - Type de champ (Integer, Dcimal, String...)
        - Required
        - ChoiceField

- "Invariant validation"
    - Validation des invariants
    - Suppose que les données à l'intérieur du système sont dans un état valide
    - "Bouclier" de prévention pour s'asurer de la consistance de nos objets
    - Inclus toutes les validations qui ne sont pas des "data contract"


<br/><br/><br/><br/><br/><br/><br/><br/>


### Quid de Parsley ? Si on "mappe" toutes nos erreurs à partir de nos validateurs ?

- On duplique UNIQUEMENT les "data contract validations", càd :
    - Type de champ dans les Form (CharField, IntegerField...)
    - Required
    - ChoiceField
    - ValidationRulesMixin


<br/><br/><br/><br/><br/><br/><br/><br/>



## Quid de ValidationRules et FieldReference ? Dans quelle(s) couche(s) devraient-ils se trouver ?
### Rappel : ValidationRules
- Django Model qui sauvegarde des règles de validations (métier et affichage) de champs de formulaires en DB
- Validation et affichage varient en fonction du l'état d'une donnée (par exemple, le type d'une UE)
- Variations possibles :
    - (métier) champ requis ou non
    - (métier) champ à valeur fixée (valeur par défaut bloquée et non éditable)
    - (métier) champ avec validation "regex"
    - (affichage) champs avec valeur par défaut
    - (affichage) champs avec help text (exemple)
    - (affichage) champs avec place holder (espace réservé)
- Initialisé à partir de `validation_rules.csv`


### Rappel : FieldReference
- Django Model qui sauvegarde des règles de validations (métier et affichage) de champs de formulaires en DB
- Permet l'édition ou non des champs d'un formulaire en fonction :
    - du rôle de l'utilisateur (central, facultaire... - nécessite l'accès aux groupes / permissions)
    - du contexte (événement académique, type d'UE) :
- Initialisé à partir de `field_reference.json`


### Intégration dans le DDD et dans les forms

#### ValidationRules

- À implémenter
    - dans les BusinessValidator dans notre domaine (domaine complet)
    - dans les Django Forms (existe déjà)
- Différence avec l'utilisation d'aujourd'hui :
    - le nommage des champs stockés dans `validation_rules.csv` seront des **termes métier**
    
#### FieldReference

- À implémenter
    - dans les DomainService (domaine complet)
    - dans les Django Forms (existe déjà)
- Différence avec l'utilisation d'aujourd'hui :
    - le nommage des champs stockés dans `field_reference.json` seront des **termes métier**

- Question : pourquoi ne pas réutiliser FieldReference dans nos validateurs (domaine) plutôt que dans un DomainService ?



<br/><br/><br/><br/><br/><br/><br/><br/>



## Comment afficher les BusinessExceptions (invariants) par champ dans un form ? Comment éviter de s'arrêter à la 1ère exception ? Et comment afficher toutes les erreurs au client ?

### Principe du "Fail fast"

- Stopper l'opération en cours dès qu'une erreur inattendue se produit
- Objectif : application plus stable
    - Limite le temps de réaction pour corriger un bug
        - Erreur rapide = stacktrace = rollback (si activé) = information d'une erreur au plus tôt (à l'utilisateur)
    - Empêche de stocker des données en état inconsistant
    - Principe opposé : fail-silently (try-except)
- Exemple dans Osis : les validateurs
    - Tout invariant métier non respecté lève immédiatement une exception



<br/><br/><br/><br/><br/><br/><br/><br/>



### Solution : ValidatorList + TwoStepsMultipleBusinessExceptionListValidator + DisplayExceptionsByFieldNameMixin

- Faire hériter nos ValidatorLists de `TwoStepsMultipleBusinessExceptionListValidator` (implémentation ci-dessous)
    - Toute règle métier (Validator) raise une BusinessException
    - Toute action métier (application service) raise une MultipleBusinessExceptions (ValidatorList)
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

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        """Contains ONLY validations for : 
        - Type of fields
        - ChoiceField (Enums fields)
        - RequiredFields
        - ValidationRules (cf. "validation_rules.csv")
        """
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
@attr.s(slots=True)
class UpdateTrainingValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    command = attr.ib(type=CommandRequest)
    existing_training = attr.ib(type=Training)
    existing_training_identities = attr.ib(type=List[TrainingIdentity])

    def get_data_contract_validators(self) -> List[BusinessValidator]:
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
class UpdateTrainingForm(ValidationRuleMixin, DisplayExceptionsByFieldNameMixin, forms.Form):
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
class CreateTrainingView(generics.View):

    def post(self, *args, **kwargs):
        form = CreateTrainingForm(request.POST)
        if form.is_valid():
            form.save()
            if not form.errors:
                return success_redirect()
        return error_redirect()

```


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



## Et si mon domaine ne peut pas être complet à cause des performances ?
## Et si mon use case nécessite des actions métier sur plusieurs aggrégats ?

- Utiliser un DomainService
- Si un rapport est nécessaire : utiliser 
TODO :: implémenter fonction pour try except les BusinessException de plusieurs acions métier pour en faire un rapport


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




Idée vers laquelle tendre : 
- Solution 1
- BusinessActionCannotBeExecutedException
- CommandRequest
    - is_valid()
        - Champs requis
        - Type des attributs
    - rapport
        - exceptions : List[BusinessException]
        - warnings : List[str]
        - changes : List[?]
- ApplicationService
    - if not my_command.is_valid() : raise MultipleBusinessExceptions(my_command.report.exceptions)
- Forms
    - Mixin pour gérer ces exceptions OU refaire ces mêmes validations dans les forms ?
- Domain
    - rapport
        - exceptions : List[BusinessException]
        - warnings : List[str]
        - changes : List[?]
- DomainService
    - if not my_command.is_valid() : raise BusinessActionCannotBeExecutedException(my_command.report.exceptions)
    

- Solution 2 : 
- CommandRequest
    - convert_to_learning_unit_data_dto()
    - convert_to_group_data_dto()
- FieldReference
    - content_type = AggregateRoot
    - field_name = attribut d'un aggregate (comment gérer les attributs imbriqués dans des sous-Entity / sous-valueObjects)
    - contexte = ? 
    
    
- Solution 3 (en parallèle au problème du ResponsibleEntity)
- Factory.build(dto) 
    - 1 seule fonction build() avec 1 DTO commun
        - LearningUnitRepository -> Queryset -> LearningUnitDto -> Builder -> LearningUnit
        - create_learning_unit_service -> CommandRequest -> LearningUnitDto -> Builder -> LearningUnit
- Une CommandRequest == Django Form
    - Responsable de la validation venant de l'extérieur
    - "code contract"
    - is_valid() : UNIQUEMENT :
        - Champs requis
        - Type des attributs
        - min/max_length pour les str ? (Mais devrait être dans le domaine - selon moi)
        - autres ?
        - raises MultipleBusinessException
            - permet de réutiliser le MixinForForms comme pour les BusinessExceptions
            - si pas raises MultipleBusinessException, autre solution : 
                - dupliquer UNIQUEMENT ces validations dans Forms et dans CommandRequest (le .isvalid( renvoie juste True/false dans ce cas)
- FieldReference :
    - Contenu : basé sur les champs du DomainObjectDTO
    - Réutilisé dans DomainService
        - DomainService car nécessite dépendance extérieure : les rôles et le calendrier académique
        - TODO : implémenter
    - Réutilisé dans Django Form (c'est gratuit c 'est deja implémenté) 
- ValidationRules :
    - Contenu : basé sur les champs du DomainObjectDTO (c'est au form d'y adhérer correctement)
    - Réutilisé dans CommandRequest
        - Pour Required
    - Réutilisé dans Validator
        - Pour regex
        - Pour fixé (valeur par défaut bloquée et non éditable)
    - (pas de réutilisation pour le champs set par défaut)
    - Problème : conflit : utilisé dans Django Forms, dans CommandRequest, et dans Validator






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

@attr.s(frozen=True, slots=True)
class TrainingDataContract(interface.DTO):
    pass
    




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
@attr.s(slots=True)
class UpdateTrainingValidatorList(MultipleExceptionBusinessListValidator):
    data_contract = attr.ib(type=CommandRequest)
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

