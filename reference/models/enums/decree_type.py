from base.models.utils.utils import ChoiceEnum


# No translation provided because it's map with column name on reference_decree.
# Check if reference_decree is relevant?
class DecreeType(ChoiceEnum):
    BEFORE_BOLOGNE = "Avant bologne"
    BOLOGNE = "Bologne"
    PAYSAGE = "Paysage"
