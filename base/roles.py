from base.auth.roles import entity_manager, program_manager, tutor
from osis_role import role

role.role_manager.register(entity_manager.EntityManager)
role.role_manager.register(program_manager.ProgramManager)
role.role_manager.register(tutor.Tutor)
