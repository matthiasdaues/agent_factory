# A3-SR-13 — Clark, Ciccarese and Goble, "Micropublications" (2014)

```json
{
  "source_identity": "Clark, T., Ciccarese, P. N., Goble, C. A., 'Micropublications: a semantic model for claims, evidence, arguments and annotations in biomedical communications', Journal of Biomedical Semantics 5:28, DOI 10.1186/2041-1480-5-28; arXiv:1305.3506",
  "author_or_issuing_body": "Tim Clark, Paolo N. Ciccarese, Carole A. Goble",
  "publisher": "BioMed Central (Journal of Biomedical Semantics), read on PubMed Central, PMC4530550",
  "publication_date": "2014-07-04T00:00:00Z",
  "relevant_event_date": "2013-05-15",
  "source_family": "Primary. Original paper of the micropublication model. It builds on SWAN (A3-SR-12, same authors Clark and Ciccarese) and criticizes the nanopublication model (A3-SR-06, A3-SR-10).",
  "precise_evidence_location": "Background, 'Beyond statement-based models'; Background, 'The role and importance of empirical evidence'; Methods, 'Modeling considerations'; Example 9; Figure 1 caption; Table 1.",
  "method": "A model proposal. The authors analyze nine use cases and implement the model in OWL 2 and SWRL with example instances in RDF (arXiv abstract).",
  "limitations": "The page text is 191,422 characters; the extraction read the first 100,000. The Discussion section is unread, so criticisms of predecessors there are missing. Quotes and section names come from a model-assisted extraction and were not compared with the raw HTML. The Argument Interchange Format does not appear in the text read, so this record cannot show how micropublications relate to AIF. The authors describe SWAN and nanopublications as they understood them in 2013 and 2014; the nanopublication community may have disagreed. The event date is the arXiv submission date (15 May 2013); the paper was received by the journal on 12 March 2013.",
  "provenance": "Fetched 2026-11-17 with the WebFetch tool from https://pmc.ncbi.nlm.nih.gov/articles/PMC4530550/ and https://arxiv.org/abs/1305.3506 (abstract page; the arXiv PDF could not be decoded). Re-verify by opening the PMC page and searching for the quoted phrases."
}
```

## Evidence

Quotes are exact as returned by the extraction.

- On SWAN, Background 'Beyond statement-based models': SWAN is "a model for claims and hypotheses in natural language". It "models a principal statement, or 'hypothesis', with supporting statements" from the same publication only. Table 1 marks SWAN as not supporting claim networks and not representing direct empirical evidence.
- On nanopublications: they "model only the indicated statement". "None of these models provide a means to build claim networks of arbitrary depth." "There is no suggestion in the current specification that nanopublications may be applied directly" to evidence, "nor that they are designed to present primary scientific evidence". Figure 1 caption: the "Support" graph "is actually a set of Qualifiers used for filtering". Formalization of assertions "is likely an impediment to such direct use".
- On the Annotation Ontology and Open Annotation, Example 9: "Initially we used the Annotation Ontology, AO" and "We have now transitioned to a richer model, OAM (the Open Annotation Model)".
- On Toulmin, Methods: Toulmin's model "focuses on the internal structure of argument". The authors avoid separate backing and warrant classes "because these concepts become relativized across a large network".
- arXiv abstract (paraphrase): a micropublication is minimally "any statement with an attribution" and maximally an entire knowledgebase with evidence graphs. The paper says publications are defeasible arguments supported by data and methods.

## What the source shows

It shows the authors' criticism of two predecessors (SWAN and nanopublications) and the model built against them: claims, support and challenge links, evidence graphs, with Open Annotation for attachment to documents.

## What the source does not show

It does not show an independent evaluation of the criticism, or any criticism of micropublications. The Discussion section is unread.

## Failed searches and gaps

No source that criticizes the micropublications model was found. The 2008 SWAN journal paper was not read (see A3-SR-12).
