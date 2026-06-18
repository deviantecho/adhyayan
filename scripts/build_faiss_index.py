from pathlib import Path
import json
import faiss
import numpy as np


embeddings_folder = Path("data/embeddings")

all_chunks = []
all_embeddings = []


for embedding_file in embeddings_folder.glob("*.json"):

    print(
        f"Loading {embedding_file.name}"
    )

    with open(
        embedding_file,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

        for chunk in chunks:

            all_chunks.append(
                chunk
            )

            all_embeddings.append(
                chunk["embedding"]
            )


if not all_embeddings:

    raise ValueError(
        "No embeddings found!"
    )


embeddings_array = np.array(
    all_embeddings,
    dtype="float32"
)


print(
    f"Loaded {len(all_embeddings)} embeddings"
)

print(
    f"Shape: {embeddings_array.shape}"
)


dimension = embeddings_array.shape[1]


# ----------------------------------
# Cosine Similarity Search
# Works because embeddings were
# normalized during generation
# ----------------------------------

index = faiss.IndexFlatIP(
    dimension
)


index.add(
    embeddings_array
)


faiss.write_index(
    index,
    "data/faiss_index.bin"
)


with open(
    "data/chunk_metadata.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_chunks,
        f,
        ensure_ascii=False
    )


print(
    f"Indexed {len(all_chunks)} chunks"
)

print(
    f"Embedding dimension: {dimension}"
)

print(
    "FAISS index created successfully"
)