

- GUIDLELINE : AUCUNE aise BusinessEwception dans Aggreagtes, Entity ou valudeobject : c'est cptiré dans Validators


### forms

- Les validations des forms doivent se trouver dans les validators du domaine
    - Validateurs du domaine :
        - RequiredFieldsValidator
        - MaximumValueValidator
        - MinimumValueValidator


-------------------------------

### validateurs


GUIDELINE : nomencalture : valiators  :"SHOULD"

- Interdit de passer des Command dans un Validator 
--> Modifier interface BusinessValidator, qui peut recevoir uniquement : 
    - EntityRoot
    - Entity
    - ValueObject
    - EntityIdentity
    - Types primitifs

- [W4] Un validateur ne peut pas modifier les arguments qu'elle reçoit pour sa propre validation. Exemple : self.transition_name = "TRANSITION " + transitionname (https://github.com/uclouvain/osis/pull/9680/files#)
- Effectuer toujours les checks dans l'action métier de l'objet du domaine
    - Exemples d'action métier : `ProgramTree.paste_node()`, `Program_tree.up_link()`, `Training.update_aims()`

- Pas nécessaire de valider si une Entity existe déjà ou non. Exemple où la validation est "overkill" :
    - LearningUnit.Language
    - LearningUnit.Campus
    - LearningUnit.Entity

        
## Validators - references à ajouter

- https://lostechies.com/jimmybogard/2016/04/29/validation-inside-or-outside-entities/
- https://stackoverflow.com/questions/52883013/validation-in-domain-driven-design
- https://enterprisecraftsmanship.com/posts/validation-and-ddd/
- https://enterprisecraftsmanship.com/posts/code-contracts-vs-input-validation/
- https://enterprisecraftsmanship.com/posts/fail-fast-principle/
https://stackoverflow.com/questions/60535089/ddd-validation-for-existence-of-entity-in-other-bounded-contexts

 

- W4 EntityRoleField : pour filtrer la liste des entités => dans Forms
- W4 : vérifier le RequiredFieldsValidator (en l'état, 1 seul validateur sur tous les champs : empeĉhe d'avoir validation champs apr champs

- FAQ : comment déterminer si une règle métier doit se trouver dans Osis-role ou dans le domaine DDD ?
    - Si c'est une permission d'accès à une action (application service) dans le sens "puis-je ou non faire cette action?"
        - Osis-role
        - Exemples :
            - Je ne peux accéder à la fonctionnalité "X" que si je suis un utilisateur central
            - Je ne peux accéder à la modification d'une UE qui si son entité de charge fait partie des entités que je gère
            - Je ne peux accéder à la consultation des UEs que si j'ai la permission "can read learning unit"
  
    - Si c'est une règle en rapport avec le calendrier académique
        - Osis-role
        - (mais théoriquement : dans le DDD)
        - Exemple : 
            - Je ne peux accéder à la modification d'une UE que si l'événement "gestion journalière" est ouvert
     - Si c'est une règle en rapport avec le contenu des données postées (formulaire) par le client
        - Validation de contenu -> Invariant métier -> DDD (domaine - validator)
        - Exemple : 
            - Lorsque je crée une UE, son entité de charge doit être une entité qui fait partie des entités que je gère
