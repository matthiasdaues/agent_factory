# A3-SR-15 — Rahwan, Zablith and Reed, "Laying the Foundations for a World Wide Argument Web" (2007)

```json
{
  "source_identity": "Rahwan, I., Zablith, F., Reed, C., 'Laying the foundations for a World Wide Argument Web', Artificial Intelligence 171(10-15), 897-921, DOI 10.1016/j.artint.2007.04.015; preprint submitted 4 June 2007",
  "author_or_issuing_body": "Iyad Rahwan, Fouad Zablith (British University in Dubai), Chris Reed (University of Dundee)",
  "publisher": "Elsevier (journal); the copy read is the authors' preprint on web.mit.edu/irahwan",
  "publication_date": "2007-07-01T00:00:00Z",
  "relevant_event_date": "2007-06-04",
  "source_family": "Primary. Paper that implements and extends AIF (A3-SR-14) in RDF Schema. Reed and Rahwan co-wrote A3-SR-14 and A3-SR-17.",
  "precise_evidence_location": "Abstract; Section 2 (passage beginning 'A number of highly-structured argument-based deliberation support systems (ADSS) have been proposed'); Section 4 'Extending the Core AIF: Representing Argument Schemes'; Section 5 'AIF-RDF: The Extended AIF Ontology in RDF Schema', text on disjointness.",
  "method": "A design paper: an ontology extension, an RDF Schema implementation and a pilot system, ArgDF.",
  "limitations": "The journal issue spans July to October 2007; the first day of July stands as publication date. The event date is the preprint submission date. The section heading for the ADSS passage was not captured in the extraction. The paper describes a pilot tool and reports no user study. It states the RDFS disjointness limit in one sentence and does not discuss other limits.",
  "provenance": "Fetched 2026-11-17 with curl from http://web.mit.edu/irahwan/www/docs/AIJ2007.pdf and converted with pdftotext. Quotes are exact and were checked against the extracted text."
}
```

## Evidence

- Abstract: "First, we extend the recently proposed Argument Interchange Format (AIF) to express arguments with a structure based on Walton's theory of argumentation schemes. Then, we describe an implementation of this ontology using the RDF Schema Semantic Web-based ontology language".
- Abstract: the pilot system ArgDF lets users "create arguments using different argumentation schemes" and "query arguments using a Semantic Web query language"; users "can attack or support parts of existing arguments".
- Section 2, on earlier systems: "These systems suffer from two key limitations. Firstly, they usually support a small number of participants. Secondly, most of them target specific domains".
- Section 2: "highly-structured ADSSs are based on client-server architectures and usually designed for small to medium-sized groups, and are therefore not easily scalable".
- Section 4: "Each Walton scheme type has a name, conclusion, set of premises and a set of critical questions bound to this scheme." The paper adds a new class of nodes, called forms (F-nodes), for the generic form of premises and conclusions.
- Section 5: "Recall that the core AIF requires that all classes of edges and nodes are disjoint [...] Unfortunately, disjointedness cannot be expressed in RDFS, and considered one of the limitations of this semantic language."

## What the source shows

It shows the second AIF formulation (2007): AIF extended with argumentation schemes and F-nodes, written in RDF Schema, and one limit of that choice (no disjointness).

## What the source does not show

It does not show how ArgDF performed in use, nor the later OWL ontology (A3-SR-17).

## Failed searches and gaps

None.
