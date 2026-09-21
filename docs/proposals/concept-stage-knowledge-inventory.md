---
scope: global
schema_version: 2
status: draft
owner: Agent Factory maintainers
created: 2026-09-14
updated: 2026-09-14
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - .agent-factory/factory/docs/factory-guide.md
    - .agent-factory/factory/agents/virgil.md
    - .agent-factory/factory/playbooks/greenfield-development.md
    - .agent-factory/factory/playbooks/brownfield-onboarding.md
    - .agent-factory/factory/skills/capture-context/SKILL.md
    - .agent-factory/factory/rulebooks/templates/
    - .agent-factory/factory/rulebooks/schemas/

governance:
  assurance: high
  risk_domains:
    - compatibility
    - operations
    - reliability

estimate:
  as_of: 2026-09-14
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Concept Stage Knowledge Inventory

## Summary

Add a formal Concept stage before Requirements. The stage inventories the
knowledge needed to manage a development project without claiming that all
knowledge is available at project inception.

Each knowledge obligation has an explicit state, owner, source, risk, and
resolution point. The stage ends when the project is ready for requirements
work, not when it is ready for implementation.

## Original analysis

• Short answer: the concept stage can inventory all required knowledge areas, but it cannot—and should not—claim that all necessary knowledge is already
known.

The useful target is:

> A complete inventory of knowledge obligations, with every item either known, referenced, explicitly unknown, deferred, or not applicable.

That is compatible with iSAQB and lifecycle standards. “Complete project knowledge before development” is not.

## Standards perspective

iSAQB is primarily an architecture qualification framework, not a project-management standard. Its current Foundation curriculum expects architects to
address stakeholders and concerns, functional and quality requirements, constraints, context, decisions, interfaces, cross-cutting concepts, trade-offs, and
risks. iSAQB CPSA-F curriculum

Crucially, iSAQB REQ4ARC says architects do not need all requirements and constraints at the beginning. They need the important architecture drivers early
and should refine the rest just in time. iSAQB REQ4ARC curriculum

Other standards broaden the picture:

- ISO 21502 adds benefits, outcomes, governance, planning, control, risks, issues, change, and information management.
- ISO/IEC/IEEE 15288:2023 covers the entire lifecycle—conception through retirement—and explicitly treats processes as iterative and concurrent.
- ISO/IEC/IEEE 29148 adds requirements management, validation, and traceability throughout the lifecycle.
- arc42 provides an appropriate architecture inventory: goals, constraints, context, solution strategy, views, decisions, qualities, risks, and glossary.

Together they imply that a concept stage should establish coverage, ownership, and controlled uncertainty, not freeze the project’s knowledge.

## Assessment of Agent Factory today

Agent Factory does not currently define a formal Concept phase. Phase 0 contains conversational and utility work; the formal chain starts at Requirements.
That is visible in the Factory guide (.agent-factory/factory/docs/factory-guide.md:123).

Its current ingredients provide good but incomplete coverage:

| Knowledge area                           | Current coverage                                         | Assessment                                              |
| ---------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------- |
| Motivation and initial scope             | Proposal summary, motivation, scope, completion criteria | Good for a feature; weaker for an entire project        |
| Technical and domain knowledge           | Concern-based agent-context.md with Read: references     | Strong routing mechanism                                |
| Development rules                        | Branching, testing, review, security, scope discipline   | Strong engineering baseline                             |
| Requirements                             | PRD, scope map, Gherkin, supplementary specifications    | Strong, but belongs to the following Requirements phase |
| Architecture                             | arc42, Structurizr, ADRs, ATAM review                    | Strong, but deliberately later                          |
| Stakeholders and concerns                | Mostly implicit in interviews and later documentation    | Insufficiently inventoried                              |
| Business case and benefits               | Motivation only                                          | Partial                                                 |
| **Quality goals and scenarios**          | Mainly handled during requirements and architecture      | Too late for identifying early architecture drivers     |
| Project governance                       | Proposal owner and assurance classification              | Partial                                                 |
| Schedule, funding, capacity and skills   | Only limited estimates                                   | Missing                                                 |
| Dependencies, suppliers and procurement  | No systematic concept-stage inventory                    | Missing                                                 |
| **Risks, assumptions and opportunities** | Risk domains and open questions                          | No unified register                                     |
| Operations, support and retirement       | Infrastructure hints appear later                        | Weak                                                    |
| Knowledge ownership and freshness        | Read: paths exist                                        | Missing owners, review dates, and validity states       |

The agent-context documentation (.agent-factory/factory/docs/factory-guide.md:161) explicitly calls it a routing switchboard, not a knowledge base. That is the right
design, but it cannot alone prove knowledge coverage.

There is also artifact-contract drift: the current capture-context skill (.agent-factory/factory/skills/capture-context/SKILL.md:28) mandates one docs/agent-context.md
file and rejects the retired YAML model, while the greenfield playbook (.agent-factory/factory/playbooks/greenfield-development.md:59) still requires those YAML files and
the old capture-charter skill. A formal concept-stage gate would first need to resolve this inconsistency.

## Recommended concept-stage model

I would introduce a formal Phase 0: Concept/Inception, whose exit condition is “ready for requirements work,” not “ready to implement.”

Keep the artifact set small:

1. Concept brief

   - Problem or opportunity
   - Business goals and expected benefits
   - Target users
   - System boundary and operational context
   - Success and failure measures
   - Initial scope and explicit exclusions

2. Stakeholder and concern map

   - Stakeholder or role
   - Concern
   - Decision authority
   - Required involvement
   - Conflicts with other concerns

3. Driver register

   - Important functional capabilities
   - Top quality goals expressed as scenarios
   - Technical, organizational, legal and commercial constraints
   - Architecture hypotheses
   - Major risks and trade-offs

   This closely resembles the arc42 Architecture Inception Canvas.

4. Project-management outline

   - Governance and decision rights
   - Delivery approach
   - Funding and time boundaries
   - Team, skills and capacity assumptions
   - External dependencies and suppliers
   - Risk, issue and change processes
   - Communication and reporting
   - Release, operations, support and retirement assumptions

5. Knowledge-obligation register

   This is the piece that makes the inventory defensible. Each entry should contain:

   concern: Availability target
   category: quality
   status: unknown # known | unknown | deferred | not_applicable
   source: null
   owner: product-owner
   consumers: [requirements, architecture, operations]
   confidence: low
   risk_if_wrong: high
   resolution_by: before architecture review
   validation: stakeholder approval
   review_trigger: traffic forecast changes

docs/agent-context.md would then point agents to these authoritative artifacts rather than duplicate their contents.

## Appropriate completeness gate

The concept stage should pass only when:

- Every mandatory knowledge category has an entry.
- Every entry is marked known, unknown, deferred, or not_applicable.
- Every important unknown has an owner, risk, and resolution milestone.
- The most important quality goals and constraints are concrete enough to guide requirements and architecture.
- Stakeholders and decision rights are identified.
- Sources of truth do not conflict.
- The stakeholder approves the problem, outcomes, boundaries, and unresolved-risk profile.

So my verdict is:

> Agent Factory has many of the right downstream artifacts, but its current Phase 0 cannot yet claim a standards-informed inventory of all knowledge needed
> to manage a development project. It could do so by adding a formal concept-stage knowledge-obligation model—without trying to resolve every obligation up
> front.

That distinction would preserve the Factory’s small-step philosophy while making omissions, uncertainty, and responsibility mechanically visible.

## Motivation

Agent Factory starts its formal delivery chain at Requirements. Phase 0
currently provides conversation, project fitting, proposal drafting, and
knowledge routing, but it has no defined Concept-stage contract or exit gate.

The existing [Factory guide § Agent Context](../../.agent-factory/factory/docs/factory-guide.md#agent-context)
defines `docs/agent-context.md` as a routing switchboard rather than a knowledge
base. This separation is useful, but routing alone cannot show whether the
project has considered every required knowledge area.

The current artifacts cover engineering practice, feature scope, requirements,
and architecture well. They cover project purpose, stakeholder authority,
benefits, capacity, suppliers, project risks, operations, and knowledge
freshness less consistently. Unknown information can remain implicit or spread
across conversations and later-phase documents.

The current greenfield contract also contains incompatible artifact paths. The
[capture-context skill § Concern model](../../.agent-factory/factory/skills/capture-context/SKILL.md#concern-model)
requires one `docs/agent-context.md` file and retires the earlier YAML model.
The [greenfield playbook § Step 1.0](../../.agent-factory/factory/playbooks/greenfield-development.md#step-10--scaffold-project-charter)
still requires the retired YAML files and the former `capture-charter` skill.
A formal Concept stage needs one consistent artifact contract.

## Core Principles

- Inventory knowledge obligations instead of requiring complete knowledge up
  front.
- Record uncertainty as managed project information.
- Keep one authoritative source for each decision or fact.
- Keep `docs/agent-context.md` as a routing interface rather than a second
  knowledge base.
- Tailor the inventory to project size, criticality, delivery model, and risk.
- Resolve only the knowledge needed for the next responsible decision.
- Review Concept-stage outputs independently before Requirements begins.

## Design

### Stage position and purpose

Introduce **Phase 0: Concept** before the existing Requirements phase. VIRGIL
may still explore an unformed idea without artifacts. The Concept stage begins
when the stakeholder decides to develop a project rather than continue open
exploration or run a disposable spike.

The Concept stage establishes:

1. why the project should exist;
2. who is affected and who may decide;
3. what system and project boundaries apply;
4. which requirements, qualities, constraints, risks, and lifecycle concerns
   can drive later decisions;
5. which project-management capabilities are needed; and
6. what is known, unknown, deferred, or not applicable.

The stage does not produce detailed requirements, a complete architecture, a
delivery backlog, or implementation estimates derived from a backlog.

### Required artifacts

The Concept stage produces five logical artifacts. The final implementation may
combine related artifacts when that reduces duplication without weakening their
contracts.

#### Concept brief

The concept brief records:

- the problem or opportunity;
- business goals and expected benefits;
- target users and other affected parties;
- intended outcomes and measures of success;
- system, organizational, and product boundaries;
- the first delivery scope and explicit exclusions; and
- the reason to proceed now.

#### Stakeholder and concern map

The map records each stakeholder or role, their concerns, decision authority,
required involvement, and known conflicts with other concerns. It distinguishes
users, operators, sponsors, developers, assurance roles, affected organizations,
and external authorities where applicable.

#### Driver register

The driver register records the information most likely to affect requirements
or architecture:

- important functional capabilities;
- prioritized quality goals expressed as observable scenarios;
- technical, organizational, legal, regulatory, and commercial constraints;
- business and technical context boundaries;
- architectural hypotheses;
- major trade-offs; and
- technical risks.

Detailed requirements and architecture decisions remain outputs of their
existing phases.

#### Project-management outline

The outline records the initial management approach:

- governance and decision rights;
- delivery approach and lifecycle;
- funding, time, and capacity boundaries;
- team structure and required skills;
- dependencies, acquisition, suppliers, and external services;
- risk, issue, opportunity, and change handling;
- communication and reporting expectations;
- information and configuration management; and
- release, operation, support, migration, and retirement assumptions.

The outline defines how the project will be managed. It does not require a
detailed schedule or work breakdown before Planning.

#### Knowledge-obligation register

The register inventories the knowledge needed by later stages. Each entry
contains at least:

```yaml
id: KO-001
concern: Availability target
category: quality
status: unknown
source: null
owner: product-owner
consumers:
  - requirements
  - architecture
  - operations
confidence: low
risk_if_wrong: high
resolution_by: before-architecture-review
validation: stakeholder-approval
review_trigger: traffic-forecast-changes
```

Allowed states are `known`, `unknown`, `deferred`, and `not_applicable`.
Additional categories may be added through project tailoring. A required
category may not disappear silently.

`docs/agent-context.md` points to the authoritative Concept artifacts for the
relevant concerns. It does not copy their content.

### Minimum knowledge taxonomy

The inventory covers these categories unless the project records why a category
does not apply:

| Category             | Required coverage                                                            |
| -------------------- | ---------------------------------------------------------------------------- |
| Purpose and value    | Problem, goals, benefits, outcomes, success measures                         |
| Stakeholders         | Roles, concerns, authority, participation, conflicts                         |
| Scope and context    | System boundary, business context, external interfaces, exclusions           |
| Requirements         | Initial capabilities, assumptions, acceptance direction, traceability origin |
| Quality              | Prioritized quality goals, scenarios, evaluation method                      |
| Constraints          | Technical, organizational, legal, regulatory, commercial                     |
| Architecture         | Drivers, hypotheses, context, trade-offs, technical risks                    |
| Delivery             | Lifecycle, milestones, dependencies, acquisition, suppliers                  |
| Organization         | Governance, team, skills, capacity, communication                            |
| Control              | Risks, issues, opportunities, change, information, configuration             |
| Assurance            | Test direction, review needs, security, privacy, compliance                  |
| Operations           | Deployment, observability, support, migration, continuity, retirement        |
| Knowledge governance | Source, owner, confidence, freshness, consumers, resolution point            |

### Concept exit gate

The Concept stage may advance to Requirements when:

- every mandatory knowledge category has at least one entry or an explicit
  `not_applicable` decision;
- every entry has an allowed state;
- every `known` entry names an authoritative source and validation method;
- every `unknown` or `deferred` entry names an owner, risk, and resolution point;
- the most important quality goals and constraints are concrete enough to guide
  requirements and architecture work;
- stakeholder roles and decision authority are identified;
- no two artifacts claim authority for the same information;
- all required deterministic checks pass;
- an independent reviewer finds no blocking omissions; and
- the stakeholder approves the purpose, outcomes, boundaries, and accepted
  uncertainty.

The gate checks knowledge coverage and control. It does not require all entries
to be `known`.

### Lifecycle after Concept

Requirements, Architecture, Planning, Implementation, and Quality consume and
update knowledge obligations. A later decision may add a new obligation or
invalidate a known entry. The responsible phase updates the authoritative
artifact and the register in the same change.

The reconciliation process checks whether implementation or operations have
invalidated Concept-stage assumptions. A project may return to Concept when its
purpose, business case, system boundary, governance, or risk profile changes
materially.

### Standards basis

The design uses the following sources as coverage guides rather than as claims
of formal certification:

- [iSAQB Certified Professional for Software Architecture Foundation Level](https://public.isaqb.org/curriculum-foundation/curriculum-foundation-en.html)
  for stakeholders, concerns, requirements, constraints, qualities, decisions,
  interfaces, cross-cutting concepts, communication, and assessment;
- [iSAQB Requirements for Software Architects](https://public.isaqb.org/curriculum-req4arc/curriculum-req4arc-en.html)
  for incremental requirements work and early identification of architecture
  drivers;
- [arc42 template](https://arc42.org/overview/) for goals, context, constraints,
  architecture decisions, quality requirements, risks, and terminology;
- [ISO 21502:2020](https://committee.iso.org/sites/tc258/home/projects/published/iso-21502.html)
  for project governance, benefits, planning, control, change, risks, issues,
  and information management;
- [ISO/IEC/IEEE 15288:2023](https://www.iso.org/standard/81702.html) for lifecycle
  coverage from conception through retirement; and
- [ISO/IEC/IEEE 29148:2018](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A29148%3Aed-2%3Av1%3Aen)
  for requirements information, management, validation, and traceability.

## Scope

**In the first release:**

- A formal Concept phase and its entry and exit conditions.
- Templates or schemas for the five logical artifacts.
- A mandatory, tailorable knowledge taxonomy.
- Explicit handling of known, unknown, deferred, and inapplicable knowledge.
- Deterministic structural validation of the knowledge-obligation register.
- Independent semantic review of Concept-stage completeness.
- Routing from Concept outputs into Requirements and Architecture.
- Integration with `docs/agent-context.md` without content duplication.
- Replacement of conflicting greenfield charter and context instructions.
- Greenfield and brownfield entry paths.

**Explicitly deferred (do NOT plan stories for these):**

- Certification against iSAQB or any International Organization for
  Standardization standard. The standards provide coverage guidance only.
- A complete project-management application with scheduling, accounting,
  resource allocation, or earned-value calculations.
- Detailed requirements, architecture, backlog, or implementation artifacts.
- Portfolio and programme management.
- Automated judgement about whether a business case is valid.
- A universal fixed taxonomy that cannot be tailored to project risk.

## Design Details

### Model information obligations, not documents

The five artifacts are logical contracts. A small project may store them in one
Concept dossier plus one machine-readable register. A regulated project may
split them across controlled documents. The gate evaluates required information
and traceability rather than a fixed document count.

### Unknown is valid but must be controlled

An unknown entry is not a gate failure by itself. It becomes a gate failure when
it lacks an owner, risk, resolution point, or validation method. This rule keeps
the process incremental without hiding uncertainty.

### Standards remain separate

iSAQB supplies architecture knowledge and practices. It does not define a full
project-management system. The Concept taxonomy therefore combines architecture,
requirements, lifecycle, and project-management perspectives while keeping
their responsibilities distinct.

## Open Questions

- Should the default physical form be one Concept dossier plus one YAML register,
  or several separate documents?
- Which exact knowledge categories are mandatory for every project, and which
  should depend on risk or project type?
- Where is the boundary between an initial capability in Concept and a functional
  requirement in Requirements?
- Should project risks and technical risks share one register or remain separate
  linked views?
- Which agent should conduct the independent Concept review?
- Which omissions can a deterministic gate detect, and which require semantic
  review?
- Which event types require a project to re-enter Concept rather than update a
  later-phase artifact?
- How should existing projects adopt the Concept inventory without reconstructing
  decisions that have no surviving evidence?
- Should the proposal lifecycle remain the entry mechanism for features while
  the Concept stage applies only to projects and major product initiatives?

## Completion Criteria

- The Factory guide defines Concept as a formal phase before Requirements.
- A validated artifact contract identifies every required Concept information
  item, its owner, and its authoritative location.
- The knowledge-obligation schema accepts only the four defined states.
- Structural validation rejects missing categories, missing ownership of
  uncertainty, unresolved source paths, and invalid resolution points.
- The Concept review procedure checks stakeholders, architecture drivers,
  project-management coverage, lifecycle coverage, and controlled uncertainty.
- Greenfield and brownfield playbooks produce the same Concept terminal contract
  through appropriate entry paths.
- Requirements and Architecture declare which Concept outputs they consume.
- `docs/agent-context.md` routes relevant concerns to Concept artifacts without
  duplicating their contents.
- The retired YAML charter model and `capture-charter` references are removed
  from active Concept and greenfield instructions.
- Tests cover valid, incomplete, deferred, inapplicable, and contradictory
  Concept inventories.
- All affected indexes, links, Markdown files, schemas, and playbooks pass their
  applicable deterministic gates.

## Guiding Rule

A complete Concept stage accounts for every required knowledge obligation; it
does not pretend that every answer is known.
