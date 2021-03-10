
## [W1] Formation 1

    Rappels théoriques :
        DDD : définition, objectif, philosophie, value et entity objects (langage commun entre tous les partis, ...) + exemple code (couches dans le code ProgramTree)
        CQS : définition + exemple code dans ProgramTree
    Workshop [contenu à développer]
        Objectif : développer ensemble les uses cases suivants dans le DDD avec nos guidelines d'aujourd'hui.
        Use case 1 : En tant qu'utilisateur facultaire, je veux créer une UE
        Use case 2 : En tant qu'utilisateur facultaire, je veux créer des parties magistrales et pratiques d'une UE et d'un partim

<p style="page-break-after: always;">&nbsp;</p>


-------------------------------

## Cas d'utilisation 1
### user story
En tant qu'utilisateur facultaire, je veux créer une UE

### business rules
- Je peux encoder
    - année académique
    - intitulé commun en fr
    - intitulé spécifique en fr
    - intitulé commun en anglais
    - intitulé spécifique en anglais
    - sigle
    - crédits
    - type (Cours, stage, mémoire, autre collectif, autre individuel, thèse)
    - sous-type de stage (stage d'enseignement, stage clinique, stage professionnel, stage de recherche)
    - l'entité responsable (du cahier des charges) qui possède un sigle, un intitulé et une adresse
    - périodicité
    - langue
    - remarque de la faculté (non publiée)
    - remarque pour publication
    - remarque pour publication (en anglais)

- Je ne peux pas créer une unité d'enseignement dont l'année académique < 2019-20
- Tous les champs sont obligatoires, sauf
    - les 3 remarques
    - "intitulé commun en anglais"
    - "intitulé spécifique en anglais"
- sous-type stage obligatoire si type=stage, sinon vide obligatoire
- Crédits > 0
- Le calendrier académique de l'événement "gestion journalière" doit être ouvert à la date du jour (sans quoi je ne peux pas créer une UE)
- L'entité responsable
    - Doit être une entité liée à l'utilisateur
    - Doit respecter une des 2 conditions 
        - être de type SECTOR, FACULTY, SCHOOL, DOCTORAL_COMMISSION
        - avoir un sigle = ILV, IUFC, CCR ou LLL
- Je ne peux pas créer une UE dont le sigle existe déjà (sur n'importe quelle année)
- La langue doit être "français" par défaut
- La périodicité doit être "Annuelle" par défaut
- Le code doit être composé en 3 parties : 
    - Le site (1 lettre)
    - Partie alphabétique (2 à 4 lettres)
    - Partie numérique (4 chiffres - dont 1er != 0)


