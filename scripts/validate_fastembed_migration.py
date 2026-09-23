"""
Validation harness for the fastembed (ONNX) query-embedding migration.

Run from the PROJECT ROOT with a Python env that has BOTH the new runtime deps
(fastembed) AND, ideally, the OLD deps (sentence-transformers) still installed so
the empirical comparison in step B can run. If sentence-transformers is not
available, step B is skipped gracefully and the rest still runs.

    python scripts/validate_fastembed_migration.py

It performs:
  A. FAISS index integrity  (785 vectors, dim 384, IndexFlatIP)
  B. Embedding compatibility: fastembed vs sentence-transformers on the SAME
     queries (cosine agreement, per-query FAISS top-1/top-5 comparison,
     behavior around the 0.35 threshold)
  C. Query embedding shape + normalization checks
  D. Optional crude RSS memory read for the fastembed embedder

This script does NOT modify the index or any project files.
"""

import json
import os
import sys

import numpy as np
import faiss

# Representative Adhyayan queries spanning both subjects, plus a deliberate
# near-threshold / out-of-domain probe to inspect behavior around 0.35.
TEST_QUERIES = [
    "What is a balanced chemical equation?",
    "Explain the process of photosynthesis in plants.",
    "State the quadratic formula and when it is used.",
    "What is the difference between reflection and refraction of light?",
    "Define an arithmetic progression and give its nth term.",
    "How do organisms reproduce asexually?",
    "What is the price of a movie ticket in Mumbai?",  # out-of-domain probe
]

THRESHOLD = 0.35
INDEX_PATH = "data/faiss_index.bin"
META_PATH = "data/chunk_metadata.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_index_and_meta():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks


def section_a(index, chunks):
    print("\n=== A. FAISS INDEX INTEGRITY ===")
    print(f"  ntotal (vector count): {index.ntotal}  (expect 785)")
    print(f"  dimension d:           {index.d}  (expect 384)")
    print(f"  index class:           {type(index).__name__}  (expect IndexFlatIP)")
    print(f"  metric_type:           {index.metric_type}  (expect {faiss.METRIC_INNER_PRODUCT}=INNER_PRODUCT)")
    print(f"  metadata chunks:       {len(chunks)}  (expect 785)")
    ok = (
        index.ntotal == 785
        and index.d == 384
        and type(index).__name__ == "IndexFlatIP"
        and index.metric_type == faiss.METRIC_INNER_PRODUCT
        and len(chunks) == 785
    )
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def fastembed_encoder():
    from fastembed import TextEmbedding
    model = TextEmbedding(model_name=MODEL_NAME)

    def encode(text):
        vec = next(iter(model.embed([text])))
        vec = np.asarray(vec, dtype="float32")
        n = np.linalg.norm(vec)
        return vec / n if n > 0 else vec

    return encode


def st_encoder():
    """Old implementation, if still installed."""
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:  # noqa
        print(f"  (sentence-transformers not available: {e}) -> skipping step B comparison")
        return None
    model = SentenceTransformer("all-MiniLM-L6-v2")

    def encode(text):
        return np.asarray(
            model.encode(text, normalize_embeddings=True), dtype="float32"
        )

    return encode


def faiss_search(index, vec, k=5):
    q = np.array([vec], dtype="float32")
    scores, idx = index.search(q, k)
    return scores[0], idx[0]


def section_c_shape_norm(fe_encode):
    print("\n=== C. QUERY EMBEDDING SHAPE + NORMALIZATION (fastembed) ===")
    v = fe_encode(TEST_QUERIES[0])
    print(f"  shape: {v.shape}  (expect (384,))")
    print(f"  dtype: {v.dtype}")
    print(f"  L2 norm: {np.linalg.norm(v):.6f}  (expect ~1.0)")
    ok = v.shape == (384,) and abs(np.linalg.norm(v) - 1.0) < 1e-3
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def section_b_compat(index, chunks, fe_encode, st_encode):
    print("\n=== B. EMBEDDING COMPATIBILITY: fastembed vs sentence-transformers ===")
    print(f"{'query':45s} | cos(fe,st) | fe_top1 | st_top1 | top5_overlap | fe>=0.35 | st>=0.35")
    print("-" * 120)
    all_cos = []
    top1_match = 0
    top5_overlaps = []
    threshold_disagree = 0

    for qtext in TEST_QUERIES:
        fe = fe_encode(qtext)
        fe_scores, fe_idx = faiss_search(index, fe, k=5)

        if st_encode is not None:
            st = st_encode(qtext)
            cos = float(np.dot(fe, st))  # both unit vectors -> cosine
            st_scores, st_idx = faiss_search(index, st, k=5)
            overlap = len(set(fe_idx.tolist()) & set(st_idx.tolist()))
            fe_pass = fe_scores[0] >= THRESHOLD
            st_pass = st_scores[0] >= THRESHOLD
            if fe_idx[0] == st_idx[0]:
                top1_match += 1
            if fe_pass != st_pass:
                threshold_disagree += 1
            top5_overlaps.append(overlap)
            all_cos.append(cos)
            print(f"{qtext[:45]:45s} | {cos:10.6f} | {fe_scores[0]:7.4f} | {st_scores[0]:7.4f} | {overlap:12d} | {str(fe_pass):8s} | {str(st_pass)}")
        else:
            print(f"{qtext[:45]:45s} | {'n/a':>10s} | {fe_scores[0]:7.4f} | {'n/a':>7s} | {'n/a':>12s} | {str(fe_scores[0] >= THRESHOLD):8s} | n/a")

    if st_encode is not None and all_cos:
        print("-" * 120)
        print(f"  mean cos(fe,st):        {np.mean(all_cos):.6f}  (expect > 0.999 if truly compatible)")
        print(f"  min  cos(fe,st):        {np.min(all_cos):.6f}")
        print(f"  top-1 index match:      {top1_match}/{len(TEST_QUERIES)}")
        print(f"  mean top-5 overlap:     {np.mean(top5_overlaps):.2f}/5")
        print(f"  threshold disagreements: {threshold_disagree} (queries where 0.35 decision flips)")
        strong = np.mean(all_cos) > 0.999 and top1_match == len(TEST_QUERIES) and threshold_disagree == 0
        print(f"  RESULT: {'STRONG COMPAT' if strong else 'REVIEW NEEDED - inspect near-threshold rows'}")


def section_d_memory():
    print("\n=== D. CRUDE MEMORY (fastembed embedder resident) ===")
    try:
        import psutil  # optional
        proc = psutil.Process(os.getpid())
        before = proc.memory_info().rss / 1e6
        fe = fastembed_encoder()
        _ = fe("warmup query")
        after = proc.memory_info().rss / 1e6
        print(f"  RSS before embedder: {before:.1f} MB")
        print(f"  RSS after  embedder: {after:.1f} MB")
        print(f"  delta:               {after - before:.1f} MB")
        print("  (Compare against the previous torch-based startup which OOMed at 512MB.)")
    except Exception as e:  # noqa
        print(f"  psutil not available or error ({e}); skip. Measure on Render instead.")


def main():
    if not os.path.exists(INDEX_PATH):
        print(f"ERROR: run from project root; {INDEX_PATH} not found.")
        sys.exit(1)

    index, chunks = load_index_and_meta()
    a_ok = section_a(index, chunks)

    fe_encode = fastembed_encoder()
    c_ok = section_c_shape_norm(fe_encode)

    st_encode = st_encoder()
    section_b_compat(index, chunks, fe_encode, st_encode)

    section_d_memory()

    print("\n=== SUMMARY ===")
    print(f"  A index integrity: {'PASS' if a_ok else 'FAIL'}")
    print(f"  C shape/norm:      {'PASS' if c_ok else 'FAIL'}")
    print("  B compatibility:   see rows above (threshold disagreements must be 0 to keep 0.35 as-is)")


if __name__ == "__main__":
    main()
