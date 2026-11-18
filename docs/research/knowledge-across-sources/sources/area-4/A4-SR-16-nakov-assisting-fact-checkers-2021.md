# A4-SR-16: Nakov et al., Automated Fact-Checking for Assisting Human Fact-Checkers

```json
{
  "source_identity": "Preslav Nakov, David Corney, Maram Hasanain, Firoj Alam, Tamer Elsayed, Alberto Barron-Cedeno, Paolo Papotti, Shaden Shaar, Giovanni Da San Martino, 'Automated Fact-Checking for Assisting Human Fact-Checkers', Proceedings of IJCAI-21, Survey Track; https://www.ijcai.org/proceedings/2021/0619.pdf",
  "author_or_issuing_body": "Nakov, Alam, Shaar (Qatar Computing Research Institute); Corney (Full Fact); Hasanain, Elsayed (Qatar University); Barron-Cedeno (University of Bologna); Papotti (EURECOM); Da San Martino (University of Padova)",
  "publisher": "International Joint Conferences on Artificial Intelligence Organization",
  "publication_date": "2021-08-01T00:00:00Z",
  "relevant_event_date": "2021-08-01",
  "source_family": "Secondary survey of automated fact-checking. Primary only for its own pipeline view and the practitioner input from Full Fact. Secondary for Vlachos and Riedel (2014), whose step sequence it restates.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2.2 Detecting Previously Fact-Checked Claims; Figure 1 fact-checking pipeline",
  "method": "Literature survey organised by the tasks of a fact-checker, written with a fact-checking organisation as co-author.",
  "limitations": "Month-only date; set to 1 August 2021 (IJCAI-21 month). A survey; it reports no new experiments. Tracing the origin of a claim is not a named task in the pipeline. Vlachos and Riedel (2014) was not read.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the IJCAI proceedings site and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "The study by Vlachos and Riedel [2014] describes the following typical sequence of fact-checking steps: (i) extracting statements that are to be fact-checked, (ii) constructing appropriate questions, (iii) obtaining the pieces of evidence from relevant sources, and (iv) reaching a verdict using that evidence."
- Section 2.2: "Misleading claims are often repeated in multiple channels, independently of any fact-checks or rebuttals. Once a claim has been established as misleading, the ongoing spread of repeats or copies of the claim can be minimised by its rapid detection. In the simplest cases, these could be simple “copy and paste” repeats that are relatively easy to detect, but more often they will be paraphrases of the original or endlessly evolving variations."
- Section 2.2: "Finally, false claims often originate in one language and then get translated to other languages. Tools that can spot repeated claims across languages would be useful to address this."
- Shows: that fact-checking tools treat repeats of a claim as verbatim copies or paraphrases, and match them to an existing fact-check. The pipeline steps contain no step for finding who first made the claim.
- Does not show: a method for tracing a claim to its first source. For that step this area relies on A4-SR-15.
