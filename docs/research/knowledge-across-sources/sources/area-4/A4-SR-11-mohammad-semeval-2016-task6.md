# A4-SR-11: Mohammad et al., SemEval-2016 Task 6: Detecting Stance in Tweets

```json
{
  "source_identity": "Saif M. Mohammad, Svetlana Kiritchenko, Parinaz Sobhani, Xiaodan Zhu, Colin Cherry, 'SemEval-2016 Task 6: Detecting Stance in Tweets', Proceedings of SemEval-2016, pp. 31-41; https://aclanthology.org/S16-1003.pdf",
  "author_or_issuing_body": "Mohammad, Kiritchenko, Zhu, Cherry (National Research Council Canada); Sobhani (University of Ottawa)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2016-06-16T00:00:00Z",
  "relevant_event_date": "2016-01-01",
  "source_family": "Primary for the SemEval-2016 stance task definition, dataset, and results.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2.2 Stance and Sentiment; results summary in Section 1",
  "method": "Annotates 4,870 English tweets for stance towards six targets. Task A is supervised on five targets; Task B tests on an unseen target (Donald Trump) without training data. Nineteen teams took part in Task A and nine in Task B.",
  "limitations": "Date set to the first workshop day (16-17 June 2016). relevant_event_date is the year of the task and is approximate. Tweets only, English only, six US targets. Stance is labelled for an author towards a target, not for one text relative to another text.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "Stance detection is the task of automatically determining from text whether the author of the text is in favor of, against, or neutral towards a proposition or target."
- Abstract: "given a tweet and a target entity (person, organization, etc.), automatic natural language systems must determine whether the tweeter is in favor of the given target, against the given target, or whether neither inference is likely. The target of interest may or may not be referred to in the tweet, and it may or may not be the target of opinion."
- Abstract: "The highest classification F-score obtained was 67.82 for Task A and 56.28 for Task B. However, systems found it markedly more difficult to infer stance towards the target of interest from tweets that express opinion towards another entity."
- Section 1: "for Task A, none of these systems surpassed a baseline SVM classifier that uses word and character n-grams as features".
- Section 2.2: "Stance detection is related to, but different from, sentiment analysis."
- Section 2.2: "Also, the same stance (favour or against) towards a given target can be deduced from positive tweets and negative tweets."
- Shows: the target-based formulation of stance with three labels, and the finding that stance and sentiment are separate signals. So a sentiment shift between two versions of a claim does not by itself show a stance shift.
- Does not show: stance of a downstream text relative to a source text.
