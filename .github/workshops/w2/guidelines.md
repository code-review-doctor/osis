## Guidelines

- FAQ : Question : Comment savoir si on doit filtrer en mémoire (domaine) ou via Repository.search/filter via queryset ?
    - Tendre vers des queries génériques, et n'aller dans le spécifique QUE s'il y a des problèmes de perf
    Ajouter guideline : GENERIGQUE au maximum dans repository
    plus il y a de filtres, plus on se demande "est-ce que c'est du métier" 
    et "est-ce que notre nom de fonction est explicicte et respecte le single responsibility principle"?

### Domain

- [w2] Un domaine peut avoir plusieurs aggrégats
- [w2] Un domaine ne peut faire aucune référence à un élément extérieur (même par inversion de dépendance)
=> Objectif : pas de mock. S'il est nécessaire de mock notre domaine, il n'est pas pure.

- Encapsule l'ensemble des règles métier (cf. lien vers doc technique "domaine pure et complet")

- [W2] Toute exception lancée par le domaine doit être une BusinessException

-------------------------------

### Domain services

- [W2] : ajouter lien vers FAQ ou reference "pure and complete domain"

Code pas propre, à proscrire : 
- [W2] Appeler des DomainService d'un autre domain

- [W2] Pourquoi ne pas utiliser l'injection de dépendance avec les DomainService? 
    - Car un domaine service ne fait pas partie de la couche "domaine"
    - Note : quid si domain service "pure" (pas d'accès à repo?) 

- Regroupe les **objets** qui ne représentent pas un `ValueObject` ou une `Entity` du domaine. 
Exemple : un calculateur de taxe

- Contient de la logique métier

- Utiliser injection de dépendances si le domain service a besoin d'un repository

- Ne connaît pas la base de données (pas de querysets)!

- Renvoie uniquement des types primitifs, des Entity ou ValueObjects

- Peut recevoir une Entity, ValueObject, type_primitif ou repositories 

- Accès : 
    - couche Domain
    - couche Repository
    - couche BusinessException


-------------------------------

### Repository

Code pas propre, à proscrire : 
- [W2] raise une exception business dans un repository --> ça doit être un validator ! => Question : ne devrait-on pas créer un validateur "générique", qui génère un message d'erreur générique pour toute autre erreur non anticipée ? (enfait non... sinon plsu de stacktrace et Sentry plus nécessaire ! )
- [W2] [FAQ] Un repository peut-il raise une Exception business ?
    - ==> NON
    - Les exceptions "infra" (IntergityError, etc...) on laisse péter pour garder la stacktrace précise

- [W2] Pas de get_or_create / update_or_create pour les Entities mis uniquement pour les values objetcs 

-------------------------------

### Application services

Code pas propre, à proscrire : 
- [W2] des try-except dans un service
- [W2] des conditions et du code algorithmic dans un service


- [W2] Ne peut pas être modifié ! (Sauf en cas de bug). Un application service étant un use case, son contenu ne devrait jamais être modifié - sauf si le use case métier a changé.

