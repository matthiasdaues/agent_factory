---
id: RECON-0001
source: reconcile
artifact: docs/spec/production-grade-remote-command-foundation.feature:222
traces: [DOM-03, ST-0003B]
---

# The Scenario "Non-active Domain rejects Task Draft publication" has no implementing code

**What is wrong:** The Rule "Only an active Domain makes its Tasks eligible"
(DOM-03) contains the Scenario "Non-active Domain rejects Task Draft
publication". No code implements it. There is no publication operation yet, so
the Scenario has no `@`-reference. The other three Scenarios of the Rule are
implemented and referenced. The Rule therefore stays `specified` in the scope
map.

**Fix:** Implement the publication gate with
[ST-0003](../../backlog/ST-0003B.md). Publication must read the Domain state
through `DomainRegistryApi.get_domain_state` and reject a non-`ACTIVE` Domain
before it creates a Task Version. Then add the `@`-reference to the Scenario,
set the QA strategy row `DOM-03-API-02` to `implemented`, move DOM-03 to
`implemented` in the scope map, and set this finding to `resolved`.
