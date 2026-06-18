import os
import json
import faiss
import numpy as np

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai


# Load environment variables
load_dotenv()


# Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Load FAISS index
index = faiss.read_index(
    "data/faiss_index.bin"
)


# Load chunk metadata
with open(
    "data/chunk_metadata.json",
    "r",
    encoding="utf-8"
) as f:

    chunks = json.load(f)


print(f"Loaded {len(chunks)} chunks")


# Conversation memory
chat_history = []


while True:

    question = input(
        "\nAsk a question (type 'exit' to quit): "
    )

    if question.lower() == "exit":
        break

    print("Processing question...")

    # Build conversation history
    history_text = ""

    for message in chat_history[-6:]:

        history_text += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    # Rewrite follow-up questions
    if len(chat_history) > 0:

        rewrite_prompt = f"""
Previous Conversation:

{history_text}

Current Question:

{question}

Rewrite the current question into a complete standalone question.

Only return the rewritten question.
"""

        try:

            rewrite_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=rewrite_prompt
            )

            search_query = (
                rewrite_response.text.strip()
            )

            print(
                f"\nRewritten Query: {search_query}"
            )

        except Exception:

            search_query = question

    else:

        search_query = question

    # Convert query to embedding
    question_embedding = embedding_model.encode(
        search_query
    )

    question_embedding = np.array(
        [question_embedding],
        dtype="float32"
    )

    # Retrieve chunks
    k = 3

    distances, indices = index.search(
        question_embedding,
        k
    )

    context = ""
    sources = []

    for i in range(k):

        chunk = chunks[
            indices[0][i]
        ]

        sources.append(
            f"{chunk['subject']} > "
            f"{chunk['chapter_file']} > "
            f"{chunk['section']}"
        )

        context += f"""
Subject: {chunk['subject']}
Chapter: {chunk['chapter_file']}
Section: {chunk['section']}

{chunk['text']}

--------------------------------
"""

    # Final answer prompt
    prompt = f"""
You are an NCERT Class 10 tutor.

Previous Conversation:

{history_text}

Context:

{context}

Current Question:

{question}

Answer ONLY using the provided NCERT context.

If the answer is not present in the context, say:

'I could not find this information in the NCERT data.'

Explain in a Class 10 friendly manner.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    except Exception as e:

        print(
            f"\nGemini Error: {e}"
        )

        continue

    print("\nANSWER\n")

    print(response.text)

    # Save conversation
    chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    chat_history.append(
        {
            "role": "assistant",
            "content": response.text
        }
    )

    print("\nSOURCES\n")

    unique_sources = list(
        dict.fromkeys(sources)
    )

    for i, source in enumerate(
        unique_sources,
        start=1
    ):

        print(
            f"{i}. {source}"
        )