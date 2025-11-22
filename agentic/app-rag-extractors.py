import pdfplumber
import docx
import io

async def extract_text_from_pdf(data: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

async def extract_text_from_docx(data: bytes) -> str:
    f = io.BytesIO(data)
    doc = docx.Document(f)
    return "\n".join([p.text for p in doc.paragraphs])

async def extract_text_from_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")

async def extract_text(data: bytes, filename: str) -> str:
    filename = filename.lower()
    if filename.endswith(".pdf"):
        return await extract_text_from_pdf(data)
    elif filename.endswith(".docx"):
        return await extract_text_from_docx(data)
    else:
        return await extract_text_from_txt(data)
