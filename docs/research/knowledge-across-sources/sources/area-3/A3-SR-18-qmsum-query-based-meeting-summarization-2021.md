# A3-SR-18: Zhong et al., QMSum, query-based multi-domain meeting summarization (2021)

```json
{
  "source_identity": "Ming Zhong, Da Yin, Tao Yu, et al., 'QMSum: A New Benchmark for Query-based Multi-domain Meeting Summarization', Proceedings of NAACL-HLT 2021, pages 5905-5921; https://aclanthology.org/2021.naacl-main.472.pdf",
  "author_or_issuing_body": "Zhong, Yin, Yu, Zaidi, Mutuma, Jha, Awadallah, Celikyilmaz, Liu, Qiu, Radev (Fudan University, UCLA, Yale University, Microsoft Research, Microsoft Cognitive Services Research)",
  "publisher": "Association for Computational Linguistics",
  "publication_date": "2021-06-06T00:00:00Z",
  "relevant_event_date": "2021-06-06",
  "source_family": "Primary for the QMSum benchmark and its task definition. Secondary for the AMI and ICSI corpora, which it reuses and describes.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 3.1 Data Collection",
  "method": "Annotators wrote 1,808 query-summary pairs over 232 meetings from AMI, ICSI, and Welsh and Canadian parliamentary committees; the paper evaluates a locate-then-summarize method.",
  "limitations": "publication_date is the first day of the conference as printed. The summaries are written on manual transcripts, so speaker attribution and recognition errors are outside the task. Two-column PDF extraction interleaves lines; quotes were reassembled from the column text.",
  "provenance": "PDF downloaded with curl from the URL above on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "meeting summaries have become essential to remind those who may or may not have attended the meetings about the key decisions made and the tasks to be completed. However, it is hard to create a single short summary that covers all the content of a long meeting involving multiple people and topics."
- Section 1: "Most existing work and datasets on meeting summarization (Janin et al., 2003; Carletta et al., 2005) pose the problem as a single document summarization task where a single summary is generated for the whole meeting."
- Section 1: "This poses the question of whether a single paragraph is enough to summarize the content of an entire meeting?"
- Abstract: "QMSum consists of 1,808 query-summary pairs over 232 meetings in multiple domains."
- Section 3.1: ICSI "is an academic meeting dataset composed of 59 weekly group meetings at International Computer Science Institute (ICSI) in Berkeley, and their summaries."
- Shows: the summary task restated from one generic summary per meeting to answers to user queries, with a stated criticism of the AMI and ICSI framing.
- Does not show: an evaluation of whether query answers keep the link to the source utterances.
