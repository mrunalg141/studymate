# StudyMate

StudyMate is a document Q&A assistant that answers questions grounded in your own notes.

Upload a PDF, ask a question in plain English, and get an answer retrieved from that specific document — not from generic model knowledge.

> Built to understand how Retrieval-Augmented Generation (RAG) actually works under the hood, rather than just calling a library.

## Features

- Upload PDF notes via drag-and-drop or file picker
- Ask questions and get answers grounded in the uploaded document
- Real retrieval-based RAG — chunking, embeddings, and semantic search, not "stuff the whole document into the prompt"
- Honest fallback — the assistant says "I don't know" when the answer isn't in the notes, instead of guessing
- Persistent chat history (SQLite) — conversations reload on every visit
- One-click chat/document reset
- Custom-built chat UI (no frontend framework)

## Tech Stack

| Layer | Tools |
|---|---|
| **Backend** | Python, FastAPI |
| **Frontend** | HTML, CSS, JavaScript (vanilla) |
| **LLM** | Groq API (OpenAI-compatible) |
| **Embeddings** | fastembed (BAAI/bge-small-en-v1.5) |
| **Vector Store** | ChromaDB |
| **Chat History** | SQLite |
| **Templating** | Jinja2 |

## How It Works

### 1. Upload

A PDF is uploaded and its text is extracted using `pypdf`.

### 2. Chunk

The extracted text is split into overlapping word-based chunks.

- Approximately 250–500 words per chunk
- Overlapping chunks
- Chunk size tuned through testing

### 3. Embed

Each chunk is converted into a vector embedding using `fastembed` with:

```text
BAAI/bge-small-en-v1.5
````

The generated embeddings are stored in ChromaDB.

### 4. Ask

When a user asks a question, the question is embedded using the same embedding model.

ChromaDB then searches for the most semantically similar chunks from the stored document data.

### 5. Filter

A relevance-distance threshold is used to reject weak matches.

This prevents unrelated questions from retrieving irrelevant context.

### 6. Answer

The retrieved chunks, if any, are passed to the LLM through the Groq API as grounding context.

The model is instructed to answer only from the provided context.

If the answer is not present in the retrieved context, the assistant responds with:

```text
I don't know
```

instead of guessing.

## Project Structure

```text
StudyMate/
├── app/
│   ├── main.py          # FastAPI app, routes
│   ├── llm.py           # LLM (Groq) integration and prompt logic
│   ├── rag.py           # Chunking, embeddings, vector store, retrieval
│   └── database.py      # SQLite chat history
│
├── templates/
│   └── index.html        # Chat UI
│
├── static/
│   ├── style.css
│   └── script.js
│
├── requirements.txt
└── .gitignore
```

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd StudyMate
```

### 2. Create and Activate a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Your API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at:

[https://console.groq.com](https://console.groq.com)

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

## Known Limitations / Roadmap

### Current Limitations

* Retrieval currently searches across all uploaded documents together — per-document scoping is planned
* No formal evaluation metrics for retrieval quality yet — currently judged manually
* Deployment is currently local-only

### Planned Improvements

* Refactor into LangChain
* Add a LangGraph decision step
* Let the system decide when retrieval is actually needed instead of running it on every query
* Add per-document retrieval scoping
* Add deployment support

## License
This project is licensed under the MIT License.
