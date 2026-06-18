import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


pdf_root = Path("data/pdfs")
output_root = Path("data/text")

output_root.mkdir(
    parents=True,
    exist_ok=True
)

for subject_folder in pdf_root.iterdir():

    if not subject_folder.is_dir():
        continue

    subject_output = (
        output_root /
        subject_folder.name
    )

    subject_output.mkdir(
        parents=True,
        exist_ok=True
    )

    for pdf_file in subject_folder.glob("*.pdf"):

        # Skip answer keys and solutions
        if (
            "answer" in pdf_file.name.lower()
            or
            "solution" in pdf_file.name.lower()
        ):
            continue

        print(
            f"Processing: {pdf_file.name}"
        )

        try:

            text = extract_text_from_pdf(
                pdf_file
            )

            output_file = (
                subject_output /
                f"{pdf_file.stem}.txt"
            )

            output_file.write_text(
                text,
                encoding="utf-8"
            )

            print(
                f"Saved: {output_file.name}"
            )

        except Exception as e:

            print(
                f"Error processing "
                f"{pdf_file.name}: {e}"
            )

print("\nAll PDFs processed.")