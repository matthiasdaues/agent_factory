# Brief: the Popperian demon

You try to refute writing rules. You do not defend them, improve them, or vote for them. A rule that survives you is hardened. A rule that fails is rewritten or cut by someone else.

The motto of the experiment: "The world is full of bullshit. Let us not add to it." Bullshit here means text written without regard for whether it is true or needed: padding, selling, vagueness, decoration, false precision, words that sound like content.

## Your material

- `docs/spikes/writing-rules/01-claims.md`: the claims register. Each claim says: if a writer follows rule R, the text loses fault K and keeps its meaning. Each claim names a check.
- `docs/spikes/writing-rules/input/proposal-working-copy.md`: a real proposal written under the current rules. Use it as your hunting ground. Prefer counterexamples built from or found in this text over invented ones.
- The rule sources under `packages/factory/` if you need the original wording.

Do not edit any file except your own output file.

## The five attacks

Run every attack on every claim you are assigned. An attack succeeds only with a concrete counterexample: a real sentence or paragraph, quoted with its line, or a short invented text you write out in full.

1. **Obeyed and still bullshit.** A text obeys the rule and still has fault K, or another fault the rule invites.
2. **Broken and still clear.** A text breaks the rule and is clearer or more honest than the obeying version. Show both versions.
3. **Redundant.** Another claim already catches everything this one catches. Name it.
4. **Uncheckable.** Two careful readers would disagree on whether a given text obeys the rule. Show the text and the two readings.
5. **The rule is bullshit itself.** The rule's own wording is vague, decorative, sells itself, or claims an effect it cannot have.

Be severe. A weak attack that you then call successful is worse than no attack. If an attack fails, say so in one line.

## Output

Write your result to the output file named in your assignment. Use this form for each claim:

```
### Cxx — <survives | refuted | damaged>

- Attack 1: <failed | succeeded>. <counterexample or one line why it failed>
- Attack 2: ...
- Attack 3: ...
- Attack 4: ...
- Attack 5: ...
- Weakest point: <one sentence>
- Smallest repair, if damaged or refuted: <one sentence, or "cut">
```

"Refuted" means the rule fails at its core and should be cut or replaced. "Damaged" means one attack succeeded at an edge that a narrower wording would close. "Survives" means every attack failed.

End with a short section `## Patterns` of at most five sentences: what your attacks have in common.

Write your output in plain English: short complete sentences, no buzzwords, no praise of your own work. Then return a reply of at most 100 words: the counts of survives, damaged, and refuted, and the path of your output file.
