# 3. Set LimitOffset as pagination style for API list

Date: 2021-11-18

## Status

Accepted

## Context

With more and more use of API, we've noticed that list returned can have multiple implementations / patterns.


## Decision

We will use LimitOffset as pagination style for all api which return list 
(cf. https://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination).

We will limit to return maximum 100 items in list (cf. https://github.com/uclouvain/osis/blob/dev/backoffice/settings/rest_framework/pagination.py#L30)

## Consequences

+) Consistent way of returning list throughout API

+) Provide maximum in order to prevent large data returned (Network/Database overload)

-) If client need to fetch all data, client need to make multiple call with next attribute