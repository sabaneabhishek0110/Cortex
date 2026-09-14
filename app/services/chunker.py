#chunker.py
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain.docstore.document import Document

def chunk_text(text: str, source_name="document.pdf",
               chunk_size=800, chunk_overlap=200,
               encoding_name="gpt2") -> list[str]:

    # Normalize newlines and clean whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    # Attempt token-based splitting first
    try:
        token_splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            encoding_name=encoding_name
        )
        chunks = token_splitter.split_text(text)
    except Exception as e:
        print(f"[TokenTextSplitter failed with error: {e}] Falling back to RecursiveCharacterTextSplitter.")
        char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 2,  # allow bigger chunks for char splitter
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = char_splitter.split_text(text)

    # Add metadata with source and chunk number
    enhanced_chunks = [
        f"(Source: {source_name}, Chunk {i+1})\n\n{chunk.strip()}"
        for i, chunk in enumerate(chunks)
        if chunk.strip()
    ]

    return enhanced_chunks