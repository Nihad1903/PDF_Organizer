import re
from PyPDF2 import PdfWriter, PdfReader
from typing import List
from io import BytesIO

def parse_page_ranges(pages_str: str, total_pages: int) -> List[int]:
    if not pages_str.strip():
        raise ValueError("Page range cannot be empty")

    page_numbers = set()
    parts = [p.strip() for p in pages_str.split(',')]

    for part in parts:
        if not part:
            continue

        part = part.replace('end', str(total_pages))

        match = re.match(r'^(\d+)(?:-(\d+))?$', part)
        if not match:
            raise ValueError(f"Invalid page range format: {part}")

        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start

        if start < 1 or end > total_pages:
            raise ValueError(f"Page numbers must be between 1 and {total_pages}")
        if start > end:
            raise ValueError(f"Invalid range: {start}-{end}")

        page_numbers.update(range(start - 1, end))

    return sorted(list(page_numbers))

def split_pdf(pdf_file, page_numbers: List[int]) -> BytesIO:
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    for page_num in page_numbers:
        if page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])

    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer
