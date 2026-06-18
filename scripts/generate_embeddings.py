from pathlib import Path
from sentence_transformers import SentenceTransformer
import json


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

chunks_folder = Path("data/chunks")
output_folder = Path("data/embeddings")

output_folder.mkdir(exist_ok=True)


for chunk_file in chunks_folder.glob("*.json"):

    print(f"Processing {chunk_file.name}")

    with open(chunk_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    embedded_chunks = []

    for chunk in chunks:

        embedding_text = (
            f"{chunk['section']}\n\n"
            f"{chunk['text']}"
        )

        embedding = model.encode(
           embedding_text,
           normalize_embeddings=True
        ).tolist()

        embedded_chunks.append({
            "subject": chunk["subject"],
            "chapter_file": chunk["chapter_file"],
            "section": chunk["section"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": embedding
        })

    output_file = (
        output_folder /
        f"{chunk_file.stem}_embeddings.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            embedded_chunks,
            f,
            ensure_ascii=False
        )

print("Embedding generation complete.")