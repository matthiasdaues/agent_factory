# Gaps Report: value-first-onboarding-journey

Generated: 2026-09-23
Source: [value-first-onboarding-journey.md](../proposals/value-first-onboarding-journey.md)

## Actor-Goal Matrix

| Actor              | Goal                                                     | Rule                                                                       | Status    |
| ------------------ | -------------------------------------------------------- | -------------------------------------------------------------------------- | --------- |
| Release maintainer | Publish reproducible installation assets                 | Rule: Release maintainer publishes reproducible installation assets        | specified |
| Newcomer           | Diagnose installation readiness without changes          | Rule: Newcomer diagnoses installation readiness without changes            | specified |
| Newcomer           | Control each prerequisite fix                            | Rule: Newcomer controls each prerequisite fix                              | specified |
| Newcomer           | Install a verified Factory release with explicit consent | Rule: Newcomer installs a verified Factory release with explicit consent   | specified |
| Project maintainer | Update an installation within its trust boundary         | Rule: Project maintainer updates an installation within its trust boundary | specified |
| Newcomer           | Receive project insight before advanced configuration    | Rule: Newcomer receives project insight before advanced configuration      | specified |
| Newcomer           | See gate value before choosing hooks                     | Rule: Newcomer sees gate value before choosing hooks                       | specified |
| Newcomer           | Complete one isolated task and choose its outcome        | Rule: Newcomer completes one isolated task and chooses its outcome         | specified |
| Quality researcher | Measure the complete newcomer journey                    | Rule: Quality researcher measures the complete newcomer journey            | specified |

## Missing Rules

None. Every actor-goal pair has a Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Ambiguous Wording

| ID      | Location | Step Text | Issue                          | Disposition |
| ------- | -------- | --------- | ------------------------------ | ----------- |
| VFO-G01 | —        | —         | No ambiguous wording detected. | closed      |

## Boundary Coverage

| Proposal boundary                                        | Covered by                                                   |
| -------------------------------------------------------- | ------------------------------------------------------------ |
| Public documentation and installation scripts            | Release, diagnosis, installation, and update Rules           |
| CLI orientation, session menu, VIRGIL, and newcomer tour | Project insight, gate demonstration, and isolated-task Rules |
| Context capture and proof-of-concept workflow            | Project insight and isolated-task Rules                      |
| Consumer and source pre-commit configuration             | Gate and hook Rule                                           |
| Existing installation and context tests                  | Installation, update, project insight, and hook contracts    |

## Deferred Scope

The proposal defers graphical installation, native Windows installation,
automatic installation of every prerequisite, persistent user profiles,
automatic production changes, and a hosted demonstration environment. This
specification defines no Rule for those capabilities.
