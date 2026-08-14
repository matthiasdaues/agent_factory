---
id: FAGAN-0009
source: fagan-review
severity: major
category: defect
artifact: docs/proposals/implemented/research-survey-mode.md:3
status: resolved
traces: [ST-0060, ST-0061, ST-0062, ST-0064, Survey Mode]
---

# Survey design contradicts the implemented artifact boundary

**What is wrong:** The changed design still labels survey mode "not yet
implemented" and states as a non-goal that survey reuses the falsification
final-report schema instead of adding a schema family. The same document's
implementation decisions, the completed stories, and the committed code all
define dedicated survey plan and report schemas. The design therefore gives
opposite instructions about the system's actual contract.

**Fix:** Mark the design as implemented and replace the stale schema non-goal
with the actual boundary: survey uses dedicated plan and report contracts while
reusing the shared brief and source-record contracts; falsification schemas
remain unchanged.

**Resolution:** The design now records implementation by ST-0060 through
ST-0064 and states the shipped boundary: dedicated survey plan and report
schemas reuse only the shared brief and source-record contracts, without
weakening the falsification plan or final-report schemas. A regression rejects
the stale implementation status and final-report reuse claim.
