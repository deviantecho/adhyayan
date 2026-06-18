from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings_folder = Path("data/embeddings")

all_chunks = []


for embedding_file in embeddings_folder.glob("*.json"):

    with open(
        embedding_file,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

        all_chunks.extend(chunks)


print(f"Loaded {len(all_chunks)} chunks")


question = input(
    "\nAsk a question: "
)


question_embedding = model.encode(
    question
)


scores = []


for chunk in all_chunks:

    similarity = cosine_similarity(
        [question_embedding],
        [chunk["embedding"]]
    )[0][0]

    scores.append(
        (similarity, chunk)
    )


scores.sort(
    reverse=True,
    key=lambda x: x[0]
)


print("\nTOP RESULTS\n")


for score, chunk in scores[:3]:

    print("=" * 80)

    print(
        f"Score: {score:.4f}"
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

    print()

    print(
        chunk["text"][:500]
    )

    print("\n")