# Area 3: Embedding similarity

This index covers what embedding similarity can and cannot establish for five tasks: paraphrase, claim matching, text reuse, near-duplicate detection, and same-idea detection. It reports what the recorded sources document. It does not judge whether any concept survived refutation. The records are in the folder `sources/area-3/` and carry the IDs `A3-SR-01` to `A3-SR-21`. Each record states what its source shows and what it does not show.

The area has 21 records, above the planned 18, because the confirming check, vector versioning, and the hash methods each needed their own sources.

## State of the art, as the sources document it

**Sentence embeddings.** A sentence encoder trained on natural language inference (NLI) labels outperformed unsupervised encoders on transfer tasks in 2017 (A3-SR-01). Raw BERT output, averaged or taken from the first token, scored worse than averaged GloVe word vectors on semantic textual similarity (STS) (A3-SR-03). Sentence-BERT (SBERT) fine-tunes BERT in a siamese network, so that sentence vectors can be compared by cosine (A3-SR-03). Contextual representations occupy a narrow cone, so two random words can have a cosine near 1 (A3-SR-04). Later work names this anisotropy as the reason for the poor similarity of BERT sentence embeddings (A3-SR-05). SimCSE trains with a contrastive objective and reports that it makes the space more uniform (A3-SR-06).

**Benchmarks.** STS grades meaning similarity on a scale from 0 to 5 (A3-SR-02). MTEB states that STS correlates poorly with other uses, and that no single embedding method leads on all tasks (A3-SR-08). BEIR shows dense retrievers falling behind BM25 under domain shift (A3-SR-07). The MTEB maintainers later removed tasks that models had trained on, and the rankings changed (A3-SR-09).

**What similarity finds and misses, per task.**

| Task                     | What the records show similarity finds                                                                                                                             | What the records show it misses                                                                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Paraphrase               | Graded meaning similarity correlates with human STS scores (A3-SR-02, A3-SR-03, A3-SR-06). MTEB includes paraphrase and duplicate pairs as a task type (A3-SR-08). | Negation and word order: STS systems scored a sentence and its negation as nearly equivalent (A3-SR-02). Bi-encoders rank negated documents at or below random (A3-SR-10).        |
| Claim matching           | A cosine threshold of 0.71 reaches an F1 of 0.90 on English pairs (A3-SR-14).                                                                                      | Claim matching does not always mean the same meaning, and lower-resource languages score F1 between 0.17 and 0.61 (A3-SR-14). Domain shift lowers dense retrieval (A3-SR-07).     |
| Text reuse               | Containment measures how much of A lies in B, and substring matching finds partial copies (A3-SR-15, A3-SR-18).                                                    | These measures are syntactic by the author's own words (A3-SR-15). No record measures reuse with rewording.                                                                       |
| Near-duplicate detection | MinHash and SimHash find pages and documents with high n-gram overlap at web scale (A3-SR-15, A3-SR-16, A3-SR-17, A3-SR-18).                                       | Precision and recall near 0.75 on a sample at k = 3 (A3-SR-17). The hashes do not cover semantic duplicates with low n-gram overlap (A3-SR-18, A3-SR-19).                         |
| Same-idea detection      | Embedding clusters with a cosine threshold remove semantic duplicates (A3-SR-19).                                                                                  | The threshold slides from duplicate to related (A3-SR-19). Cosine is symmetric and cannot express the direction of entailment (A3-SR-11). Long texts cluster together (A3-SR-12). |

**From candidate to confirmed relation.** The records show two kinds of second-stage check. A cross-encoder reads both texts together. It costs about 65 hours for all pairs of 10,000 sentences (A3-SR-03), and it generalises better than single vectors across domains (A3-SR-07). It also handles negation best among the tested models (A3-SR-10). An NLI model scores entailment from a premise to a hypothesis. It scores higher than an embedding-based metric on factual consistency, but it degrades on texts longer than 200 tokens (A3-SR-13). For near-duplicates, the records show a cheap hash stage followed by an exact Jaccard and edit-similarity check (A3-SR-18). No record tests NLI as a filter on candidates from a vector search.

**Versioning and recomputation.** Vectors from different models live in unrelated spaces. The usual options are to keep one model for the life of the index or to re-encode the whole collection (A3-SR-20). One provider states that its two current models are incompatible and that an upgrade requires re-embedding all data (A3-SR-21). Research on update strategies that avoid re-encoding exists for continued fine-tuning of one model (A3-SR-20).

## Hardened concepts

Four concepts show several documented formulations with criticism between them. Each step names its source. A step without a source is marked as a gap.

### 1. The sentence embedding for similarity (6 steps)

1. **Averaged word vectors, before 2017.** A sentence vector is the average of its word vectors. No record covers this step from its own source. SBERT uses averaged GloVe vectors as a baseline (A3-SR-03). Gap: Arora et al. 2017 was not reachable. Criticism that led to step 2: Conneau et al. state that efforts to embed larger chunks of text "have however not been so successful" (A3-SR-01).
2. **Supervised encoder trained on NLI, 2017.** InferSent trains a sentence encoder on SNLI and transfers it to other tasks (A3-SR-01). Criticism that led to step 3: none recorded. The move to BERT came from its general success, and no record states a fault of InferSent for similarity. The Universal Sentence Encoder of 2018 belongs between steps 2 and 3, but I did not record it.
3. **Raw BERT output, 2018 to 2019.** Users averaged the BERT output layer or took the first token (A3-SR-03). Criticism that led to step 4: SBERT measured this as worse than averaged GloVe vectors, with an average correlation of 54.81 for averaging and 29.19 for the first token (A3-SR-03). A cross-encoder works well but needs about 65 hours for all pairs of 10,000 sentences (A3-SR-03).
4. **Siamese fine-tuning, 2019.** SBERT fine-tunes BERT on NLI and STS data, so that cosine between sentence vectors works (A3-SR-03). Criticism that led to step 5: Li et al. find that BERT "always induces a non-smooth anisotropic semantic space of sentences" (A3-SR-05). This builds on the word-level finding of A3-SR-04.
5. **Post-processing to an isotropic space, 2020.** BERT-flow maps sentence vectors to a Gaussian distribution without labels (A3-SR-05). Criticism that led to step 6: SimCSE states that such methods "only aim to encourage isotropic representations", while contrastive learning also aligns positive pairs (A3-SR-06).
6. **Contrastive training, 2021.** SimCSE uses dropout noise as the only augmentation, or NLI pairs as positives and hard negatives (A3-SR-06). Criticism for a later step: MTEB states that SimCSE and SBERT "solely evaluate on STS and classification tasks" (A3-SR-08). The step after SimCSE is a family of general embedding models ranked on MTEB. I did not record a primary source for any of these models.

### 2. Anisotropy as an explanation of poor similarity (3 steps)

1. **A narrow cone of word representations, 2019.** In BERT, ELMo, and GPT-2, contextual word representations are anisotropic (A3-SR-04). Criticism that led to step 2: the paper studies words, not sentences, and offers no fix (A3-SR-04).
2. **Anisotropy of sentence embeddings, fixed after training, 2020.** BERT-flow names anisotropy as the cause of poor sentence similarity and applies a normalizing flow (A3-SR-05). Criticism that led to step 3: post-processing only targets isotropy (A3-SR-06).
3. **Uniformity through the training objective, 2021.** SimCSE reports that contrastive learning makes the space more uniform and aligns positive pairs (A3-SR-06). Criticism for a later step: none recorded.

### 3. The benchmark for embedding similarity (5 steps)

1. **STS shared tasks, 2012 to 2016.** Annotators grade sentence pairs from 0 to 5. The record is secondary for these years (A3-SR-02). Criticism that led to step 2: the organisers wanted one shared training and evaluation set across the years (A3-SR-02). This is a stated motive, not a criticism of a fault.
2. **STS Benchmark, 2017.** One English set selected from the 2012 to 2017 data (A3-SR-02). Criticism that led to step 3: STS-only evaluation leaves transfer to search open, and "STS is known to poorly correlate with other real-world use cases" (A3-SR-08). The two works MTEB cites for that statement are a gap.
3. **Zero-shot retrieval benchmark, 2021.** BEIR tests retrieval on 18 datasets that the models did not train on (A3-SR-07). Criticism that led to step 4: BEIR covers retrieval only. MTEB names this as a gap in earlier benchmarks (A3-SR-08). The authors of BEIR also report a lexical bias in its annotations (A3-SR-07).
4. **Many task types in one benchmark, 2022.** MTEB covers 8 task types, 58 datasets, and 112 languages (A3-SR-08). Criticism that led to step 5: MTEB itself names short texts and task imbalance (A3-SR-08). MMTEB names limited language, domain, and task diversity. It also removes MS MARCO and Natural Questions "to prevent overfitting" (A3-SR-09).
5. **Multilingual and zero-shot benchmark, 2025.** MMTEB has over 500 tasks and a zero-shot English version. Small English models lose ranks on it (A3-SR-09). Criticism for a later step: the authors name English leakage through translated data (A3-SR-09). No independent audit is recorded.

### 4. Near-duplicate detection by hashing (5 steps)

1. **Shingles with min-wise sampling, 1997.** Broder defines resemblance and containment over word shingles and estimates them from small sketches (A3-SR-15). Criticism that led to step 2: Charikar presents his construction as a "simple alternative to minwise independent permutations" that also estimates cosine between general vectors (A3-SR-16). This states an extension, not a fault.
2. **Random-hyperplane sketch, 2002.** One bit per random hyperplane gives a sketch whose bit agreement estimates the angle between vectors (A3-SR-16). Criticism that led to step 3: the paper is theory and reports no document experiment (A3-SR-16).
3. **SimHash at web scale, 2007.** Manku et al. use 64-bit fingerprints with up to 3 differing bits on 8 billion pages. They report precision and recall near 0.75 (A3-SR-17). Criticism that led to step 4: none recorded between 2007 and 2021. This is a gap.
4. **Hash candidates plus an exact check, 2021.** Lee et al. use MinHash for candidates. They then require a Jaccard index above 0.8 and an edit similarity above 0.8, and they add exact substring matching (A3-SR-18). Criticism that led to step 5: SemDeDup states that web datasets "are largely uncurated beyond searches for exact duplicates, potentially leaving much redundancy" (A3-SR-19).
5. **Embedding-based semantic deduplication, 2023.** SemDeDup clusters embeddings and removes pairs above a cosine threshold (A3-SR-19). Criticism for a later step: none recorded. The paper reports no precision against human labels.

The confirming check (cross-encoder, NLI) and vector versioning have recorded sources. They show no sequence of formulations with criticism between them, so they are not listed as hardened concepts.

## Gaps

- **Averaged word vectors.** Arora et al., "A simple but tough-to-beat baseline for sentence embeddings" (ICLR 2017), was not reachable. OpenReview returned an HTML page instead of the PDF twice. Step 1 of concept 1 has no source of its own.
- **Read but not recorded.** The Universal Sentence Encoder (2018), Shaar et al. 2020, Augmented SBERT (2020), and backward-compatible training (Shen et al. 2020) repeat findings of kept records. The Universal Sentence Encoder belongs between steps 2 and 3 of concept 1.
- **Current embedding models.** No record covers a general model after SimCSE, such as E5.
- **Direction of entailment in current encoders.** I found no recent measurement. A3-SR-11 is an argument from 2015.
- **Text reuse with rewording.** No record measures embedding similarity for reworded text reuse.
- **NLI as a filter on vector candidates.** No record tests the pipeline of vector search followed by an NLI check for claim matching or same-idea detection.
- **Vector versioning.** The fetched OpenAI page held only navigation. No record describes storing the model version with each vector; product features belong to area 2.
- **STS criticism sources.** MTEB cites Neelakantan et al. 2022 and Wang et al. 2021 for the weak correlation of STS with other uses. I did not read either.
- **Hashing between 2007 and 2021.** I found no source for the criticism that moved practice from SimHash to MinHash with exact checks.
