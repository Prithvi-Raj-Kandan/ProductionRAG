from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_pages_from_pdf(input_files):
    """
    Returns a list of page-level dicts, preserving text per page.
    """
    all_pages = []
    for file in input_files:
        pdf_name = str(file)
        reader = PdfReader(file)
        for page_index, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                all_pages.append({
                    "pdf_name": pdf_name,
                    "page_no": page_index + 1,
                    "text": text
                })
    return all_pages

def extract_text_from_pages(all_pages: dict):
    """
    Concatenates text from all pages into a single string.
    """
    all_text = " ".join(page["text"] for page in all_pages)
    return all_text


def create_chunks(all_text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = text_splitter.split_text(all_text)
    return chunks