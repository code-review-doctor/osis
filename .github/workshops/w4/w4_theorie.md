# Partie 1



# Partie 2
https://enterprisecraftsmanship.com/posts/fail-fast-principle/


 [W4] Quid des services de "check" avant validation ? Exemple : program_management.ddd.service.read.check_version_name_service.check_version_name
Comment gérer les cas de "rapports" à générer quand on rempli un Arbre ? Pattern mediator ? Principe de Logger + subscriber / listener

Proposition pour gérer les rapport :

- Obliger tous nos validatorList d'hériter de MultipleExceptionBusinessListValidator
- Créer un service (read) qui effectue l'action métier à checker (DomainObject.business_action())
- Toute action métier raise une MultipleBusinessExceptions, qui peuvent être catchées côté client
- Nomenclature : check_<application_service_name>
- Exemple : 
```python
import program_management.ddd.command
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.repositories.program_tree import ProgramTreeRepository


# ddd/service/read 
def check_paste_node_service(check_command: program_management.ddd.command.CheckPasteNodeCommand) -> None:
    identity = ProgramTreeIdentity(code=check_command.code, year=check_command.year)
    
    tree = ProgramTreeRepository().get(identity)
    
    tree.paste_node(check_command)

```