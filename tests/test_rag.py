from rag.pipeline import RAGPipeline


rag = RAGPipeline(
    "documents"
)

results = rag.search(
    "What is the minimum password length?",
    k=3
)

for result in results:
    print("\n--- RESULT ---")
    print("Source:", result["source"])
    print("Page:", result["page"])
    print("Score:", result["score"])
    print(result["text"])