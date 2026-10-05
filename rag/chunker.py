def create_chunks(
    pages,
    chunk_size: int = 500,
    overlap: int = 100
):

    chunks = []

    for page in pages:

        text = page["text"]
        page_number = page["page"]
        source = page["source"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            if chunk.strip():

                chunks.append({
                    "text": chunk,
                    "page": page_number,
                    "source": source
                })

            start += chunk_size - overlap

    return chunks