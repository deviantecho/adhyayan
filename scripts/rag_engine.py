"""
RAG Engine with Provider Abstraction and Streaming Support
Supports both Gemini (production) and OmniRoute (local development)
"""

import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import json
import faiss
import warnings
import numpy as np
import time

from dotenv import load_dotenv
from fastembed import TextEmbedding
from .llm import get_provider
from .answer_schema import normalize_response, Answer


# --------------------------------------------------
# Lightweight query embedder (ONNX via fastembed)
# --------------------------------------------------
# Replaces the sentence-transformers + PyTorch runtime stack, which exceeded
# Render's 512MB free-tier memory limit at startup. fastembed serves the same
# `sentence-transformers/all-MiniLM-L6-v2` model via ONNX Runtime (no torch):
#   - 384 dimensions
#   - mean pooling
#   - L2-normalized output by default
# These match how the existing 785 FAISS document vectors were generated
# (all-MiniLM-L6-v2 with normalize_embeddings=True), so the existing
# IndexFlatIP (cosine) index is reused WITHOUT rebuilding.
#
# This wrapper preserves the exact call signature previously used against the
# sentence-transformers model:
#     embedding_model.encode(text, normalize_embeddings=True)
# so downstream retrieval logic is unchanged.

_FASTEMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class _QueryEmbedder:
    """Adapter exposing a sentence-transformers-like .encode() over fastembed.

    fastembed's TextEmbedding for all-MiniLM-L6-v2 already applies mean pooling
    and L2 normalization, producing 384-dim unit vectors. The `normalize_embeddings`
    argument is accepted for signature compatibility; fastembed normalizes by
    default, so a defensive re-normalization is applied only when requested to
    guarantee unit-length vectors for the IndexFlatIP (cosine) index.
    """

    def __init__(self, model_name: str = _FASTEMBED_MODEL_NAME):
        self._model = TextEmbedding(model_name=model_name)

    def encode(self, text, normalize_embeddings: bool = True):
        # fastembed.embed() takes an iterable of documents and returns a
        # generator of numpy arrays (float32, shape (384,)).
        vector = next(iter(self._model.embed([text])))
        vector = np.asarray(vector, dtype="float32")

        if normalize_embeddings:
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

        return vector


warnings.filterwarnings("ignore")
load_dotenv()

# Debug timing - controlled by environment variable
DEBUG_TIMING = os.getenv("DEBUG_TIMING", "false").lower() == "true"


def load_resources():
    if DEBUG_TIMING:
        print("\n[INIT] Loading AI resources...")

    # Load LLM provider (Gemini or OmniRoute based on LLM_PROVIDER env var)
    t_provider_start = time.time()
    llm_provider = get_provider()
    t_provider_end = time.time()
    if DEBUG_TIMING:
        print(f"[INIT] Provider '{llm_provider.__class__.__name__}' loaded in {t_provider_end - t_provider_start:.3f}s")

    # Embedding model - loaded once at startup
    t_embed_model_start = time.time()
    embedding_model = _QueryEmbedder(_FASTEMBED_MODEL_NAME)
    t_embed_model_end = time.time()
    if DEBUG_TIMING:
        print(f"[INIT] Embedding model loaded in {t_embed_model_end - t_embed_model_start:.3f}s")

    # FAISS index - loaded once at startup
    t_faiss_start = time.time()
    index = faiss.read_index("data/faiss_index.bin")
    t_faiss_end = time.time()
    if DEBUG_TIMING:
        print(f"[INIT] FAISS index loaded in {t_faiss_end - t_faiss_start:.3f}s")

    # Chunk metadata - loaded once at startup
    t_chunks_start = time.time()
    with open("data/chunk_metadata.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    t_chunks_end = time.time()
    if DEBUG_TIMING:
        print(f"[INIT] {len(chunks)} chunks loaded in {t_chunks_end - t_chunks_start:.3f}s")

    t_total = time.time() - t_provider_start
    if DEBUG_TIMING:
        print(f"[INIT] All resources loaded in {t_total:.3f}s total")

    return (llm_provider, embedding_model, index, chunks)


llm_provider, embedding_model, index, chunks = load_resources()
if DEBUG_TIMING:
    print("RAG_ENGINE READY - Per-request initialization NOT happening\n")


# Chapter name mappings remain the same
SCIENCE_CHAPTERS = {
    "chapter1": "Chemical Reactions and Equations",
    "chapter2": "Acids, Bases and Salts",
    "chapter3": "Metals and Non-metals",
    "chapter4": "Carbon and its Compounds",
    "chapter5": "Periodic Classification of Elements",
    "chapter6": "Life Processes",
    "chapter7": "How Do Organisms Reproduce?",
    "chapter8": "Heredity",
    "chapter9": "Light - Reflection and Refraction",
    "chapter10": "The Human Eye and the Colourful World",
    "chapter11": "Electricity",
    "chapter12": "Magnetic Effects of Electric Current",
    "chapter13": "Our Environment"
}

MATH_CHAPTERS = {
    "chapter1": "Real Numbers",
    "chapter2": "Polynomials",
    "chapter3": "Pair of Linear Equations in Two Variables",
    "chapter4": "Quadratic Equations",
    "chapter5": "Arithmetic Progressions",
    "chapter6": "Triangles",
    "chapter7": "Coordinate Geometry",
    "chapter8": "Introduction to Trigonometry",
    "chapter9": "Some Applications of Trigonometry",
    "chapter10": "Circles",
    "chapter11": "Constructions",
    "chapter12": "Areas Related to Circles",
    "chapter13": "Surface Areas and Volumes",
    "chapter14": "Statistics",
    "chapter15": "Probability"
}


def get_chapter_name(subject, chapter_file):
    if subject.lower() == "science":
        return SCIENCE_CHAPTERS.get(chapter_file, chapter_file)
    if subject.lower() == "mathematics":
        return MATH_CHAPTERS.get(chapter_file, chapter_file)
    return chapter_file


def clean_section_name(section):
    section = section.strip()
    while len(section) > 0 and (section[0].isdigit() or section[0] == "."):
        section = section[1:]
    section = section.strip()
    if section.isupper():
        section = section.title()
    return section


def ask_question(question, chat_history, subject_filter="All Subjects"):
    """
    Non-streaming RAG question answering with precise latency instrumentation.
    """
    timings = {}
    t_start = time.time()

    # T0: Request received - t_start is already set

    # T1: History/query preparation
    t1_start = time.time()
    history_text = ""
    for message in chat_history[-6:]:
        history_text += f"{message['role']}: {message['content']}\n"
    search_query = question
    t1_end = time.time()
    timings['query_prep'] = t1_end - t1_start

    # --------------------------------------------------
    # Query Rewriting (OPTIMIZED: only with history)
    # --------------------------------------------------

    t_rewrite = 0
    if len(chat_history) > 0:
        t_rewrite_start = time.time()

        rewrite_prompt = f"""
Previous Conversation:

{history_text}

Current Question:

{question}

Rewrite the current question into a complete standalone question.

Only return the rewritten question.
"""

        try:
            search_query = llm_provider.generate(rewrite_prompt).strip()
            t_rewrite = time.time() - t_rewrite_start
            timings['query_rewrite'] = t_rewrite
        except Exception:
            search_query = question
            t_rewrite = time.time() - t_rewrite_start
            timings['query_rewrite'] = t_rewrite
    else:
        timings['query_rewrite'] = 0

    # T2: Embedding start
    t2_start = time.time()
    question_embedding = embedding_model.encode(search_query, normalize_embeddings=True)
    question_embedding = np.array([question_embedding], dtype="float32")
    t2_end = time.time()
    timings['embedding'] = t2_end - t2_start

    # T4: FAISS search start
    t4_start = time.time()
    retrieval_k = 15
    distances, indices = index.search(question_embedding, retrieval_k)
    t4_end = time.time()
    timings['faiss'] = t4_end - t4_start

    # Relevance Filter
    if distances[0][0] < 0.35:
        return (
            "I could not find this information in the NCERT data.",
            [],
            [],
            chat_history
        )

    # Subject Filtering
    filtered_chunks = []
    filtered_distances = []

    for position, idx in enumerate(indices[0]):
        chunk = chunks[idx]

        if subject_filter == "All Subjects":
            filtered_chunks.append(chunk)
            filtered_distances.append(distances[0][position])
        elif chunk["subject"].lower() == subject_filter.lower():
            filtered_chunks.append(chunk)
            filtered_distances.append(distances[0][position])

    if len(filtered_chunks) == 0:
        return (
            f"No relevant chunks found in {subject_filter}.",
            [],
            [],
            chat_history
        )

    top_chunks = filtered_chunks[:5]
    top_distances = filtered_distances[:5]

    # T6: Context construction
    t6_start = time.time()
    context = ""
    sources = []
    retrieval_details = []

    for rank, (chunk, distance) in enumerate(zip(top_chunks, top_distances), start=1):
        chapter_name = get_chapter_name(chunk["subject"], chunk["chapter_file"])

        sources.append(
           f"{chunk['subject'].title()} > "
           f"{chapter_name} > "
           f"{clean_section_name(chunk['section'])}"
        )

        retrieval_details.append({
            "rank": rank,
            "subject": chunk["subject"].title(),
            "chapter": chapter_name,
            "section": clean_section_name(chunk["section"]),
            "distance": round(float(distance), 4)
        })

        context += f"""
Subject: {chunk['subject']}
Chapter: {chapter_name}
Section: {chunk['section']}

{chunk['text']}

--------------------------------
"""
    t6_end = time.time()
    timings['context'] = t6_end - t6_start

    # T8: Prompt construction
    t8_start = time.time()
    prompt = f"""
You are an NCERT Class 10 tutor providing structured educational explanations.

Previous Conversation:

{history_text}

Context:

{context}

Current Question:

{question}

Instructions:

1. Answer ONLY using the provided NCERT context.
2. Do not use outside knowledge.
3. If the answer is not present, say: 'I could not find this information in the NCERT data.'
4. Structure your answer to help students learn effectively.

You MUST structure every educational answer using these EXACT semantic markers:

<KEY_IDEA>
[One concise statement capturing the central concept - REQUIRED]
</KEY_IDEA>

<EXPLANATION>
[Clear explanation in short paragraphs using Class 10 level language - REQUIRED]
</EXPLANATION>

<EXAMPLE title="descriptive title">
[Concrete example when it helps understanding - OPTIONAL]

For chemical reactions or mathematical formulas within the example:
<EQUATION>
[equation here]
</EQUATION>

[Continue example explanation after equation]
</EXAMPLE>

<EQUATION>
[Standalone equations outside examples - OPTIONAL]
</EQUATION>

CRITICAL FORMATTING RULES:
1. <KEY_IDEA> and <EXPLANATION> are MANDATORY for all educational answers
2. Use <EQUATION> tags for ANY equation (chemistry, mathematics, physics)
3. Multiple <EXAMPLE> blocks are allowed when multiple examples help
4. Multiple <EQUATION> blocks within one <EXAMPLE> are allowed
5. <EQUATION> blocks outside <EXAMPLE> are allowed for standalone formulas
6. NEVER use plain headings like "KEY IDEA:" or "EXAMPLE:" - only XML tags
7. Example title attribute is optional: <EXAMPLE> or <EXAMPLE title="...">
8. Preserve the natural order of blocks in your response
9. Use **bold** for emphasis and *italic* for terms when appropriate
10. Use bullet points (-) for lists when helpful
11. Keep paragraphs short and focused

For simple non-educational queries (greetings, simple facts), structured tags are not required.
"""
    t8_end = time.time()
    timings['prompt'] = t8_end - t8_start

    # T9: Provider generation start
    t9_start = time.time()
    try:
        answer = llm_provider.generate(prompt)
        t9_end = time.time()
        timings['provider_gen'] = t9_end - t9_start
    except Exception as e:
        answer = f"LLM API Error:\n\n{e}"
        t9_end = time.time()
        timings['provider_gen'] = t9_end - t9_start

    # Save chat history
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": answer})

    unique_sources = list(dict.fromkeys(sources))

    t_total = time.time() - t_start
    timings['total'] = t_total

    # Print detailed timing breakdown
    if DEBUG_TIMING:
        print(f"\n[TIMING BREAKDOWN]")
        print(f"  request:        {0.000:.3f}s")
        print(f"  query_prep:     {timings['query_prep']:.3f}s")
        print(f"  query_rewrite:  {timings['query_rewrite']:.3f}s" + (" (SKIPPED)" if timings['query_rewrite'] == 0 else ""))
        print(f"  embedding:      {timings['embedding']:.3f}s")
        print(f"  FAISS:          {timings['faiss']:.3f}s")
        print(f"  context:        {timings['context']:.3f}s")
        print(f"  prompt:         {timings['prompt']:.3f}s")
        print(f"  provider_gen:   {timings['provider_gen']:.3f}s")
        print(f"  TOTAL:          {timings['total']:.3f}s")

    return (answer, unique_sources, retrieval_details, chat_history)


def ask_question_stream(question, chat_history, subject_filter="All Subjects"):
    """
    Streaming version with PHASE 3.16H PRECISE LATENCY INSTRUMENTATION.

    Timing stages:
    T0  - request received
    T1  - history/query preparation complete
    T2  - embedding start
    T3  - embedding complete
    T4  - FAISS search start
    T5  - FAISS search complete
    T6  - context construction start
    T7  - context construction complete
    T8  - prompt construction complete
    T9  - provider.generate_stream() CALLED
    T10 - first provider chunk received
    T11 - first SSE content event sent
    T12 - total completion
    """

    timings = {}
    t_start = time.time()

    # ========== T1: History/query preparation ==========
    t1_start = time.time()
    history_text = ""
    for message in chat_history[-6:]:
        history_text += f"{message['role']}: {message['content']}\n"
    search_query = question
    t1_end = time.time()
    timings['t1_query_prep'] = t1_end - t1_start

    # ========== Query rewriting (optimized) ==========
    t_rewrite = 0
    if len(chat_history) > 0:
        t_rewrite_start = time.time()

        rewrite_prompt = f"""
Previous Conversation:

{history_text}

Current Question:

{question}

Rewrite the current question into a complete standalone question.

Only return the rewritten question.
"""

        try:
            search_query = llm_provider.generate(rewrite_prompt).strip()
            t_rewrite = time.time() - t_rewrite_start
        except Exception:
            search_query = question
            t_rewrite = time.time() - t_rewrite_start
    timings['t1_query_rewrite'] = t_rewrite

    # ========== T2-T3: Create Embedding ==========
    t2_start = time.time()
    question_embedding = embedding_model.encode(search_query, normalize_embeddings=True)
    question_embedding = np.array([question_embedding], dtype="float32")
    t3_end = time.time()
    timings['t2_t3_embedding'] = t3_end - t2_start

    # ========== T4-T5: FAISS Retrieval ==========
    t4_start = time.time()
    retrieval_k = 15
    distances, indices = index.search(question_embedding, retrieval_k)
    t5_end = time.time()
    timings['t4_t5_faiss'] = t5_end - t4_start

    # ========== Relevance Filter ==========
    if distances[0][0] < 0.35:
        yield {
            "type": "error",
            "error": "I could not find this information in the NCERT data."
        }
        return

    # ========== Subject Filtering ==========
    filtered_chunks = []
    filtered_distances = []

    for position, idx in enumerate(indices[0]):
        chunk = chunks[idx]

        if subject_filter == "All Subjects":
            filtered_chunks.append(chunk)
            filtered_distances.append(distances[0][position])
        elif chunk["subject"].lower() == subject_filter.lower():
            filtered_chunks.append(chunk)
            filtered_distances.append(distances[0][position])

    if len(filtered_chunks) == 0:
        yield {
            "type": "error",
            "error": f"No relevant chunks found in {subject_filter}."
        }
        return

    top_chunks = filtered_chunks[:5]
    top_distances = filtered_distances[:5]

    # ========== T6-T7: Build Context ==========
    t6_start = time.time()
    context = ""
    sources = []
    retrieval_details = []

    for rank, (chunk, distance) in enumerate(zip(top_chunks, top_distances), start=1):
        chapter_name = get_chapter_name(chunk["subject"], chunk["chapter_file"])

        sources.append(
           f"{chunk['subject'].title()} > "
           f"{chapter_name} > "
           f"{clean_section_name(chunk['section'])}"
        )

        retrieval_details.append({
            "rank": rank,
            "subject": chunk["subject"].title(),
            "chapter": chapter_name,
            "section": clean_section_name(chunk["section"]),
            "distance": round(float(distance), 4)
        })

        context += f"""
Subject: {chunk['subject']}
Chapter: {chapter_name}
Section: {chunk['section']}

{chunk['text']}

--------------------------------
"""
    t7_end = time.time()
    timings['t6_t7_context'] = t7_end - t6_start

    # ========== T8: Prompt Construction ==========
    t8_start = time.time()
    prompt = f"""
You are an NCERT Class 10 tutor providing structured educational explanations.

Previous Conversation:

{history_text}

Context:

{context}

Current Question:

{question}

Instructions:

1. Answer ONLY using the provided NCERT context.
2. Do not use outside knowledge.
3. If the answer is not present, say: 'I could not find this information in the NCERT data.'
4. Structure your answer to help students learn effectively.

You MUST structure every educational answer using these EXACT semantic markers:

<KEY_IDEA>
[One concise statement capturing the central concept - REQUIRED]
</KEY_IDEA>

<EXPLANATION>
[Clear explanation in short paragraphs using Class 10 level language - REQUIRED]
</EXPLANATION>

<EXAMPLE title="descriptive title">
[Concrete example when it helps understanding - OPTIONAL]

For chemical reactions or mathematical formulas within the example:
<EQUATION>
[equation here]
</EQUATION>

[Continue example explanation after equation]
</EXAMPLE>

<EQUATION>
[Standalone equations outside examples - OPTIONAL]
</EQUATION>

CRITICAL FORMATTING RULES:
1. <KEY_IDEA> and <EXPLANATION> are MANDATORY for all educational answers
2. Use <EQUATION> tags for ANY equation (chemistry, mathematics, physics)
3. Multiple <EXAMPLE> blocks are allowed when multiple examples help
4. Multiple <EQUATION> blocks within one <EXAMPLE> are allowed
5. <EQUATION> blocks outside <EXAMPLE> are allowed for standalone formulas
6. NEVER use plain headings like "KEY IDEA:" or "EXAMPLE:" - only XML tags
7. Example title attribute is optional: <EXAMPLE> or <EXAMPLE title="...">
8. Preserve the natural order of blocks in your response
9. Use **bold** for emphasis and *italic* for terms when appropriate
10. Use bullet points (-) for lists when helpful
11. Keep paragraphs short and focused

For simple non-educational queries (greetings, simple facts), structured tags are not required.
"""
    t8_end = time.time()
    timings['t8_prompt'] = t8_end - t8_start

    unique_sources = list(dict.fromkeys(sources))

    # ========== T9: Provider streaming called ==========
    t9_start = time.time()

    # Yield metadata first
    t_retrieval_complete = time.time()
    timings['t9_retrieval_complete'] = t_retrieval_complete - t_start

    yield {
        "type": "metadata",
        "sources": unique_sources,
        "retrieval_details": retrieval_details
    }

    # ========== T10-T11: LLM Streaming ==========
    accumulated_answer = ""
    t_first_chunk = None
    t_first_sse = None

    try:
        for chunk in llm_provider.generate_stream(prompt):
            current_time = time.time()

            if t_first_chunk is None:
                t_first_chunk = current_time
                timings['t10_first_provider_chunk'] = t_first_chunk - t_start
                if DEBUG_TIMING:
                    print(f"\n[TIMING] Provider first chunk: {timings['t10_first_provider_chunk']:.3f}s")

            accumulated_answer += chunk

            if t_first_sse is None:
                t_first_sse = current_time
                timings['t11_first_sse_content'] = t_first_sse - t_start
                if DEBUG_TIMING:
                    print(f"[TIMING] SSE first content: {timings['t11_first_sse_content']:.3f}s")

            yield {
                "type": "content",
                "content": chunk
            }

    except Exception as e:
        # Emit explicit error event - FIX for stream freeze
        yield {
            "type": "error",
            "error": f"Generation failed: {str(e)}"
        }
        return

    # ========== T12: Complete ==========
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": accumulated_answer})

    t12_complete = time.time()
    timings['t12_total'] = t12_complete - t_start

    # Print final breakdown
    if DEBUG_TIMING:
        print(f"\n[TIMING BREAKDOWN - STREAMING]")
        print(f"  T0  request:          0.000s")
        print(f"  T1  query_prep:       {timings['t1_query_prep']:.3f}s")
    rewrite_msg = " (SKIPPED)" if timings['t1_query_rewrite'] == 0 else ""
    print(f"  T1  query_rewrite:    {timings['t1_query_rewrite']:.3f}s{rewrite_msg}")
    print(f"  T2-T3 embedding:      {timings['t2_t3_embedding']:.3f}s")
    print(f"  T4-T5 FAISS:          {timings['t4_t5_faiss']:.3f}s")
    print(f"  T6-T7 context:        {timings['t6_t7_context']:.3f}s")
    print(f"  T8  prompt:           {timings['t8_prompt']:.3f}s")
    print(f"  T9  retrieval done:   {timings['t9_retrieval_complete']:.3f}s")
    print(f"  T10 first chunk:      {timings.get('t10_first_provider_chunk', 'N/A'):.3f}s" if isinstance(timings.get('t10_first_provider_chunk'), float) else "  T10 first chunk:      N/A")
    print(f"  T11 first SSE:        {timings.get('t11_first_sse_content', 'N/A'):.3f}s" if isinstance(timings.get('t11_first_sse_content'), float) else "  T11 first SSE:        N/A")
    print(f"  T12 total:            {timings['t12_total']:.3f}s")

    # Bottleneck analysis
    retrieval_time = timings['t9_retrieval_complete']
    provider_time = timings['t12_total'] - timings['t9_retrieval_complete']
    print(f"\n[BOTTLENECK ANALYSIS]")
    print(f"  Retrieval (T0-T9):    {retrieval_time:.3f}s ({100*retrieval_time/timings['t12_total']:.1f}%)")
    print(f"  Provider (T9-T12):    {provider_time:.3f}s ({100*provider_time/timings['t12_total']:.1f}%)")

    # ========== NORMALIZE RESPONSE (Phase 3.16O) ==========
    # Convert the complete LLM response into normalized Answer object
    # This ensures provider-agnostic structure for frontend
    normalized = normalize_response(accumulated_answer)

    # Attach sources and retrieval details to the normalized answer
    normalized.sources = unique_sources
    normalized.retrieval_details = retrieval_details

    # ========== EMIT EXPLICIT DONE EVENT WITH STRUCTURED ANSWER ==========
    # This is MANDATORY - frontend uses validated structure, never raw text

    done_event = {
        "type": "done",
        "updated_history": chat_history,
        "answer": normalized.to_dict()
    }

    yield done_event