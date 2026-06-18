from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np


# ----------------------------------
# Load embedding model
# ----------------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ----------------------------------
# Load FAISS index
# ----------------------------------

index = faiss.read_index(
    "data/faiss_index.bin"
)


# ----------------------------------
# Load metadata
# ----------------------------------

with open(
    "data/chunk_metadata.json",
    "r",
    encoding="utf-8"
) as f:

    chunks = json.load(f)


# ----------------------------------
# Ask question
# ----------------------------------

question = input(
    "\nAsk a question: "
)


# ----------------------------------
# Create query embedding
# Must match embedding generation
# ----------------------------------

question_embedding = model.encode(
    question,
    normalize_embeddings=True
)

question_embedding = np.array(
    [question_embedding],
    dtype="float32"
)


# ----------------------------------
# Search FAISS
# ----------------------------------

k = 5

scores, indices = index.search(
    question_embedding,
    k
)


# ----------------------------------
# Display results
# ----------------------------------

print("\nTOP RESULTS\n")


for i in range(k):

    chunk = chunks[
        indices[0][i]
    ]

    print("=" * 80)

    print(
        f"Similarity: {scores[0][i]:.4f}"
    )

    print(
        f"Subject: {chunk['subject']}"
    )

    print(
        f"Chapter: {chunk['chapter_file']}"
    )

    print(
        f"Section: {chunk['section']}"
    )

    print(
        f"Chunk ID: {chunk.get('chunk_id', 'N/A')}"
    )

    print()

    print(
        chunk["text"][:800]
    )

    print("\n")