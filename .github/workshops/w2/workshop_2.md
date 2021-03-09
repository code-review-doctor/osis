## [W2] Formation 2

    Partie 1 
        Théorie
            Domaine "pure" et domaine "complet"
            Pattern "Sandwich"
        Workshop
            Sur base du code dans "program_management" et ensuite du code du workshop 1 :
                Déterminer si notre domaine est "pure" et/ou "complet"
                Refactorer notre code (UE) pour le rendre "pure" (si nécessaire)
                Refactorer notre code (UE) pour le rendre "complet" (si nécessaire)
    Partie 2
        Théorie
            Différence entre un DomainService et un ApplicationService
            Dépendances entre aggregates dans un même domain (définition plus détaillée d'un modèle "pure")
        Workshop [contenu à développer]
            Use case 1 : En tant qu'utilisateur facultaire, je veux supprimer une UE
            Use case 2 : En tant qu'utilisateur facultaire, je veux créer un Partim
            Use case 3 : En tant qu'utilisateur facultaire, je veux visualiser le nombre d'inscrits à une UE.

- Questions pendant pratique :
    - Validator sur AcademicEvent est-il pure ? 

TODO partie 2 :: 
- Questions après théorie:
    - Puis-je appeler un Domain service dans un application service ?
    - Puis-je appeler un application service dans un domain service ?




-------------------------------

### Domain

- [w2] Un domaine peut avoir plusieurs aggrégats
- [w2] Un domaine ne peut faire aucune référence à un élément extérieur (même par inversion de dépendance)
=> Objectif : pas de mock. S'il est nécessaire de mock notre domaine, il n'est pas pure.

-------------------------------

### Domain services

- [W2] : ajouter section pour "domain service" + ajouter les couches qui ont accès au domainservice (application service uniquement)

- [W2] : ajouter lien vers FAQ ou reference "pure and ocmplete domain"

Code pas propre, à proscrire : 
- [W2] Appeler des DomainService d'un autre domain

- [W2] POurquoi ne pas utiliser l'injection de dépendance avec les DomainService? (Car sans l'inject, l'appel à un DomainService reste un lien direct vers la DB...). Avantage : on sait tout de suite quelles fonctions font appel à la DB (via ses aprams de type Repo ou DomaiNService)

- Regroupe les **objets** qui ne représentent pas un `ValueObject` ou une `Entity` du domaine. 
Exemple : un calculateur de taxe

- Accès : 
    - couche Domain
    - couche Repository


-------------------------------

### Repository

Code pas propre, à proscrire : 
- [W2] raise une exception business dans un repository --> ça doit être un validator ! => Question : ne devrait-on pas créer un validateur "générique", qui génère un message d'erreur générique pour toute autre erreur non anticipée ? (enfait non... sinon plsu de stacktrace et Sentry plus nécessaire ! )
- [W2] [FAQ] Un repository peut-il raise une Exception business ?


-------------------------------

### Application services

Code pas propre, à proscrire : 
- [W2] des try-except dans un service
- [W2] des conditions et du code algorithmic dans un service


-------------------------------

#PARTIE 2

## Cas d'utilisation 1
### as a story
En tant qu'utilisateur facultaire, je veux supprimer une UE
(pour DomainService + domaine "incomplet")

### business rules
- Je ne peux pas supprimer l'UE si 
    - je suis hors de la période "gestion journalière" du calendrier académique
    - l'UE est utilisée dans un programme type


## Cas d'utilisation 2
### as a story
En tant qu'utilisateur facultaire, je veux créer un partim
(pour la dépendances entre aggregatesRoot)

### business rules
- Ajout d'un concept de sous-type (complet, partim) d'UE
- Possède les même champs qu'une UE
- Je ne peux pas modifier le sous-type et le type d'une UE
- Si l'UE est de type COURS, stage, mémoire => crédits décimaux non autorisés.
Dans les autres cas, les crédits décimaux sont autorisés.



## Cas d'utilisation 3
### as a story
En tant qu'utilisateur facultaire, je veux visualiser le nombre d'inscrits à une UE. 
(pour DomainService)
### business rules
Aucune

