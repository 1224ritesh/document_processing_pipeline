import fitz  # pymupdf
import io


def split_pdf_by_pages(pdf_bytes: bytes, page_numbers: list[int]) -> bytes:
    
    src = fitz.open(stream=pdf_bytes, filetype="pdf")
    dst = fitz.open()

    for page_num in sorted(page_numbers):
        if 0 <= page_num < len(src):
            dst.insert_pdf(src, from_page=page_num, to_page=page_num)

    buffer = io.BytesIO()
    dst.save(buffer)
    dst.close()
    src.close()

    return buffer.getvalue()


def get_page_count(pdf_bytes: bytes) -> int:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    count = len(doc)
    doc.close()
    return count


def validate_pdf(pdf_bytes: bytes, max_size_mb: int, max_pages: int) -> None:
    size_mb = len(pdf_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"PDF size {size_mb:.1f}MB exceeds limit of {max_size_mb}MB")

    page_count = get_page_count(pdf_bytes)
    if page_count > max_pages:
        raise ValueError(f"PDF has {page_count} pages, exceeds limit of {max_pages}")
    if page_count == 0:
        raise ValueError("PDF has no pages")
