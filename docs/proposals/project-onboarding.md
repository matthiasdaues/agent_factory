---
schema_version: 2
title: Project Onboarding
status: draft
owner: md@matthiasdaues.de
created: 2026-11-08
updated: 2026-11-08
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/init-factory
    - packages/factory/scripts/crap-score
    - packages/factory/scripts/dependency-check
    - packages/factory/agents/virgil.md
    - packages/factory/agents/implementation-agent.md
    - packages/factory/playbooks/brownfield-onboarding.md
    - packages/factory/skills/detect-test-regime/SKILL.md
    - packages/factory/skills/reverse-map/SKILL.md
    - packages/factory/skills/security-review/SKILL.md
    - packages/factory/rulebooks/core-artifacts.yaml
    - packages/factory/config/AGENTS.claude.md
    - packages/factory/config/AGENTS.codex.md
    - packages/factory/config/AGENTS.copilot.md
    - packages/factory/config/AGENTS.pi.md

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - reliability

estimate:
  as_of: 2026-11-08
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Project Onboarding

## Primer

The primer is written after the grilling, when the design is settled.

## Summary

The feature tells a person who installs the factory on any existing project what the factory found, and what it cannot check there (DEC-09). It adds a plain-language opening paragraph, a stack profile of platform, framework, and languages, and a measured gap report whose rows the user must decide. It answers one question the factory cannot answer today: which parts of this project do the factory's checks not see? The first release works for every stack, and it brings stack skills for native Android in Java and Kotlin only.

## Motivation

The factory onboards every project through the same file-name scan and the same Python-bound gates. A check on a small sample Android project shows three problems, and the problems reach every stack the factory does not know well.

The scan misdescribes the project. `init-factory` maps any `build.gradle` file to `java` and never reads a source file. The sample was written in Kotlin and reported as `java`. A Flutter project would report `java` too, because `pubspec.yaml` is not a known manifest and the `android/` folder holds a Gradle file.

Two gates pass without checking anything. `dependency-check` and `crap-score` read only `*.py` files. The sample had a `ui` package and a `data` package that import each other, with rules that forbid both directions. `dependency-check` exited 0. `crap-score` returned an empty list and exited 0. Every non-Python project gets the same result, and `dependency-check` runs after every story. A mixed project gets a partial check with no notice: the factory's own `packages/` directory holds 60 Python files and 14 TypeScript files, and the gates read only the Python files.

The user learns none of this. The session start lists detections such as languages and test commands. It does not say what the project is, and it does not say what the factory cannot do there. The onboarding playbook hard-codes `npm`, `pytest`, and `grep` patterns for TypeScript, Python, and Go, so any other stack starts with commands that do not apply. On a mobile project the gap is wider, because no playbook, agent, skill, or rulebook mentions emulators, signing, or app stores.

## Core Principles

- The platform, the framework, and the languages are three separate facts. An Android project is not necessarily a Kotlin project (DEC-01).
- A gap is measured against the real project wherever a measurement is possible. A support table can go stale, and a count cannot.
- A gate that cannot read the code does not pass. A gate passes only when every language is read, covered by a declared tool, or waived.
- The factory uses the team's own tools. It adds no parser for another language.
- A factory gap and a project gap are different things. A gate that cannot read Java is a factory gap. A missing test is project debt, and the gap report does not list it.

## Design

The user meets the feature in three steps: the opening paragraph, the gap report, and the decision on each row. All three draw on one stack profile.

### The opening paragraph

The first session on an unfitted project opens with one paragraph of plain language. The session agent writes it. The install script does not, because the script has no model and cannot draw a conclusion (DEC-02). For a native Android project, the paragraph reads:

> After scanning this directory, I conclude the following. This looks like an Android app for taking notes, which people install on their phones. Most of it is written in Java, and a newer part is in Kotlin. Automatic checks run on every push, but they test only the logic and never run the app on a phone. I can help you plan, document, and review this project today. I cannot yet check its code structure or run it on a device. I could not tell how you release it. Tell me if I got something wrong.

For a web service in TypeScript with a few Python scripts, the paragraph reads:

> After scanning this directory, I conclude the following. This looks like a web service that handles room bookings. Almost all of it is written in TypeScript, and a few helper scripts are in Python. Automatic tests run on every push, and most parts of the service have them. I can help you plan, document, and review this project today. I can check the code structure of the Python scripts, but not yet of the TypeScript code. I could not tell where the service runs in production. Tell me if I got something wrong.

The paragraph answers five things in this order: what the project is, what it is made of, how it is looked after, what the factory can and cannot do here, and what stayed unclear.

The agent reads the stack profile, the README, the project name and description in the manifest of the stack, and the top-level package names. The agent changes no file while it writes the paragraph. Three rules govern the wording:

- A sentence that goes beyond the evidence starts with "This looks like" or a similar marker. A fact the agent could not find appears as "I could not tell".
- The paragraph names no tool and no file. The evidence stays in `project-context.json`, and the agent shows it when the user asks how it knows.
- Every statement about what the factory cannot do comes from the census described below, not from the agent's judgement.

The paragraph replaces the summary line in the `AGENTS.<cli>.md` session-start text. When the user confirms or corrects a sentence, the agent updates the profile and sets `fitting.fingerprint_confirmed` to `true`. A reply that only picks the fitting or the menu leaves the key `false`. The category list from fitting step 1 stays as the detail view on request.

### The stack profile

`init-factory` writes the profile into `project-context.json`.

| Fact      | What it names               | How the scan finds it                                                                                                                                                                             | What it decides                                                     |
| --------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Platform  | Where the software runs     | `AndroidManifest.xml` for `android`, a `*.xcodeproj` directory for `ios`, a known browser framework for `browser`, a known backend framework or `Dockerfile` for `server`, otherwise `unknown`    | Entry points, how the software is run and released, security checks |
| Framework | What the code is built on   | The known framework lists of the scan, plus `pubspec.yaml` for Flutter, `react-native` in `package.json`, `*.csproj` for MAUI, `ProjectSettings/` for Unity, `capacitor.config.*` for a web shell | Test commands, the place of entry points in the code                |
| Languages | What the code is written in | The census: a count of source files per language                                                                                                                                                  | Which tools can read the code                                       |

A project can have several platforms. A web application has a `server` and a `browser` part, and a Flutter project holds both an `android/` and an `ios/` folder. When the platform stays `unknown`, the paragraph says so in its last part.

The census counts files by extension. It covers Java, Kotlin, C and C++, Swift, Objective-C, Dart, JavaScript, TypeScript, C#, Python, Go, Rust, Ruby, and PHP. It skips the directories in `SCAN_SKIP_DIRS` and generated or vendored directories such as `Pods/` and `.gradle/`. The directory name `factory` is skipped only at the repository root, because `com/example/notes/factory/` is ordinary source code.

Each entry in `languages` gains a `files` count. A manifest such as `build.gradle` or `package.json` does not imply a language, because the census supplies it. The file counts also show which part of a repository is the main code: 40 Kotlin files next to 900 Dart files describe a Dart app.

### The gap report

After the fingerprint, the fitting writes `docs/stack-gaps.md`, with one row per capability. The capabilities are the same for every stack, and only the measurements differ. A Python service with a known framework may have no row at all. The example is an Android project with 180 Java, 32 Kotlin, and 12 C++ files, because it shows most kinds of gap.

| Capability       | Measured in this project                              | Consequence                                    | Decision                                         |
| ---------------- | ----------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------ |
| Dependency rules | Read 0 of 224 source files                            | `ui/MainActivity.kt` may import `data/` unseen | Project tool for Java and Kotlin, waiver for C++ |
| Complexity       | Read 0 of 224 source files                            | The gate has nothing to score                  | Open                                             |
| Test execution   | One JVM suite found, the device suite cannot run here | Agents cannot check `androidTest/`             | Environment: the human runs the device suite     |
| Entry points     | 14 activities and 3 receivers in the manifest         | `reverse-map` needs the Android rules          | Stack knowledge                                  |
| Security         | 4 exported components                                 | The web checklist does not cover them          | Stack knowledge                                  |
| Release          | Fastlane found, no signing access                     | Agents cannot produce a release build          | Waiver: release stays with the human             |

Each row closes in one of four ways:

- **Project tool.** The gate runs a command that the project declares in `docs/testing.yaml`.
- **Stack knowledge.** A skill supplies the entry-point list, the security checks, and the mapping of test suites to factory test layers.
- **Environment.** The missing device, credential, service, or machine goes into the suite's `prerequisites` in `docs/testing.yaml`. Agents then report the suite as not run.
- **Waiver.** The user accepts the gap and states a reason.

`docs/stack-gaps.md` is registered in `core-artifacts.yaml` as an optional seam artifact. A project with no gaps has no rows and needs no file.

### The gate contract

`dependency-check` and `crap-score` read Python natively. Each gate runs the census on its source root when it starts. A language counts as covered when the gate reads it natively, when a declared command covers it, or when a waiver names it. The gate exits 1 when a language is not covered, and the message names the language and the test-strategy agent (DEC-05).

The gate runs the census itself because `project-context.json` lies under the gitignored `.agent-factory/` directory, so a story worktree cannot read it. A live census also notices a language that a story introduces.

A project declares commands and waivers in `docs/testing.yaml`:

<!-- yaml-excerpt -->

```yaml
gates:
  dependency_check:
    commands:
      - command: "./gradlew archTest"
        covers: [java, kotlin]
    waived:
      - language: cpp
        reason: "The NDK part is a vendored codec that we do not change."
```

The gates run a declared command the way `mutation-testing` does: from the worktree, in its own process group, with a time limit. A non-zero exit fails the gate. The JSON report lists each language with its file count and how it was covered.

`covers` is a declaration, not a measurement. The factory cannot count what an external tool read unless it parses that tool's report.

### Stack knowledge

Knowledge splits along the profile, in the same shape for every stack. A platform skill holds what all projects on that platform share: entry points, security checks, and how the software is run and released. A framework skill holds the test mapping and the in-code entry points. The skills load only when the profile names their platform or framework. A stack without a skill shows the gap in its report, and the user records a waiver or writes a skill for the project.

The first skills are one platform skill for Android and one framework skill for native Android in Java and Kotlin (DEC-04, DEC-06). Android is the first case because it has none of the factory's assumptions: no HTTP entry points, no web security model, and tests that need a device.

### Changes to the brownfield playbook

- Steps 1.1 and 1.2 read the test commands and the entry-point patterns from the stack profile and the loaded skills. They no longer hard-code `npm`, `pytest`, and `grep`.
- Step 2.2 asks where the software runs and how it is released, for every platform. Terraform stays one possible answer. A mobile project answers with its backend, its release tooling, and its app store, because the architecture model needs the device and the store as deployment nodes.
- The Stage 1 exit requires `docs/stack-gaps.md` on a project with gaps, and the check fails while a row is open.

`detect-test-regime` and `reverse-map` follow the loaded skills for test suites and entry points that they do not know, such as Gradle suites and manifest entries. `security-review` applies the platform skill's checks next to the OWASP Top 10.

## Scope

**In the first release:**

- The opening paragraph on every unfitted project, whatever its stack.
- The stack profile with the census for every language listed in the design.
- Recognition of the platforms `android`, `ios`, `browser`, and `server`, and of the frameworks named in the design.
- The gap report with its four ways of closing a row.
- The gate contract for `dependency-check` and `crap-score`.
- The Android platform skill and the native Android framework skill for Java and Kotlin.
- The playbook, `detect-test-regime`, `reverse-map`, and `security-review` changes that use these skills.

**Explicitly deferred (do NOT plan stories for these):**

- iOS skills and device rules. iOS needs a Mac, and no check on one is possible from the current Linux development machine (DEC-04).
- Skills for any other stack, such as Flutter, React Native, Django, or Spring. The first release recognizes these stacks where the design names them and shows the gap. Each skill waits for a project that needs it.
- A factory parser for any language except Python. The team's tools do this work.
- Parsing external tool reports to measure what a declared command read. The declaration is enough until a false declaration causes a problem.
- Starting emulators, provisioning devices, or standing up services. The environment path records the gap, and a human closes it.
- Release automation for any platform.

## Design Details

- A language with a small file count still needs coverage or a waiver. One waiver for a few helper scripts costs one recorded decision, and a threshold would hide real code.
- `.kts` build scripts are not counted as Kotlin source. They configure the build and do not form the app.
- `covers` and `language` use the census names: `java`, `kotlin`, `cpp`, `swift`, `objective-c`, `dart`, `javascript`, `typescript`, `csharp`, `python`, `go`, `rust`, `ruby`, `php`.
- The Python result of a native gate stays unchanged. A Python-only project sees no difference.
- The census counts by extension, so an executable script without an extension is not counted. This matches what the native gates read today.
- A repository with no counted source file gives the gate nothing to check. The gate passes and the report states that the census found no source file.

## Open Questions

- What happens to a project that is already installed and has non-Python code, for example a fitted TypeScript project, when `update-factory` brings the new gate contract?
- Does a gate that cannot read a language fail, or does it report "not applicable" and pass with a warning? The design above assumes failure (DEC-05).
- Which stack gets the first skills, or does the first release bring none? The design above assumes native Android in Java and Kotlin, with iOS recognized and deferred (DEC-04, DEC-06).
- Do the first stack skills ship with the factory, or do they live in the first project and move into the factory later? The design above assumes they ship (DEC-07).

## Completion Criteria

- On a sample Android project in Kotlin, the scan reports `android`, `native`, and `kotlin` with its file count, and it does not report `java`.
- On a sample Flutter project, the scan reports both platforms, `flutter`, and `dart` as the largest language.
- On a sample FastAPI project, the scan reports `server`, `fastapi`, and `python` with its file count.
- On a sample with no platform signal, the scan reports `unknown`, and the paragraph says the agent could not tell where the software runs.
- A source directory named `factory` below the repository root appears in the census.
- On a sample project with an unfitted status, the session start opens with a paragraph that covers the five parts in order, names no tool and no file, and changes no file.
- A reply that corrects the paragraph updates the profile and sets `fitting.fingerprint_confirmed` to `true`. A reply that only picks the menu leaves it `false`.
- `dependency-check` exits 1 on a Kotlin sample with no declared command and no waiver, and the message names `kotlin` and the test-strategy agent.
- `crap-score` behaves the same way on the same sample.
- Both gates exit 0 on the same sample with a passing declared command that covers `kotlin`, and they exit 1 when that command fails.
- Both gates exit 0 on the same sample with a waiver for `kotlin`, and the JSON report shows the waiver.
- On a sample with Python and TypeScript files and no declaration for `typescript`, both gates exit 1 and name `typescript`, although they read the Python files.
- A Python-only project gets the same gate result as before the change.
- On an Android sample, `docs/stack-gaps.md` holds one row per capability, with counts from the sample.
- The Stage 1 exit check fails while a row in `docs/stack-gaps.md` is open, and it passes when every row has a decision.
- `reverse-map` on an Android sample lists the activities and receivers from the manifest as entry points.

## Guiding Rule

The user always knows which parts of the project the factory did not check, and no gate reports a pass for code it did not read.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by    | Decision                                                                                                             | Raised by        |
| ------ | ---------- | ---------- | ------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------- |
| DEC-01 | 2026-11-08 | decision   | product owner | The profile keeps platform, app framework, and languages apart. Android does not imply Kotlin.                       | Stakeholder note |
| DEC-02 | 2026-11-08 | decision   | product owner | The first session opens with a plain-language paragraph that states what the scan concluded.                         | Stakeholder note |
| DEC-03 | 2026-11-08 | decision   | product owner | The paragraph, the profile, and the gap report are one feature in one proposal.                                      | Stakeholder note |
| DEC-04 | 2026-11-08 | assumption | product owner | Android comes first. iOS is recognized, and its skills are deferred.                                                 | Open Questions   |
| DEC-05 | 2026-11-08 | assumption | product owner | A gate fails on a language that it cannot read and that has no declared tool or waiver.                              | Open Questions   |
| DEC-06 | 2026-11-08 | assumption | product owner | The first framework skill covers native Android with Java and Kotlin.                                                | Open Questions   |
| DEC-07 | 2026-11-08 | assumption | product owner | The Android skills ship with the factory, because a new install gets nothing from a skill that lives in one project. | Open Questions   |
| DEC-08 | 2026-11-08 | assumption | product owner | A waiver lives in `docs/testing.yaml` with its reason, because the gate must read it and that file is tracked.       | Drafting         |
| DEC-09 | 2026-11-08 | decision   | product owner | The feature covers the onboarding of any existing project. A mobile project is one case of it.                       | Stakeholder note |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
