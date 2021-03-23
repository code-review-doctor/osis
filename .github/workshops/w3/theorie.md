
### Pour Osis : 
- Dossier `Factory` : regroupe l'ensemble des factories et builders pour nos objets du domaine
- Factory utilisée par Repository ET par application service
    - Dossier Factory situé en dehors du domaine
    - Évite la duplication de code pour la reconstitution de l'objet métier
    - Évite de charger un objet métier àpd d'un repository qui serait dans un état inconsistant

- Factory obligatoire pour tous nos objets `RootEntity` et `EntityIdentity`
    - Avantage : pas d'ambiguité : tout objet du domaine ne peut être instancié que via factory
    - Avantage : facilité e distinction privé - publique : ce qui est publique possède une factory
    - Avantage : pas besoin de faire de new Identity(...) -> juste appeler la factory
    - Inconvénient : pattern "factory" complexe pour des objets simples ("overengineering")

- Accès : 
    - Couche Domaine

- Nouvelle interface :

```python

class Builder(abc.ABC):

    def build_from_command(self, cmd: CommandRequest):
        raise NotImplementedError()

    def build_from_database_model(self, django_model_object: django.db.models.Model):
        raise NotImplementedError()

```