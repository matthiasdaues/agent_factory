# A3-SR-19: Abbas et al., SemDeDup: Data-efficient learning at web-scale through semantic deduplication

```json
{
  "source_identity": "Amro Abbas, Kushal Tirumala, Daniel Simig, Surya Ganguli, Ari S. Morcos, 'SemDeDup: Data-efficient learning at web-scale through semantic deduplication', arXiv:2303.09540v3; https://arxiv.org/pdf/2303.09540",
  "author_or_issuing_body": "Abbas, Tirumala, Simig, Morcos (Meta AI, FAIR); Ganguli (Stanford University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2023-03-01T00:00:00Z",
  "relevant_event_date": "2023-03-01",
  "source_family": "Primary for SemDeDup. Its text experiment uses C4, the corpus also studied in A3-SR-18.",
  "precise_evidence_location": "Abstract; Section 3 SemDeDup (k-means clustering and cosine threshold)",
  "method": "Embeds data points with a pre-trained model (CLIP for images, OPT for text), clusters them with k-means, and removes pairs above a cosine threshold within each cluster.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v3 of 22 March 2023. Most experiments are on images (LAION); the text experiment is smaller. The paper judges success by downstream model training, not by a labelled set of duplicate pairs. The term semantic duplicates stands in inner quotation marks in the abstract, so the abstract sentence is quoted whole. The text extraction drops the Greek letter of the threshold; I restored it as epsilon from the figure label eps.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2303.09540 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Here, we introduce SemDeDup, a method which leverages embeddings from pre-trained models to identify and remove “semantic duplicates”: data pairs which are semantically similar, but not exactly identical."
- Abstract: "large web-scale datasets such as LAION are largely uncurated beyond searches for exact duplicates, potentially leaving much redundancy."
- Section 3: "Within each cluster, we compute all pairwise cosine similarities and set a threshold cosine similarity above which data pairs are considered semantic duplicates."
- Section 3: "We expect that low thresholds of ε will find semantic duplicates, while higher thresholds will allow semantically redundant data pairs as well."
- Shows: embedding similarity used for same-idea deduplication, with the threshold as a dial between duplicate and related.
- Does not show: precision of the removed pairs against human labels.
