# 5. Use UUID over ID on URL path

Date: 2021-11-18

## Status

Accepted

## Context

Using database ID in path increase the risk of "Insecure Direct Object References" 
(cf. https://wiki.owasp.org/index.php/Top_10_2013-A4-Insecure_Direct_Object_References) according to OWASP.


## Decision

We will use natural key in path as preferred alternative.
If we cannot determine a natural key, we will use UUID in Path

## Consequences

+) In case of natural key, it's a human-readable format.

-) In case of UUID, it's difficult to read for a human.