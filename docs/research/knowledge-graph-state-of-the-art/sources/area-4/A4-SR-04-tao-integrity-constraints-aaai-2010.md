# A4-SR-04: Tao, Sirin, Bao, McGuinness: Integrity Constraints in OWL

```json
{
  "source_identity": "Jiao Tao, Evren Sirin, Jie Bao, Deborah L. McGuinness. 'Integrity Constraints in OWL'. Proceedings of the Twenty-Fourth AAAI Conference on Artificial Intelligence (AAAI-10), pp. 1443-1448, DOI 10.1609/aaai.v24i1.7525. https://ojs.aaai.org/index.php/AAAI/article/view/7525",
  "author_or_issuing_body": "Jiao Tao, Jie Bao, Deborah L. McGuinness (Rensselaer Polytechnic Institute); Evren Sirin (Clark & Parsia)",
  "publisher": "Association for the Advancement of Artificial Intelligence (AAAI)",
  "publication_date": "2010-07-01T00:00:00Z",
  "relevant_event_date": "2010-07-01",
  "source_family": "Primary. Peer-reviewed conference paper that extends record 3 and names the Motik et al. semantics (record 2) as its closest related work.",
  "precise_evidence_location": "Abstract and Introduction (page 1443); Examples 1 and 2 (page 1443); Related Work and Examples 3 to 5 (page 1444)",
  "method": "Downloaded the PDF from cdn.aaai.org on 2026-11-17, extracted text with pdftotext, and read pages 1 and 2 (Abstract through Example 5).",
  "limitations": "The date 2010-07-01 is a placeholder for the month of the conference. The paper does not print a day, and the conference month was not confirmed from a primary page. Only the first two pages were read. The formal semantics, the SPARQL reduction, and the Pellet evaluation were not checked. The criticism of Motik et al. is the authors' own and was not answered by Motik et al. in any source read here.",
  "provenance": "Downloaded from https://cdn.aaai.org/ojs/7525/7525-13-11055-1-2-20201228.pdf on 2026-11-17 with curl. Re-verify by reading page 1444 for Examples 3 to 5."
}
```

## Evidence

### Criticism of OWL's standard semantics

- Abstract: "conditions that trigger constraint violations in systems using the Closed World Assumption (CWA), will generate new inferences in standard OWL-based reasoning applications."
- Example 2 (page 1443): two producers m1 and m2 under an at-most-one constraint "will be inferred to be same due to the cardinality restriction," although "the intention to use the above cardinality restriction is not to draw this inference, but to detect an inconsistency."

### Criticism of the minimal-model proposal of Motik, Horrocks, and Sattler 2007

- Related Work (page 1444): "The closest related work to ours is the approach that reuses OWL as an IC language. One notable effort work along this line is a proposal by Motik et al. ... which is based on a minimal Herbrand model semantics of OWL."
- Example 4 (page 1444): the constraint that every product has a known producer "is still satisfied by the semantics of (Motik, Horrocks, and Sattler 2007) because in every minimal Herbrand model p has a producer," although the producer is not known.
- Example 5 (page 1444): a constraint on Category1 "is violated with the (Motik, Horrocks, and Sattler 2007) semantics because there is a minimal model where p belongs to Category1," although p may belong to Category2.
- The paper concludes that it presents "a new IC semantics for OWL that can correctly capture the intended closed world constraint semantics."

### The proposed formulation

- Abstract: "an alternative IC semantics for OWL that allows applications to work with the CWA and the weak UNA," chosen per axiom, with "IC validation ... reduced to query answering under certain conditions" and a prototype on Pellet.

### What this record supports

- It records the criticism that drove the change from step 2 to step 4 in concept 1: the minimal-model reading gave wrong answers on constraints that must see only known facts (area index, concept 1, step 4).
