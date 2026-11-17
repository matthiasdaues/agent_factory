# Demon report, section C (C10 to C19)

Line numbers starting with "P" refer to `input/proposal-working-copy.md`. Other files are named in full.

### C10 — damaged

- Attack 1: succeeded. The test works on whole sentences, so a padding clause inside a needed sentence survives. P213: "This proposal needs nothing special for it: `premerge-check` reruns every gate that `docs/testing.yaml` enables, so a scanner added later runs at the merge without a change here." Deleting the sentence loses the rerun fact, so the sentence stays. Its first clause is reassurance and nothing else.
- Attack 2: succeeded. P88: "This repository holds six old ledgers, thirteen worktrees besides the primary checkout, and 36,109 files under `.current-work/`." Delete it and the planner loses nothing needed to act, because the Design and the Completion Criteria say what to build. The sentence is still the evidence that the problem is real. The handoff (`input/handoff-run-lifecycle-decisions-2026-11-16.md`, line 40) records that a reviewer verified exactly these numbers. Cutting the sentence makes the proposal less honest.
- Attack 3: failed. No other claim has a test for need. C00 names "what the reader needs" in its wording, but its check tests only support for truth.
- Attack 4: succeeded. "Help the reader act" depends on which act. Take P88 again. Reader A treats approval as the act: the numbers are needed. Reader B treats implementation as the act: the numbers can go. Both readings are careful, and the register does not choose between them.
- Attack 5: failed. "Earns its place" is a metaphor in the title, but the body and the check are plain.
- Weakest point: "act" has no fixed object, so the deletion test gives different answers for the approver and the implementer.
- Smallest repair, if damaged or refuted: Name the act ("decide or carry out"), count evidence for a decision as needed, and apply the test to clauses as well as sentences.

### C11 — damaged

- Attack 1: succeeded. The check asks only whether the sentence "states a fact about the subject". A true benefit claim is a fact about the subject and can still sell. Invented: "The guardrail stops every destructive command in all five agent tools." Each word is a fact claim about the subject, and the sentence is a sales line. P100, "This works in every agent tool the Factory supports.", passes the check the same way. It also rests on an unchecked claim (see C15).
- Attack 2: succeeded. P84 breaks the rule: "This proposal defines one lifecycle for a run, from `dispatch init` to `dispatch close`, for both ways of driving it." The obeying version is "A run has one lifecycle, from `dispatch init` to `dispatch close`, for both ways of driving it." That version states as current fact what P88 says does not exist today. In a proposal, "This proposal defines" marks a statement as proposed. The announcing frame carries the modality, so the broken version is more honest.
- Attack 3: succeeded in part. C10's deletion test already removes "This document explains…" and "That is the right default". C11 differs from C10 only where an announcement carries meaning, as in P84, and there C11 gives the wrong answer.
- Attack 4: succeeded. P102: "Every piece of state has a reader and a remover." Reader A: a design fact, since P310 and P293 to P300 carry it out. Reader B: a slogan that praises the design, set in bold in a list of principles. The line between "fact" and "evaluation" decides the check, and the claim does not draw it.
- Attack 5: failed. The wording is plain and the two examples are concrete.
- Weakest point: the check separates fact from evaluation, but selling works by choosing facts, and announcing sometimes marks what is only proposed.
- Smallest repair, if damaged or refuted: Ban announcements of the text's structure and evaluative words ("right", "clean", "elegant"); allow a frame that marks a statement as proposed.

### C12 — damaged

- Attack 1: succeeded. The rule has two halves, and the check covers only rejected alternatives. A reassuring sentence that rejects nothing passes untested. P100: "This works in every agent tool the Factory supports." P250: "so a finding filed on a story branch cannot collide with one filed elsewhere." Neither names an alternative, so the check never applies to them.
- Attack 2: succeeded. P148 rejects reconciliation on the feature branch: "On a feature branch, two parallel runs would edit the same files and conflict at the merge into `dev`." It names neither who proposed the alternative nor why a reader would expect it, so it breaks the check. It is still the only reason in the document for where reconciliation runs, and a planner needs it. The obeying version adds a clause such as "A reader might expect reconciliation on the feature branch, where the other checks run." That clause is itself a sentence that answers a doubt nobody raised.
- Attack 3: succeeded in part. C10's deletion test catches the reassurance half: delete "Either way, no object is without an owner" and the reader loses nothing. Only the alternative half has its own check.
- Attack 4: succeeded. P329: "The guardrail refuses no other `dispatch` command, because the human watches a run by hand and can undo any other step." Reader A: a scope statement with its reason, which FV calls explaining a design by what it does. Reader B: a defense against "why not refuse `merge-story` too?". The handoff (line 46) shows a reviewer did raise that doubt, but the proposal does not say so. A reader of the proposal alone cannot tell whether the doubt was raised.
- Attack 5: failed. "A doubt nobody raised" cannot be known for sure, but "or a reader would expect it" makes the clause workable.
- Weakest point: the check tests only alternatives, while the rule's main target is the reassuring sentence.
- Smallest repair, if damaged or refuted: Give the reassurance half its own check ("the sentence states what the system does, not that a worry is settled"), and accept a reason against an alternative without naming who proposed it.

### C13 — damaged

- Attack 1: succeeded. The check bans only presenting a constraint as a benefit. Playing a constraint down passes. P384: "Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full spawn." The limit is not sold as a feature. "Usually small" still shrinks it without evidence.
- Attack 2: failed. I found no sentence where selling a constraint made the text clearer.
- Attack 3: succeeded in part. A constraint "presented as an achievement" is praise of the design, which C11 already bans. The placement half is the only part C11 does not cover.
- Attack 4: succeeded. P100: "The person watches, and the guardrail blocks what cannot be undone." Reader A: a design choice, stated as a principle. Reader B: a limitation (nothing refuses an early merge by hand, P188) promoted to a principle. The claim does not say whether a deliberate choice with a cost counts as a constraint.
- Attack 5: succeeded. The rule sends constraints to "the constraints section". `packages/factory/rulebooks/templates/proposal.md` has no such section; only `templates/story.md` (line 116) has one. In a proposal the placement half cannot be followed. The proposal puts its limits under Design Details (P382 to P386).
- Weakest point: the rule assumes a section that the main document type does not have.
- Smallest repair, if damaged or refuted: Drop the placement half and say "state a limit as a limit, with no benefit or minimizing clause attached".

### C14 — damaged

- Attack 1: succeeded. The rule's own example, "the gate exits non-zero", is observable from outside and satisfied by a script that runs `exit 1`. A goal without its condition is observable and empty. The proposal avoids this (P407 names the condition), but the rule does not demand it.
- Attack 2: succeeded. P398 breaks the rule: "`config/extensions/block-dangerous-git.ts` holds no rule of its own. It passes each command to `config/hooks/block-dangerous-git.sh` and returns the script's answer." That is a mechanism. The observable version, "pi gives the same answer as the script for every command in the test set", passes today and says nothing about drift tomorrow. P331 says drift is the actual problem. The structural criterion states the real goal more honestly.
- Attack 3: failed. No other claim covers goals.
- Attack 4: succeeded. P434: "the dispatch contract lists exactly the fields the code writes." Reader A: an observable result, checked by comparing a document with the ledger. Reader B: observable only by reading the code, so it is not "outside the code". Also, FV 91 says "outside the artifact", and the register says "outside the code". The two wordings draw the boundary in different places.
- Attack 5: succeeded. The rule says "the mechanism belongs in the scope", but proposals have no Goals section (`templates/proposal.md`). Their goals live in Completion Criteria, where the rule's split between goal and scope has no home.
- Weakest point: "observable from outside" lets a vacuous goal through and blocks a structural goal that is the true aim.
- Smallest repair, if damaged or refuted: Require each goal to name the condition and the result ("given X, the gate exits non-zero"), and allow a structural criterion when the goal is to prevent drift.

### C15 — damaged

- Attack 1: succeeded. The mark launders a premise. Invented: "pi's guard can refuse a command (unchecked; run pi with a test hook to confirm)." The sentence obeys, and the Scope can still commit stories that depend on it. The rule keeps an unchecked claim from posing as fact, but not from carrying a design.
- Attack 2: succeeded at an edge. P296: "Git keeps stashes in the repository, not in the folder, so they survive the removal." It cites no run and carries no mark. The obeying version adds "(checked with `git stash` in a worktree, git 2.43, this session)". For stable, well-known git behavior, the citation adds noise and a version note that will go stale itself.
- Attack 3: succeeded. C00's check, "each statement is supported by a source, a check run in the session, or an explicit 'unchecked' mark", covers every tool claim. C15 is C00 limited to tools.
- Attack 4: succeeded. P331: "It relies on refusing a command, which every tool's guard supports." No mark sits on the sentence. P399 asks for a test "in a real OpenCode session, not a mock", and the handoff (line 48) records that the OpenCode hook format never ran. Reader A: the document names what would check the claim, so the claim is marked. Reader B: the claim at P331 is stated as fact. The rule says "checked in the session"; the check says "cites a run or a doc". A reader of the finished document cannot see a session check.
- Attack 5: failed. The wording is concrete and the source gives a worked example.
- Weakest point: a reader of the document cannot see a check made in the session, and a mark does not stop the claim from carrying the design.
- Smallest repair, if damaged or refuted: Fold into C00 as its tool case, require the mark next to the claim, and forbid a marked claim from carrying a scoped decision until it is checked.

### C16 — damaged

- Attack 1: succeeded. The rule invites another fault: stereotyped examples. Its own case (WD 54) calls a developer from Pune named "Stefan Berger" a contradiction. A writer who obeys picks names that match a stereotype of the place, which is a habit, not a check of truth.
- Attack 2: failed. I found no text where an inconsistent example reads better. Deliberately invalid test input is a subject, not a fault of the example.
- Attack 3: failed. C00 covers true statements. An invented example is not true or false in that sense.
- Attack 4: succeeded. The third WD check reads "no stated fact contradicts another fact in the example or in the project's material", and "the project's material" has no bound. The proposal shows the cost. P240 invents a chain: "Take ST-0351, which depends on ST-0350, and ST-0352, which depends on ST-0351." All three are real stories in `backlog/`, all `status: done`. `backlog/ST-0352.md` line 8 has `deps: []`. P145 and P425 call BUG-0090 "the open finding". `docs/findings/BUG-0090.md` is a real finding with `status: resolved`, about `arch-lint`. Reader A: these are invented examples that only borrow the ID format, so they pass. Reader B: they contradict the project's material, so they fail. The document went through the rule and the contradiction stayed.
- Attack 5: failed. The fault in the register, "examples that undermine trust", is vague. The three checks in WD carry the rule.
- Weakest point: the check against "the project's material" is unbounded, so in practice no one runs it, and real IDs slip into invented examples.
- Smallest repair, if damaged or refuted: Drop the check that names fit backgrounds, and require that an invented ID either not exist in the project or match the real item.

### C17 — damaged

- Attack 1: succeeded. Completeness is not prominence. Invented report: "Done: 14 steps. Skipped: Vue lint (no frontend), mutation testing (slow), security scan (no scanner configured), migration test (database container missing)." Every skip appears in plain words. The one that matters, the migration test, is fourth in a list of routine skips.
- Attack 2: succeeded. Listing steps that do not apply makes a report longer, not more honest. "Skipped: Vue lint, no frontend" in a Python-only project tells the reader nothing, and C10 would cut it. The version that leaves it out is clearer.
- Attack 3: failed. No other claim targets omission in reports.
- Attack 4: succeeded. "Step" and "skipped" are not defined. Invented: "Tests pass." Only the unit suite ran; the integration suite was not started. Reader A: the step that ran passed, so the report obeys. Reader B: the integration suite was a skipped step, so the report breaks. The text cannot settle which steps were expected.
- Attack 5: failed. "In the same plain words as what succeeded" is concrete.
- Weakest point: the rule asks for every failed or skipped step without saying which steps were expected.
- Smallest repair, if damaged or refuted: Name the steps the task required, report each as passed, failed, or not run, and put failures first.

### C18 — damaged

- Attack 1: succeeded. The check reaches only statements the writer marks as uncertain, so false certainty, half the named fault, passes. P388 to P390: "## Open Questions / None." The frontmatter has `confidence: low` and three `unknown` estimates (P55 to P59). The handoff (line 40) lists FC-QG24 as open. The section asserts no uncertainty, so the check has nothing to test.
- Attack 2: succeeded. The mutation-testing doubt appears three times: P215, P260 and P378. Each place depends on it, and a reader who jumps to "Checks at the merge" would otherwise read P260 as settled. Repeating it is clearer than "once".
- Attack 3: failed. C00 covers the mark but not the "once" or the way to settle.
- Attack 4: succeeded. P213: "because the flaws it finds usually lie in how stories fit together." Reader A: "usually" is a hedge, so it needs a way to settle it. Reader B: "usually" is a confident claim about frequency, so no mark is needed. P384, "A gate fix is usually small", splits readers the same way.
- Attack 5: succeeded. The fault lists "false certainty", but no part of the check can detect it. The rule claims an effect its check cannot have.
- Weakest point: the check tests only uncertainty the writer already admits.
- Smallest repair, if damaged or refuted: Drop "once" in favour of "at each place the doubt matters", and drop "false certainty" from the fault or give it its own check.

### C19 — refuted

- Attack 1: succeeded. Objection can become ritual. Invented: "I think this premise is wrong, but I'll proceed as asked." The reply does not accept silently, so it obeys. If the writer then carries out the request without waiting for an answer, the objection is decoration.
- Attack 2: succeeded. The check, "no reply accepts a premise the writer believes wrong", drops the rule's word "only". Take a settled decision: Quarkdown was chosen for `publish-docs` on 2026-10-15. User: "Render the PDF with Quarkdown." Obeying the check: "I believe Pandoc fits better here. Proceed with Quarkdown?" Breaking the check: "Rendering with Quarkdown." The second reply is clearer and more respectful of a decision already made.
- Attack 3: failed. C00 catches a stated false agreement, but not silent acceptance.
- Attack 4: succeeded at the core. The check depends on what the writer believes, and no reader can see that. Invented reply: "Sure, I'll write the handoff to `/tmp/`." Reader A: it obeys, since nothing shows the writer disagreed. Reader B: it breaks, since the project rule puts handoffs in `docs/handoffs/` and the writer should have known. Only the writer can apply the check, and only to themself.
- Attack 5: succeeded. The register claims that the text "loses fault K and keeps its meaning". This rule governs conduct in a conversation, not a property of a text. It belongs in section F (process), not C.
- Weakest point: no reader can check a text against the writer's private beliefs.
- Smallest repair, if damaged or refuted: Cut it from section C and restate it in section F as a conduct rule: "when you disagree, state the objection and wait for the answer before acting".

## Patterns

Most checks cover only half of their rule: C12 tests alternatives but not reassurance, C18 tests admitted doubt but not false certainty, and C11 tests fact against evaluation but not selling by choice of facts. Three rules (C13, C14, C10) assume a reader, act or section that the proposal template does not have. Several checks depend on knowledge outside the text, such as session checks (C15), the whole project (C16), or the writer's beliefs (C19). The proposal written under these rules still holds unmarked tool claims, a false "None" under Open Questions, and invented examples that contradict the backlog, so the rules do not yet catch what they name. Narrowing each check to what a reader can see on the page closes most of the attacks.
