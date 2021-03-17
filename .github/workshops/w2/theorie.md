# Partie 1 : DDD : domaine "pure" et domaine "complet"

## Domaine complet : définition

- Un domaine est complet ssi il contient toute la logique métier de l'application

- Cas d'utilisation : modifier l'email d'un utilisateur

```python
from osis_common.ddd import interface
import attr

# Domain
@attr.s(slots=True)
class Company(interface.Entity):
    domain_name = attr.ib(type=str)
    
    def is_email_corporate(self, email: str) -> bool:
        email_domain = email.split('@')[1]
        return email_domain == self.domain_name


@attr.s(frozen=True, slots=True)
class UserIdentity(interface.Entity):
    username = attr.ib(type=str)


@attr.s(slots=True)
class User(interface.RootEntity):
    entity_identity = attr.ib(type=UserIdentity)
    company = attr.ib(type=Company)
    email = attr.ib(type=str)

    def change_email(self, new_email: str):
        if not self.company.is_email_corporate():
            raise interface.BusinessException("Incorrect email domain")
        self.email = new_email



#_____________________________________________________________________________________


# Application Service
def change_email_service(cmd: interface.CommandRequest) -> 'interface.EntityIdentity':
    repository = UserRepository()
    # Given
    user = repository.get(UserIdentity(username=cmd.username))
    
    # When
    user.change_email(new_email=cmd.email)

    # Then
    repository.update(user)
    
    return user.entity_identity
```

- "Domain logic fragmentation" est l'opposé d'un domaine complet : lorsque la logique métier (ici, `is_email_corporate`)
appartient à une autre couche que le domaine métier (couche de services, couche repository...)


<br/><br/><br/><br/><br/><br/><br/><br/>



## Domaine pure : définition

- Un domaine est "pure" ssi
    - il n'a aucune dépendance externe ou à d'autres couches de code
    - il dépend uniquement de types primitifs ou d'autres classes du domaines

- "Dépendance externe" signifie tout service (classes, fonction...) qui ne fait pas partie du domaine. Exemples :
    - base de données
    - gestion de fichiers
    - envoi de mail
    - envoi de messages (queues)

- Cas d'utilisation : règle métier : interdit de modifier si l'email existe déjà

- Essai n°1 : vérifier cette règle dans l'application service
```python
from osis_common.ddd import interface
import attr

# Application Service
def change_email_service(cmd: interface.CommandRequest) -> 'interface.EntityIdentity':
    repository = UserRepository()
    # Given
    if repository.search(email=new_email):
        raise interface.BusinessException("Email already exists")

    user = repository.get(UserIdentity(username=cmd.username))
    
    # When
    user.change_email(new_email=cmd.email)

    # Then
    repository.update(user)
    
    return user.entity_identity

```


- Notre implémentation rend-elle notre domaine pure ?
- Notre implémentation rend-elle notre domaine complet ?


<br/><br/><br/><br/><br/><br/><br/><br/>

- Essai n°2 : Injection du repository dans le domain

```python
from osis_common.ddd import interface
import attr

# Domain
@attr.s(slots=True)
class User(interface.Entity):
    entity_identity = attr.ib(type=UserIdentity)
    company = attr.ib(type=Company)
    email = attr.ib(type=str)

    def change_email(self, new_email: str, repository: UserRepository):
        if not self.company.is_email_corporate():
            raise interface.BusinessException("Incorrect email domain")
        if repository.search(email=new_email):
            raise interface.BusinessException("Email already exists")
        self.email = new_email



# Application Service
def change_email_service(cmd: interface.CommandRequest) -> 'interface.EntityIdentity':
    repository = UserRepository()
    # Given
    user = repository.get(UserIdentity(username=cmd.username))
    
    # When
    user.change_email(new_email=cmd.email, repository=repository)

    # Then
    repository.update(user)
    
    return user.entity_identity

```

- Notre implémentation rend-elle notre domaine pure ?
- Notre implémentation rend-elle notre domaine complet ?
 


<br/><br/><br/><br/><br/><br/><br/><br/>


- Essai n°3 : passer la liste des utilisateurs existants à notre domaine

```python
from osis_common.ddd import interface
import attr

# Application Service
def change_email_service(cmd: interface.CommandRequest) -> 'interface.EntityIdentity':
    repository = UserRepository()
    # Given
    all_users = repository.search()
    user = repository.get(UserIdentity(username=cmd.username), all_users=all_users)
    
    # When
    user.change_email(new_email=cmd.email)

    # Then
    repository.update(user)
    
    return user.entity_identity


# Domain
@attr.s(slots=True)
class User(interface.Entity):
    entity_identity = attr.ib(type=UserIdentity)
    company = attr.ib(type=Company)
    email = attr.ib(type=str)

    def change_email(self, new_email: str, all_users: List['User']):
        if not self.company.is_email_corporate():
            raise interface.BusinessException("Incorrect email domain")
        if new_email in {u.email for u in all_users}:
            raise interface.BusinessException("Email already exists")
        self.email = new_email

```

- Quel inconvénient à cette solution ? 

<br/><br/><br/><br/><br/><br/><br/><br/>


## Trilemme

- Il est impossible de satisfaire les 3 concepts suivants : 
    - Domain complet
    - Domain pure
    - Performance

- Choix possibles :
    - Placer toutes les opérations de lecture et écritures aux limites d'une opération métier (sandwich pattern)
        - Domaine "pure" et "complet" **au détriment des performances**
    - Partager la logique métier entre le domaine et l'application service
        - Domaine "pure" et performances **au détriment d'un domaine "complet"**
    - Injecter les dépendances hors processus dans le domaine
        - Domaine "complet" et performances **au détriment d'un domaine "pure"**

- Décision : 
    - Toujours privilégier un domaine "pure" et "complet" **au détriment des performances**

- Et si j'ai des problèmes de performances ? 
    - Privilégier un domaine "pure" et une application performante
        - Il est plus facile de maintenir un "domain logic fragmentation" plutôt que des dépendances externes (mocks, etc.)

        
<br/><br/><br/><br/><br/><br/><br/><br/>


## Questions

- Puis-je faire des `try-except` dans un application service ? 
- Puis-je placer un `if` dans un application service ?
- Puis-je lancer une BusinessException dans un application service ?
- Validator pour AcademicEvent est-il pure ?


## Exercices dans le code

- program_management.ddd.service.write.create_standard_program_tree_service.create_standard_program_tree
- program_management.ddd.service.write.paste_element_service.paste_element
- program_management.ddd.service.write.update_program_tree_version_service.update_program_tree_version
- education_group.ddd.service.write.delete_orphan_training_service.delete_orphan_training
- education_group.ddd.service.write.copy_training_service.copy_training_to_next_year
- program_management.ddd.service.write.up_link_service.up_link
- education_group.ddd.service.write.update_group_service.update_group



<br/><br/><br/><br/><br/><br/><br/><br/>

-------------------------------

<br/><br/><br/><br/><br/><br/><br/><br/>




# Partie 2 : DDD

## Différence entre "domain service" et "application service"

### Différence principale
- Les "domain services" contiennent de la logique métier alors que les "application services" n'en contiennent pas

### Application service
- Un application service représente un service qui effectue une action métier complète
- Given - when - then facilement identifiable
- Orchestre les appels dans les différentes couches (Repository, Domaine, DomaineService)



### Domain service
- Un domain service est un service qui encapsule une logique métier qui ne sait pas être représenté par un Entity ou à un ValueObject,
et qui ne représente pas un cas d'utilisation en tant que tel.
- Quand utiliser un DomainService ? 
    - Lorsque notre domaine ne peut pas être "complet" à cause des performances
        - Exemple : Vérifier si l'email d'un utilisateur existe (charger la liste de tous les utilisateurs en mémoire serait trop couteux)
    - Lorsque notre use case est dépendant d'un service technique / extérieur au domaine
        - Exemple : Générer d'un numéro de séquence (dépendance externe : base de données)
        - Exemple : Attacher un groupement dans le contenu d'une formation n'est possible que si le cache contient un groupement et peut être vidé (dépendance externe : système de cache)
        - Exemple : Calculer la date de fin de report d'une formation (dépendance externe : gestion des événements académiques)
    - Lorsque notre use case se comporte différemment en fonction du résultat d'un service extérieur
        - Exemple codé : 

```python
import attr
from decimal import Decimal
from osis_common.ddd import interface
from external.dependency.gateway import payment_gateway

# Domain
@attr.s(slots=True)
class ATM(interface.RootEntity):
    """Distributeur automatique de billets"""
    commission = attr.ib(type=Decimal)

    def calculate_amount_with_commission(self, amount: Decimal) -> Decimal:
        """Calcule le montant additionné de la commission propre à l'ATM"""
        return amount + self.commission


#-----------------------------------------------------------------------
# Application Service


# Application service (use case)
def withdraw_money(amount: Decimal) -> interface.EntityIdentity:
    """Retirer de l'argent sur un distributeur automatique de billets"""
    repository = ATMRepository()
    atm = repository.get()  # distributeur automatique de billets

    # Charge le montant avec une commission pour le facturer à travers un gateway
    amount_with_commission = atm.calculate_amount_with_commission(amount)
    result = payment_gateway.charge_payment(amount_with_commission)  # dépendance externe

    if result.is_failure():
        # Logique métier : ce "if" décide si l'argent sera finalement retiré de l'ATM ou non. 
        raise interface.BusinessException("Couldn't charge the payment from the gateway")
    
    atm.dispense_money(amount)
    
    repository.update(atm)
    
    return atm.entity_identity
    
```



<br/><br/><br/><br/><br/><br/><br/><br/>



- Solution : Domain service

```python
from decimal import Decimal
from osis_common.ddd import interface
from external.dependency.gateway import payment_gateway


# Application service
def withdraw_money(amount: Decimal) -> interface.EntityIdentity:
    repository = ATMRepository()
    atm = repository.get()  # distributeur automatique de billets
    AtmWithdrawMoney.withdraw_money(atm, amount, payment_gateway)
    repository.update(atm)
    
    return atm.entity_identity


# Domain service
class AtmWithdrawMoney(interface.DomainService):
    def withdraw_money(self, atm: ATM, amount: Decimal, payment_gateway) -> None:
        # Charge le montant avec une commission pour le facturer à travers un gateway
        amount_with_commission = atm.calculate_amount_with_commission(amount)
        result = payment_gateway.charge_payment(amount_with_commission)  # dépendance externe
    
        if result.is_failure():
            # Logique métier : ce "if" décide si l'argent sera finalement retiré de l'ATM ou non. 
            raise interface.BusinessException("Couldn't charge the payment from the gateway")
        
        atm.dispense_money(amount)


    
```


<br/><br/><br/><br/><br/><br/><br/><br/>


## Questions

- Puis-je appeler un application service dans un domain service ?
- Puis-je appeler un Domain service dans un application service ?
- Le code suivant est-il pure ?

```python
from ddd.domain.formation_enrollment import STATE1, STATE4, STATE8
from osis_common.ddd import interface

# Repository
class FormationEnrollmentRepository(interface.AbstractRepository):
    def search_enrollments_by_student(self, student_identity: StudentIdentity) -> List[FormationEnrollmentEntity]:
        data_from_db = EnrollmentDatabaseDjangoModel.objects.filter(
            student__registration_id=student_identity.registration_id,
            enrollment_state__in=[STATE1, STATE4, STATE8],
        )
        return [FormationEnrollmentEntity(...obj) for obj in data_from_db]




# ApplicationService
def search_enrollments_of_student(cmd: interface.CommandRequest) -> List[EnrollmentDatabaseDjangoModel]:
    student_identity = StudentIdentity(cmd.registration_id)
    return FormationEnrollmentRepository().search_enrollments_by_student(student_identity)

```



<br/><br/><br/><br/><br/><br/><br/><br/>



## Taille d'un agrégat (RootEntity)

- Rappel : un agrégat est un objet représentant un objet métier dans le domaine

- Rappel : un agrégat est public d'utilisation (accessible par les couches ayant accès à la couche "domaine")

- Un agrégat définit la limite d'une transaction dans notre application
    - Toute modification d'un agrégat **doit** être consistant en tout temps
    - Pas possible de persister un agrégat en plusieurs fois (transactions)

- Un grand agrégat 
    - amène la simplicité
        - plus facile d'assurer la consistance des invariants métier car par de dépendances externes
    - au détriment des performances
        - nécessaire de charger plus de données pour assurer la consistance des invariants
    - Domaine "complet" **au détriment des performances**

- Un petit agrégat 
    - amène la performance
        - possibilité de modifier les petits agrégats simultanément
        - pas besoin de charger toute la 
    - au détriment de la simplicité
        - la logique est séparée dans différents agrégats
        - dépendances externes dans les services (plus compliqué)
    - Application performante **au détriment d'un domaine "complet"**


- Taille d'un agrégat peut être influencée par le métier : 
    - Exemple : Un groupement peut-il exister sans ProgramTree ?
        - Oui -> transactions différentes : groupement peut être séparé de l'agrégat
    - Exemple : Les liens entre groupements peuvent-ils exister sans ProgramTree ?
        - Non -> transaction commune : les liens font partie intégrante du ProgramTree


## Conclusion (pour Osis)
- Privilégier les grands agrégats au détriment des performances
- Plusieurs agrégats possibles dans un même domaine
    - Note : un nombre grandissant d'agrégats dans un même domaine est signe que notre domaine 
    vise une problématique métier trop large



## Exercices

Les éléments suivants sont-ils réellement des DomainService ?
- program_management.ddd.domain.service.has_version_with_greater_end_year.HasVersionWithGreaterEndYear
- program_management.ddd.domain.service.get_last_existing_version_name.GetLastExistingVersion
- program_management.ddd.domain.service.generate_node_code.GenerateNodeCode
- program_management.ddd.domain.service.calculate_end_postponement.CalculateEndPostponement
- program_management.ddd.domain.service.get_node_publish_url.GetNodePublishUrl
- program_management.ddd.domain.service.validation_rule.FieldValidationRule