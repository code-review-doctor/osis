# 5. Use UUID over ID on URL path

Date: 2021-11-18

## Status

Accepted

## Context

Using database ID in path increase the risk of "Insecure Direct Object References" 
(cf. https://wiki.owasp.org/index.php/Top_10_2013-A4-Insecure_Direct_Object_References) according to OWASP.


## Decision

We will use natural key in path as preferred alternative.
If we cannot determine a natural key, we will use UUID in Path.
We cannot see UUID as protection so we will ensure that path is correctly protected by access check.

## Consequences

+) UUID is unique across resources.

+) UUID is difficult to guess.

-) The readability of a natural key might be a drawback. If a url is human-readable it might be easier for a human to attempt 
to modify it.
