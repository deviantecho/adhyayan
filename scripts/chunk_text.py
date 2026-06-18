
from pathlib import Path
import re
import json


input_root = Path("data/clean_text")
output_root = Path("data/chunks")

output_root.mkdir(exist_ok=True)


section_pattern = re.compile(
    r"^\d+\.\d+(\.\d+)?\s+[A-Z]"
)


def split_into_subchunks(
    text,
    max_words=250,
    overlap=50
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + max_words

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        start += (
            max_words - overlap
        )

    return chunks

for subject_folder in input_root.iterdir():

    if not subject_folder.is_dir():
        continue

    chunks = []

    for txt_file in subject_folder.glob("*.txt"):

        text = txt_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        raw_lines = text.splitlines()

        # ----------------------------------
        # Merge broken headings
        # ----------------------------------

        lines = []

        i = 0

        while i < len(raw_lines):

            line = raw_lines[i].strip()

            if section_pattern.match(line):

                merged = line

                j = i + 1

                while (
                    j < len(raw_lines)
                    and raw_lines[j].strip()
                    and not section_pattern.match(
                        raw_lines[j].strip()
                    )
                    and len(
                        raw_lines[j].strip()
                    ) < 40
                    and raw_lines[j].strip().isupper()
                ):

                    merged += (
                        " "
                        + raw_lines[j].strip()
                    )

                    j += 1

                lines.append(merged)

                i = j

            else:

                lines.append(line)

                i += 1

        # ----------------------------------
        # Build chunks
        # ----------------------------------

        current_section = None

        current_text = []

        for line in lines:

            line = line.strip()

            if section_pattern.match(line):

                if current_section:

                    chunk_text = "\n".join(
                        current_text
                    )

                    if len(
                        chunk_text.strip()
                    ) >= 50:

                        subchunks = (
                            split_into_subchunks(
                                chunk_text
                            )
                        )

                        for idx, subchunk in enumerate(
                            subchunks,
                            start=1
                        ):

                            chunks.append(
                                {
                                    "subject":
                                        subject_folder.name,
                                    "chapter_file":
                                        txt_file.stem,
                                    "section":
                                        current_section,
                                    "chunk_id":
                                        idx,
                                    "text":
                                       current_section
                                        + "\n\n"
                                        + subchunk
                                }
                            )

                current_section = line

                current_text = []

            else:

                current_text.append(line)

        # ----------------------------------
        # Last section
        # ----------------------------------

        if current_section:

            chunk_text = "\n".join(
                current_text
            )

            if len(
                chunk_text.strip()
            ) >= 50:

                subchunks = (
                    split_into_subchunks(
                        chunk_text
                    )
                )

                for idx, subchunk in enumerate(
                    subchunks,
                    start=1
                ):

                    chunks.append(
                        {
                            "subject":
                                subject_folder.name,
                            "chapter_file":
                                txt_file.stem,
                            "section":
                                current_section,
                            "chunk_id":
                                idx,
                            "text":
                                current_section
                                + "\n\n"
                                + subchunk
                        }
                    )

    output_file = (
        output_root
        / f"{subject_folder.name}_chunks.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Created {len(chunks)} chunks "
        f"for {subject_folder.name}"
    )

print("Chunking complete.")

