# A3-SR-14: Slack Developer Docs, Retrieving messages

```json
{
  "source_identity": "Slack Developer Docs, 'Retrieving messages'; https://docs.slack.dev/messaging/retrieving-messages",
  "author_or_issuing_body": "Slack Technologies (Salesforce)",
  "publisher": "Slack Technologies (docs.slack.dev)",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary. Vendor API documentation; same issuer as A3-SR-13 but a separate document about the Web API, not the export.",
  "precise_evidence_location": "Section 'Retrieving individual messages'; section on threaded messages with the conversations.replies example",
  "method": "Vendor developer guide with request and response examples.",
  "limitations": "No date on the page; both dates are the retrieval date. It documents the API, and the export may differ. The example response marks the 'replies' field as deprecated in 2019, so the format has changed over time, but the change history was not traced.",
  "provenance": "HTML downloaded with curl on 2026-11-18 and tags stripped locally. Re-verify at the URL above."
}
```

## Evidence

- Retrieving individual messages: "The ts value is essentially the ID of the message, guaranteed unique within the context of a channel or conversation."
- Same section: "They look like UNIX/epoch timestamps, hence ts, with specified milliseconds. But they're actually message IDs, even if they're partially composed in seconds-since-the-epoch."
- Threads: "Detect a threaded message by looking for a thread_ts value in the message object." and "Identify parent messages by comparing the thread_ts and ts values. If they are equal, the message is a parent message."
- Threads: "One quirk of threaded messages is that a parent message object will retain a thread_ts value, even if all its replies have been deleted."
- Example response: ""replies": \[ // Deprecated, to be removed on October 18, 2019."
- Shows: a Slack message is identified by channel plus ts, and a thread is one level deep, keyed by the parent's ts.
- Does not show: a globally unique message ID. Uniqueness is stated only within one channel.
