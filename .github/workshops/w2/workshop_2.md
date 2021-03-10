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


TODO partie 2 :: 
- Questions après théorie:
    - Puis-je appeler un Domain service dans un application service ?
    - Puis-je appeler un application service dans un domain service ?




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
(pour la dépendance entre aggregatesRoot)

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

