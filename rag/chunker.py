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

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n")
            if paragraph.strip()
        ]

        current_chunk = ""

        for paragraph in paragraphs:

            # -----------------------------------------
            # Add paragraph if it fits
            # -----------------------------------------

            if (
                len(current_chunk)
                + len(paragraph)
                + 1
                <= chunk_size
            ):

                current_chunk += (
                    paragraph + " "
                )

                continue

            # -----------------------------------------
            # Save current chunk
            # -----------------------------------------

            if current_chunk.strip():

                chunks.append({
                    "text": current_chunk.strip(),
                    "page": page_number,
                    "source": source
                })

            # -----------------------------------------
            # Start new chunk
            # -----------------------------------------

            if overlap > 0:

                overlap_text = (
                    current_chunk[-overlap:]
                )

                current_chunk = (
                    overlap_text
                    + paragraph
                    + " "
                )

            else:

                current_chunk = (
                    paragraph + " "
                )

        # -----------------------------------------
        # Save final chunk
        # -----------------------------------------

        if current_chunk.strip():

            chunks.append({
                "text": current_chunk.strip(),
                "page": page_number,
                "source": source
            })

    return chunks