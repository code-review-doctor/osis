#set( $UseCase = ${StringUtils.removeAndHump($NAME)} )
#set( $Aggregate = ${StringUtils.removeAndHump($aggregate)} )
from typing import Optional, List

class ${NAME}(
        cmd: '${UseCase}Command',
        ${aggregate}_repository: 'I${Aggregate}Repository',
) -> '${Aggregate}Idendity':
    # GIVEN
    ${aggregate} = ${aggregate}_repository.get(entity_id=cmd.entity_id)

    # WHEN

    # THEN


    return entity_id