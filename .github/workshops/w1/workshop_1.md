
## [W1] Formation 1

    Rappels théoriques :
        DDD : définition, objectif, philosophie, value et entity objects (langage commun entre tous les partis, ...) + exemple code (couches dans le code ProgramTree)
        CQS : définition + exemple code dans ProgramTree
    Workshop [contenu à développer]
        Objectif : développer ensemble les uses cases suivants dans le DDD avec nos guidelines d'aujourd'hui.
        Use case 1 : En tant qu'utilisateur facultaire, je veux créer une UE
        Use case 2 : En tant qu'utilisateur facultaire, je veux créer des parties magistrales et pratiques d'une UE et d'un partim

<p style="page-break-after: always;">&nbsp;</p>


### Application services

- [W1] Contrat 'un application service : type de retour, but (public et donc odit être robuste - possible à utiliser en envoyant n'importe quel param), raise exceptions (which type of exception ?)
- [W1] Classe BusinessException : faire une section dessus (application service ne lance que ces types d'exceptions là et pas d'autres)

- [W1] Ne peut pas être modifié ! (Sauf en cas de bug). Un application service étant un use case, son contenu ne devrait jamais être modifié - sauf si le use case métier a changé.


-------------------------------

### Repository

- [W1] Les repository peuvent instancier un objet du domaine ("DTO" via l'ORM)
- Vu le nombre de DTO qu'on a, je me demande si on ne doit pas penser à introduire une couche qui ne contient que des DTO. Cela allègerait le code des Services et Repositories.
Using DTO : not use 1 only bject from Front to DB

- [W1] Un repository doit-il exister pour toute Entity? Ou devrait il exister uniuqment pour 1 agregate root?
=> Notion de persistence et transaction dans un même aggrégat


-------------------------------

### Commandes

- [W1] Les paramètres d'une commande ne peuvent jamais être considérés comme une valeur "vérifiées" ; c'est comme un POST d'un client, on ne peut donc jamais passer des valeurs calculées "businessement" dans ces paramètres.



-------------------------------

## Cas d'utilisation 1
### user story
En tant qu'utilisateur facultaire, je veux créer une UE

### business rules
- Je peux encoder
    - année académique
    - sigle
    - crédits
    - type (Cours, stage, mémoire, autre collectif, autre individuel)
    - l'entité responsable (du cahier des charges) qui possède un sigle, un intitulé et une adresse
    - remarque (pour la faculté)
- Tous les champs sont obligatoires, sauf "remarque" 
- Les crédits doivent être supérieurs à 0
- Je ne peux pas créer une unité d'enseignement dont l'année académique < 2019-20
- Le calendrier académique de l'événement "gestion journalière" doit être ouvert à la date du jour (sans quoi je ne peux pas créer une UE)
- L'entité responsable doit être une entité liée à l'utilisateur
- Je ne peux pas créer une UE dont le sigle existe déjà (sur n'importe quelle année)
### TODO
- raise une exception business dans le repository (pour [W2]) (si entité existe pas dans le repository)

