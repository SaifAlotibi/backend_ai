import hashlib
import json
import os
from pathlib import Path

from .loader import load_pdf
from .chunker import create_chunks
from .embeddings import create_embeddings
from .vector_store import (
    create_index,
    save_index,
    load_index
)
from .retriever import retrieve


def get_documents_hash(
    documents_path: str
) -> str:

    sha256 = hashlib.sha256()

    pdf_files = sorted(
        Path(documents_path).glob("*.pdf")
    )

    for pdf_path in pdf_files:

        sha256.update(
            pdf_path.name.encode("utf-8")
        )

        with open(
            pdf_path,
            "rb"
        ) as file:

            for chunk in iter(
                lambda: file.read(8192),
                b""
            ):
                sha256.update(chunk)

    return sha256.hexdigest()


class RAGPipeline:

    def __init__(
        self,
        documents_path: str,
        index_path: str = "rag_store/index.faiss",
        chunks_path: str = "rag_store/chunks.json",
        metadata_path: str = "rag_store/metadata.json"
    ):

        self.documents_path = documents_path
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.metadata_path = metadata_path

        os.makedirs(
            os.path.dirname(self.index_path),
            exist_ok=True
        )

        pdf_files = sorted(
            Path(documents_path).glob("*.pdf")
        )

        if not pdf_files:
            raise ValueError(
                "No PDF documents found."
            )

        current_hash = get_documents_hash(
            documents_path
        )

        # -----------------------------------------
        # Load existing index
        # -----------------------------------------

        if (
            os.path.exists(self.index_path)
            and os.path.exists(self.chunks_path)
            and os.path.exists(self.metadata_path)
        ):

            with open(
                self.metadata_path,
                "r",
                encoding="utf-8"
            ) as file:

                metadata = json.load(file)

            saved_hash = metadata.get(
                "documents_hash"
            )

            if saved_hash == current_hash:

                print(
                    "Loading existing RAG index..."
                )

                self.index = load_index(
                    self.index_path
                )

                with open(
                    self.chunks_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    self.chunks = json.load(file)

                return

        # -----------------------------------------
        # Build new index
        # -----------------------------------------

        print(
            "Building RAG index from documents..."
        )

        all_pages = []

        for pdf_path in pdf_files:

            print(
                f"Loading: {pdf_path.name}"
            )

            pages = load_pdf(
                str(pdf_path)
            )

            all_pages.extend(
                pages
            )

        self.chunks = create_chunks(
            all_pages
        )

        if not self.chunks:
            raise ValueError(
                "No text chunks were created."
            )

        # -----------------------------------------
        # Create embeddings
        # -----------------------------------------

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        embeddings = create_embeddings(
            texts
        )

        # -----------------------------------------
        # Create FAISS index
        # -----------------------------------------

        self.index = create_index(
            embeddings
        )

        # -----------------------------------------
        # Save index
        # -----------------------------------------

        save_index(
            self.index,
            self.index_path
        )

        # -----------------------------------------
        # Save chunks
        # -----------------------------------------

        with open(
            self.chunks_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.chunks,
                file,
                ensure_ascii=False,
                indent=2
            )

        # -----------------------------------------
        # Save metadata
        # -----------------------------------------

        with open(
            self.metadata_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {
                    "documents_hash": current_hash,
                    "documents": [
                        pdf.name
                        for pdf in pdf_files
                    ]
                },
                file,
                indent=2
            )

    def search(
        self,
        query: str,
        k: int = 3,
        min_similarity: float = 0.4
    ):

        return retrieve(
            query=query,
            index=self.index,
            chunks=self.chunks,
            k=k,
            min_similarity=min_similarity
        )