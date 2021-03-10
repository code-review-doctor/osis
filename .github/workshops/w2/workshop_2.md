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
            Use case 1 : En tant qu'utilisateur facultaire, je veux supprimer une UE
    Partie 2
        Théorie
            Différence entre un DomainService et un ApplicationService
            Dépendances entre aggregates dans un même domain (définition plus détaillée d'un modèle "pure")
        Workshop [contenu à développer]
            Use case 2 : En tant qu'utilisateur facultaire, je veux créer un Partim
            Use case 3 : En tant qu'utilisateur facultaire, je veux visualiser le nombre d'inscrits à une UE.


-------------------------------


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
(pour la dépendance entre aggregatesRoot)

### business rules
- Un partim possède les mêmes champs qu'une UE, mais les champs suivants sont hérités de l'UE
    - Sigle (de l'UE)
    - Année académique
    - Type
    - Sous-type de stage
    - Intitulé commun (fr)
    - Intitulé commun (en)
    - Entité responsable du cahier des charges
- Je ne peux pas créer un Partim "orphelin" (un partim doit être lié à une UE)
- Le sigle d'un partim est le même que celui d'une UE, suffixée obligatoirement par 1 lettre
- Je ne peux pas créer un partim si son sigle existe déjà
- La valeur initiale des "crédits" doit être la même que celle de l'UE (mais peut être changée) 



## Cas d'utilisation 3
### as a story
En tant qu'utilisateur facultaire, je veux visualiser le nombre d'inscrits à une UE. 
(pour DomainService)
### business rules
Aucune

