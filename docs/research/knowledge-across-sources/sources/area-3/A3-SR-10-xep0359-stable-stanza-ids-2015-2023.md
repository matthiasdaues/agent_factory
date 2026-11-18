# A3-SR-10: XEP-0359, Unique and Stable Stanza IDs (2015 to 2023)

```json
{
  "source_identity": "XEP-0359, 'Unique and Stable Stanza IDs', version 0.7.0 (2023-02-20); https://xmpp.org/extensions/xep-0359.html",
  "author_or_issuing_body": "Florian Schmaus",
  "publisher": "XMPP Standards Foundation",
  "publication_date": "2023-02-20T00:00:00Z",
  "relevant_event_date": "2015-06-01",
  "source_family": "Primary. XMPP extension lineage; used by XEP-0313 (archive) and XEP-0461 (replies), which were fetched but not recorded.",
  "precise_evidence_location": "Section 1 Introduction; Section 2.1 and 2.2; Section 3 Business Rules; Section 6 Security Considerations; Appendix H Revision History, versions 0.0.1 to 0.7.0",
  "method": "Experimental standards-track extension; revision history records each change with a date.",
  "limitations": "Status is Experimental, and version 0.6.0 records a deferral for lack of activity, so the document is not an approved standard. Adoption across clients was not measured. relevant_event_date is the first draft.",
  "provenance": "HTML downloaded with curl on 2026-11-18 and tags stripped locally. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "This XEP introduces unique and stable IDs for messages" and they "can be used together with Message Archive Management (XEP-0313) [1] to uniquely identify a message within an archive."
- Section 2.1: "The value of the 'id' attribute must be unique and stable, i.e. it MUST NOT change later for some reason within the scope of the 'by' value."
- Section 2.2: "Note that originating entities often want to conceal their XMPP address and therefore the <origin-id/> element has no 'by' attribute."
- Section 6: "The value of origin-id is spoofable and hence SHOULD not be used when referencing other stanzas."
- Revision 0.0.2 (2015-06-22): "Rename the XEP from "Message IDs" to "Stanza IDs"" and "Add 'by' attribute".
- Revision 0.3.0 (2016-10-29): "Rename client-id element to origin-id." Revision 0.5.0 (2017-08-23): "Define stanza-ids for messages only". Revision 0.7.0 (2023-02-20): "Add security consideration regarding spoofability and reference example".
- Shows: XMPP adds a scoped identifier (id plus the assigning entity) on top of the core protocol, and the scope and trust rules were added in dated steps.
- Does not show: the criticism behind each revision. The history gives the change, not the argument.
