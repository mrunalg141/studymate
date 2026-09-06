import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
import time
import chromadb
from pypdf import PdfReader
from fastembed import TextEmbedding

embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

print("DEBUG - warming up embedder...")
_warmup_start = time.time()
dummy_chunks = ["This is a sample sentence used only to warm up the embedding model."] * 10
list(embedder.embed(dummy_chunks))
print(f"DEBUG - embedder warmup took {time.time() - _warmup_start:.2f}s")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("studymate_docs")

def extract_pdf_text(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text, chunk_size=250, overlap=20):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+chunk_size]))
        i += chunk_size - overlap
    return chunks

def index_pdf(path, doc_id):
    start = time.time()
    text = extract_pdf_text(path)
    print(f"DEBUG - extraction took {time.time() - start:.2f}s")

    t2 = time.time()
    chunks = chunk_text(text)
    print(f"DEBUG - created {len(chunks)} chunks in {time.time() - t2:.2f}s")

    t3 = time.time()
    embeddings = [e.tolist() for e in embedder.embed(chunks)]
    print(f"DEBUG - embedding took {time.time() - t3:.2f}s")

    t4 = time.time()
    collection.add(
        ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"doc_id": doc_id} for _ in chunks]
    )
    print(f"DEBUG - chroma add took {time.time() - t4:.2f}s")
    return len(chunks)

def retrieve_context(question, top_k=3, threshold=1.8):
    q_embedding = list(embedder.embed([question]))[0].tolist()
    results = collection.query(query_embeddings=[q_embedding], n_results=top_k)

    print("DEBUG - documents found:", len(results["documents"][0]))
    print("DEBUG - distances:", results["distances"][0])

    if not results["documents"][0]:
        return ""
    distances = results["distances"][0]
    if min(distances) > threshold:
        print(f"DEBUG - REJECTED: min distance {min(distances)} > threshold {threshold}")
        return ""
    return "\n\n".join(results["documents"][0])

def clear_collection():
    global collection
    chroma_client.delete_collection("studymate_docs")
    collection = chroma_client.get_or_create_collection("studymate_docs")
