from osis_common.ddd import interface
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from workshops_ddd_ue.domain.exceptions import LearningUnitUsedInProgramTreeException
from workshops_ddd_ue.domain.learning_unit import LearningUnitIdentity


class LearningUnitCanBeDeleted(interface.DomainService):

    def validate(
            self,
            learning_unit_identity: 'LearningUnitIdentity',
            program_tree_repo: 'ProgramTreeRepository'
    ):
        self.__check_if_is_used_in_program_tree(learning_unit_identity, program_tree_repo)


    def __check_if_is_used_in_program_tree(
            self,
            learning_unit_identity: 'LearningUnitIdentity',
            program_tree_repo: 'ProgramTreeRepository'
    ):
        node_identity = NodeIdentity(code=learning_unit_identity.code, year=learning_unit_identity.academic_year.year)
        programs_using_learning_unit = program_tree_repo.search_from_children([node_identity])
        if programs_using_learning_unit:
            identities = [prog.entity_id for prog in programs_using_learning_unit]
            raise LearningUnitUsedInProgramTreeException(learning_unit_identity, identities)
