from nltk.tokenize import sent_tokenize

def chunk_text(
    text: str,
    max_tokens: int = 800,
    overlap: int = 100
) -> list[str]:
    sentences = sent_tokenize(text)
    
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) > max_tokens:
            chunks.append(current.strip())
            current = current[-overlap:] + " " + sentence
        else:
            current += " " + sentence

    if current:
        chunks.append(current.strip())

    return chunks
