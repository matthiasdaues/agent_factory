# A3-SR-13: Slack Help Center, How to read Slack data exports

```json
{
  "source_identity": "Slack Help Center article 220556107, 'How to read Slack data exports'; https://slack.com/help/articles/220556107-How-to-read-Slack-data-exports",
  "author_or_issuing_body": "Slack Technologies (Salesforce)",
  "publisher": "Slack Technologies (slack.com Help Center)",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary. Vendor documentation of the official workspace export format.",
  "precise_evidence_location": "Sections 'JSON files' (folder layout and reference files), 'How to read messages' (JSON field list and example), TXT example, note on threads, 'How to read an edited message'",
  "method": "Vendor help article describing the export archive.",
  "limitations": "The page shows no publication or revision date; both dates are the retrieval date. The article is living documentation and may change without notice. The thread note sits after the TXT example, so it may apply to TXT exports only; the article does not say. The article was not compared with a real export archive.",
  "provenance": "HTML downloaded with curl on 2026-11-18 and tags stripped locally. Re-verify at the URL above, or through a web archive snapshot of that date."
}
```

## Evidence

- JSON files: "Each folder will contain messages from the conversation, organized by date in separate JSON files."
- How to read messages: ""ts": The timestamp when the message was posted. You can use any online unix time converter to translate the timestamp."
- How to read messages, example: ""ts": "1355517523.000005""
- Note: "Edited and deleted messages will only appear in your export file if your retention policy is set to keep them."
- After the TXT example: "Your export file will not differentiate between messages in a thread and messages sent to a channel. All messages in a thread will appear in the flow of the conversation."
- Shows: the export gives each message a user ID, text, and ts, splits files by day, and depends on the retention policy for edits and deletions.
- Does not show: the thread_ts field in JSON exports. The article does not mention it; A3-SR-14 documents it for the API.
