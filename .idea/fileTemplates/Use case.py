#set( $UseCase = ${StringUtils.removeAndHump($NAME)} )
#set( $aggregate_lower = $aggregate.toLowerCase() )
#set( $Aggregate = ${StringUtils.removeAndHump($aggregate)} )
from typing import Optional, List

def ${NAME}(
        cmd: '${UseCase}Command',
        ${aggregate_lower}_repository: 'I${Aggregate}Repository',
) -> '${Aggregate}Identity':
    # GIVEN
    ${aggregate_lower} = ${aggregate_lower}_repository.get(entity_id=cmd.entity_id)

    # WHEN

    # THEN

    return entity_id