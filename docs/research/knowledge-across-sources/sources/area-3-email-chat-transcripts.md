# Area 3: Email, Chat, and Meeting Transcripts

This index covers how email, chat, and meeting transcripts identify messages, threads, and speakers, and how decisions and action items are taken from meetings. It cites the 22 source records in [`area-3/`](area-3/) by ID. Each record holds the quotes. This index holds the sequence.

## State of the Art

**Email.** An email message identifies itself by one `Message-ID` field. The sender's host must make it globally unique, and a new version of a message gets a new identifier (A3-SR-04, A3-SR-05). A reply names its parent in `In-Reply-To` and its ancestors in `References`. `References` holds the parent's `References` followed by the parent's `Message-ID` (A3-SR-04, A3-SR-05). That rule came from Usenet in 1987 (A3-SR-03). Mail software did not follow the rules reliably, so threading code must tolerate missing, free-text, and contradictory headers (A3-SR-06, A3-SR-07). The one standards-track threading algorithm is the IMAP `THREAD=REFERENCES` algorithm. It formalizes the Netscape 2.0 and 3.0 algorithm and falls back to subject matching (A3-SR-06, A3-SR-07).

**Chat.** Chat protocols separate the identity of a message from the identity of a conversation. XMPP has an opaque `<thread/>` value per conversation, with one optional parent thread (A3-SR-08, A3-SR-09). A stable message identifier exists only as an experimental extension. In that extension, the identifier is valid within the scope of the entity that assigned it (A3-SR-10). Matrix derives an event ID from a hash of the event, so the ID is the event's content address (A3-SR-11). Matrix threads are flat: each threaded event points to the thread root, and threads do not nest (A3-SR-12). Slack identifies a message by channel plus a timestamp-like `ts` value and builds one level of threads from `thread_ts` (A3-SR-14). The official Slack export documents `ts`, `user`, and `text` per message. It does not document thread fields, and it keeps edits and deletions only under a matching retention policy (A3-SR-13).

**Transcripts.** Conversation disentanglement splits one stream of chat messages into separate conversations. Its current task definition labels reply links between messages and takes each connected component as one conversation (A3-SR-16). Speaker diarization answers "who spoke when" without naming the speakers. It is scored with diarization error rate (DER) and, since 2019, with Jaccard error rate (JER) (A3-SR-22). Meeting corpora such as AMI record one close-talking channel per speaker and link human summaries, with decision and action headings, to dialogue acts (A3-SR-17). Decision and action-item detection label the roles that utterances play, such as issue, proposal, and agreement, instead of one flat class (A3-SR-20, A3-SR-21). Meeting summarization has moved from one summary per meeting to summaries that answer a query (A3-SR-18).

## Hardened Concepts

Each step names the formulation, its date, the criticism that led to the next step, and the records for both. A step whose formulation or criticism has no record in this area is marked as a gap.

### 1. The Message-ID Rule

1. **Identifier for one version of a message, unique per host (1977).** RFC 733 defines `Message-ID` as an identifier for "THIS version of THIS message", with uniqueness guaranteed by the generating host. The example uses "at" as the separator (A3-SR-01). Criticism that led to RFC 822: gap. No source in this area states why the syntax changed.
2. **Identifier in addr-spec form inside angle brackets (1982).** RFC 822 keeps the meaning and writes the identifier as `"<" addr-spec ">"` (A3-SR-02). Criticism: identifiers and email addresses now have the same syntax, so software cannot tell them apart (A3-SR-06).
3. **No reuse, opaque to other hosts (1987, netnews).** RFC 1036 forbids reuse during the lifetime of an earlier message and tells programmers to treat foreign identifiers as unknown strings (A3-SR-03). Criticism that led to RFC 2822: the records hold no direct criticism. RFC 2822 lists "CFWS within msg-id not allowed" as a change without a reason (A3-SR-04).
4. **Globally unique, sender's intent decides identity (2001).** RFC 2822 requires global uniqueness, recommends a domain on the right-hand side, and lets the sender's meaning decide whether a changed message keeps its identifier (A3-SR-04). Criticism: the quoted left-hand side allows several written forms of one identifier, so the IMAP threading algorithm must normalize them "to avoid false non-matches" (A3-SR-07).
5. **One written form, obsolete forms parsed only (2008).** RFC 5322 removes `no-fold-quote` and quoted pairs from `msg-id`. It keeps the RFC 822 forms for parsing only (A3-SR-05). The link between step 4's criticism and this change is an inference. RFC 5322 gives no reason (A3-SR-05).

### 2. In-Reply-To and References

1. **Free phrase or identifier, unordered (1977 and 1982).** RFC 733 and RFC 822 allow `*(phrase / msg-id)` in both fields (A3-SR-01, A3-SR-02). Criticism: in a 1997 survey of 22,950 messages, 4,554 `In-Reply-To` fields held no bracketed identifier at all. The author calls the `References` definition "pretty useless" (A3-SR-06).
2. **Ordered ancestor list for news (1987).** RFC 1036 builds `References` from the parent's `References` plus the parent's identifier and permits truncation (A3-SR-03). Criticism: readers truncate in undefined ways, so messages in one thread carry "seemingly-contradictory References data" (A3-SR-06).
3. **Identifiers only, the news rule adopted for mail, single parent (2001).** RFC 2822 restricts both fields to identifiers, adopts the construction rule, and discourages `References` for replies with several parents (A3-SR-04). Criticism: "in actual practice this discipline has not been followed" for multiple `In-Reply-To` identifiers (A3-SR-07). Some clients put the parent only in `In-Reply-To` (A3-SR-06).
4. **Phrases ignored when parsing (2008).** RFC 5322 keeps the phrase forms as obsolete syntax and states that their phrases are ignored (A3-SR-05). The IMAP algorithm takes only the first valid identifier from `In-Reply-To` (A3-SR-07). No later criticism was found.

### 3. The Email Threading Algorithm

1. **Grouping by subject.** IMAP `ORDEREDSUBJECT`, "poor man's threading", groups by base subject and date and has no grandchildren (A3-SR-07). Its first date and first source are a gap.
2. **Reference-based threading with dummy parents and subject fallback (Netscape 2.0 and 3.0, before 1997).** The algorithm builds parent links from headers. It keeps placeholder parents for missing messages and groups unthreaded messages by subject (A3-SR-06). Criticism: Netscape 4.0 dropped both steps and presented threading as a kind of sorting (A3-SR-06). This is one developer's account.
3. **Internet-Draft imapext-thread (2002).** Gap. The draft was not read.
4. **Standards-track REFERENCES algorithm (2008).** RFC 5256 formalizes step 2 for IMAP servers and adds identifier normalization (A3-SR-07). Criticism: false `References` data merges one thread into another, and subject extraction can remove meaningful text (A3-SR-07, Section 6).

### 4. XMPP Thread and Message Identity

1. **Thread rules in RFC 3921 (2004).** Gap. RFC 3921 was not read. XEP-0201 states that its thread rules "have never been well specified" (A3-SR-09).
2. **Best-practice thread profile (2006 to 2010).** XEP-0201 adds UUIDs and a borrowed mail `In-Reply-To` header in 2007, a parent attribute in 2008, and removes the `In-Reply-To` header in 2010 (A3-SR-09). The revision history gives no reason for the removal (A3-SR-09).
3. **Thread identity in the core RFC (2011).** RFC 6121 makes `<thread/>` opaque, unique, and conversation-level, with an optional parent. It leaves conflicts between overlapping parent links to the implementation (A3-SR-08). Criticism: the core rules give no stable message identifier for archives or for chat rooms (A3-SR-10, Section 1).
4. **Scoped stable stanza IDs (2015 to 2023).** XEP-0359 adds `<stanza-id>` with an assigning entity and `<origin-id>` without one. In 2023 it adds that `origin-id` is spoofable (A3-SR-10). The extension is still Experimental (A3-SR-10).

### 5. The Matrix Event ID

1. **`$opaque_id:domain` (room versions 1 and 2).** The domain only namespaces the identifier (A3-SR-11). Criticism: servers received several events with one ID and could not tell which to use (A3-SR-11, room version 3).
2. **Reference hash of the event in Base64 (room version 3).** The server computes the ID from the event (A3-SR-11). Criticism: the `/` character broke clients that did not encode the ID and was read differently by reverse proxies (A3-SR-11, room version 4).
3. **URL-safe Base64 of the reference hash (room version 4).** (A3-SR-11). No later change was recorded. The dates of steps 1 to 3 are approximate.

### 6. The Disentanglement Task

1. **Clustering of speakers by time gaps (2003 to 2006).** Secondary only: the earlier systems are known through their critics (A3-SR-15). Criticism: they "cluster speakers, not utterances". Also, no public annotated data or agreed metrics existed (A3-SR-15).
2. **Clustering of utterances into conversations, with one-to-one and local metrics (2008).** Elsner and Charniak publish 800 annotated lines of IRC chat (A3-SR-15). Criticism: the datasets are small or not released. A widely used heuristic corpus has missing or extra messages in 80% of its conversations (A3-SR-16).
3. **Reply-structure graph, conversations as connected components (2019).** Kummerfeld et al. annotate 77,563 messages with reply links and adjudicate disagreements (A3-SR-16). Criticism: mixing conversations that had explicit structure creates biased test data (A3-SR-16). No later restatement was recorded.

### 7. The Action-Item Task

1. **One flat action-item label on ICSI meetings (2005 to 2006).** Secondary only, through A3-SR-20. Criticism: inter-annotator agreement was κ = 0.36 and the F-scores were about 0.3 (A3-SR-20).
2. **Four role classes: task description, timeframe, ownership, agreement (2006 to 2007).** Purver et al. reach pairwise κ from 0.64 to 0.78 (A3-SR-20). The 2006 first version was not read, so its date is from A3-SR-20.

### 8. The Decision-Detection Task

1. **Decision-making dialogue acts as one class, derived from summary links (2007).** Hsueh and Moore label 554 of 37,400 AMI dialogue acts (A3-SR-19). Criticism: the class mixes utterances with different roles, as the authors note themselves (A3-SR-19). Fernandez et al. add that a flat classifier reached an F-score of 0.35 (A3-SR-21).
2. **Decision dialogue acts: issue, resolution proposal, resolution restatement, agreement (2008).** Fernandez et al. report 58% F-score for decision regions (A3-SR-21). No later restatement was recorded.

### 9. The Diarization Metric

1. **DER in the NIST Rich Transcription evaluations (2002 to 2009).** Secondary only, through A3-SR-22.
2. **DER with a 250 ms collar and overlapped speech excluded (most work after 2009).** Secondary only, through A3-SR-22. Criticism: backchannels and overlaps are common, so the scores were "over-optimistic" (A3-SR-22).
3. **Full DER without collars, plus JER (2019).** DIHARD II adopts both (A3-SR-22). No later restatement was recorded.

### 10. The Meeting Summary Task

1. **One human abstractive summary per meeting, with the headings ABSTRACT, DECISIONS, PROBLEMS/ISSUES, and ACTIONS, linked to an extractive summary (AMI, about 2005 to 2006).** (A3-SR-17). Criticism: one short summary cannot cover a long meeting with many people and topics (A3-SR-18).
2. **Query-based summaries over meetings from several domains (2021).** QMSum (A3-SR-18). No later restatement was recorded.

## Gaps

- **ICSI corpus paper.** The Janin et al. 2003 PDF at the ICSI server timed out twice. The ICSI corpus page on the AMI site was fetched but holds only a short description, so it was not recorded. ICSI appears only through A3-SR-18 and A3-SR-20.
- **Unread predecessors.** RFC 3921, RFC 5536, the 2002 imapext-thread draft, and the mailing lists of the IETF DRUMS working group and of standards@xmpp.org were not read. Shen et al. 2006, Aoki et al. 2003 and 2006, Lowe et al. 2015, Gruenstein et al. 2005, Morgan et al. 2006, Carletta et al. 2005, and the NIST RT evaluation plans were not read. Each appears only through a later source.
- **Matrix proposals.** The Matrix Spec Change proposals for room versions 3 and 4 and for threads were not read. The exact release dates of room versions 3 and 4, spec v1.4, and spec v1.12 were not confirmed.
- **Other chat exports.** The official export formats of Discord, Microsoft Teams, Telegram, and WhatsApp were not searched. Slack is the only export format recorded.
- **Speaker naming.** No source covers the step from anonymous diarization labels to named speakers, or speaker attribution in automatic meeting transcripts.
- **Read but not recorded.** Elsner and Charniak 2010 repeats the 2008 task definition and adds the aliases "thread detection" and "thread extraction". XEP-0313 and XEP-0461 were fetched. XEP-0461 states that group chat replies must use the XEP-0359 room-assigned ID.
- **Overlap with other areas.** None found. This area does not cover claim matching or reuse classes.
