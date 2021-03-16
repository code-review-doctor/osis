
### forms

- Les validations des forms doivent se trouver dans les validators du domaine
    - Validateurs du domaine :
        - RequiredFieldsValidator
        - MaximumValueValidator
        - MinimumValueValidator
        

-------------------------------

### validateurs

- [W4] Un validateur ne peut pas modifier les arguments qu'elle reçoit pour sa propre validation. Exemple : self.transition_name = "TRANSITION " + transitionname (https://github.com/uclouvain/osis/pull/9680/files#)
- Effectuer toujours les checks dans l'action métier de l'objet du domaine
    - Exemples d'action métier : `ProgramTree.paste_node()`, `Program_tree.up_link()`, `Training.update_aims()`
- Effectuer toujours les checks AVANT d'effectuer l'action métier sur l'objet
        - évite d'avoir un objet du domaine en état inconsistant -> garantit qu'un objet du domaine tjr consistant (plus facile en mainteance)
        - facilite les tests unitaires
        - si après : oblige à dunder method "add_node" sans validation métier -> porte ouverte
        - Question : qqn voit-il un avantage à faire le check après validation ?
        
        
## Validators - references à ajouter

- https://lostechies.com/jimmybogard/2016/04/29/validation-inside-or-outside-entities/
- https://stackoverflow.com/questions/52883013/validation-in-domain-driven-design
- https://enterprisecraftsmanship.com/posts/validation-and-ddd/
- https://enterprisecraftsmanship.com/posts/code-contracts-vs-input-validation/


- estce une validaiton métier ou une validation technique ? 
    - technique ==> Forms / commands validations (couche "service" au niveau architecture)
    - métier ==> Couche "domaine" obligatoirement
    - Duplication ?
 