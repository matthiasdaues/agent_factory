# Judge verdicts on the blind passages

Each passage was judged on its own against `factory-voice.md`. The checks cover the speaker's style and vocabulary, Meaningful text, Paragraphs, Decision questions, Target state and record, and the final pass on buzzwords. The Structured artifacts table and the Documents section were not applied. A passage fails when it clearly breaks a stated rule within its own text. It does not fail only because context from the surrounding text is missing.

| Passage | Verdict | Sections broken                   | Most serious breach: words and reason                                                                             |
| ------- | ------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| P01     | passes  |                                   |                                                                                                                   |
| P02     | passes  |                                   |                                                                                                                   |
| P03     | passes  |                                   |                                                                                                                   |
| P04     | fails   | Decision questions                | "Today showed how hard it is to get out of a wrong install record": the reason does not say how (a) helps.        |
| P05     | fails   | Meaningful text                   | "Three of these fixes ... The other two ... these four fixes": three plus two is five, not four.                  |
| P06     | passes  |                                   |                                                                                                                   |
| P07     | fails   | Decision questions                | "withdraws DEC-02, DEC-04, DEC-07, DEC-10 and DEC-12": bare identifiers; the receiver cannot picture the outcome. |
| P08     | passes  |                                   |                                                                                                                   |
| P09     | passes  |                                   |                                                                                                                   |
| P10     | passes  |                                   |                                                                                                                   |
| P11     | fails   | Speaker style                     | "Not available.": a fragment; it does not say what is unavailable.                                                |
| P12     | passes  |                                   |                                                                                                                   |
| P13     | fails   | Meaningful text                   | "the eight assumptions: DEC-07 to DEC-11, DEC-13, and DEC-14": the list holds seven, not eight.                   |
| P14     | fails   | Speaker vocabulary                | "(the actual table cells)": "actual" changes no meaning here.                                                     |
| P15     | passes  |                                   |                                                                                                                   |
| P16     | passes  |                                   |                                                                                                                   |
| P17     | passes  |                                   |                                                                                                                   |
| P18     | fails   | Decision questions                | "settles Q3's register, Q5, Q7, and Q8": question numbers alone; the receiver cannot see what gets settled.       |
| P19     | passes  |                                   |                                                                                                                   |
| P20     | fails   | Paragraphs                        | "the guard or ownership stops me": an abstract noun acts; it does not name the thing that stops.                  |
| P21     | passes  |                                   |                                                                                                                   |
| P22     | passes  |                                   |                                                                                                                   |
| P23     | passes  |                                   |                                                                                                                   |
| P24     | fails   | Speaker style                     | "key set → exit 1 with the message": arrows between clauses and fragments in place of sentences.                  |
| P25     | fails   | Decision questions                | "commands for the two orphan suites": the suites are not named, and no recommendation is given.                   |
| P26     | passes  |                                   |                                                                                                                   |
| P27     | fails   | Meaningful text                   | "The twelve defaults: G02 to G07, G09, and G11 to G16": the list holds thirteen.                                  |
| P28     | fails   | Speaker style                     | "the brief-storage run, then the gate proposal": a fragment with no verb.                                         |
| P29     | passes  |                                   |                                                                                                                   |
| P30     | passes  |                                   |                                                                                                                   |
| P31     | passes  |                                   |                                                                                                                   |
| P32     | fails   | Speaker style, Decision questions | "B, with prose in notes, ... notes free in length and position": over 25 words, compressed, with dropped verbs.   |
| P33     | passes  |                                   |                                                                                                                   |
| P34     | passes  |                                   |                                                                                                                   |
| P35     | passes  |                                   |                                                                                                                   |
| P36     | passes  |                                   |                                                                                                                   |
| P37     | passes  |                                   |                                                                                                                   |
| P38     | passes  |                                   |                                                                                                                   |
| P39     | passes  |                                   |                                                                                                                   |
| P40     | passes  |                                   |                                                                                                                   |
| P41     | passes  |                                   |                                                                                                                   |
| P42     | fails   | Speaker style                     | "no factory specific docs folders found": a fragment with dropped articles and no subject.                        |
| P43     | passes  |                                   |                                                                                                                   |
| P44     | passes  |                                   |                                                                                                                   |
| P45     | passes  |                                   |                                                                                                                   |
| P46     | fails   | Meaningful text                   | "my ten author fixes for U1 to U6 and C1 to C6": twelve items, but ten fixes; the count disagrees.                |
| P47     | passes  |                                   |                                                                                                                   |
| P48     | passes  |                                   |                                                                                                                   |
| P49     | passes  |                                   |                                                                                                                   |
| P50     | fails   | Meaningful text                   | "It waits for line 8 of ...": it points at a line it does not show or name.                                       |
| P51     | fails   | Decision questions                | "more than N commits ahead?": no recommendation, no value for N, and no statement of what it settles.             |
| P52     | passes  |                                   |                                                                                                                   |
| P53     | passes  |                                   |                                                                                                                   |
| P54     | passes  |                                   |                                                                                                                   |
| P55     | passes  |                                   |                                                                                                                   |
| P56     | passes  |                                   |                                                                                                                   |
| P57     | passes  |                                   |                                                                                                                   |
| P58     | fails   | Speaker vocabulary, Final pass    | "keeps the specification and the DSL as core truth": "core truth" sounds important but says little.               |
| P59     | passes  |                                   |                                                                                                                   |
| P60     | passes  |                                   |                                                                                                                   |
| P61     | passes  |                                   |                                                                                                                   |
| P62     | passes  |                                   |                                                                                                                   |

## Count

18 of 62 passages fail. The speaker's style and vocabulary fired most often, in 7 passages: P11, P14, P24, P28, P32, P42, and P58. Decision questions fired in 6 passages, Meaningful text in 5, Paragraphs in 1, and the final pass in 1. Target state and record fired in none.
