import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, local, free
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("studymate_docs")

def extract_pdf_text(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+chunk_size]))
        i += chunk_size - overlap
    return chunks

def index_pdf(path, doc_id):
    text = extract_pdf_text(path)
    chunks = chunk_text(text)
    print(f"DEBUG - extracted {len(text)} chars, created {len(chunks)} chunks")  # ADD THIS
    embeddings = embedder.encode(chunks).tolist()
    collection.add(
        ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"doc_id": doc_id} for _ in chunks]
    )
    return len(chunks)

def retrieve_context(question, top_k=3, threshold=1.8):
    q_embedding = embedder.encode([question]).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=top_k)
    
    print("DEBUG - documents found:", len(results["documents"][0]))          # ADD THIS
    print("DEBUG - distances:", results["distances"][0])                      # ADD THIS
    
    if not results["documents"][0]:
        return ""
    distances = results["distances"][0]
    if min(distances) > threshold:
        print(f"DEBUG - REJECTED: min distance {min(distances)} > threshold {threshold}")  # ADD THIS
        return ""
    return "\n\n".join(results["documents"][0])