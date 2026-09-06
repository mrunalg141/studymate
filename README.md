StudyMate

StudyMate is a document Q&A assistant that answers questions grounded in your own notes. 
Upload a PDF, ask a question in plain English, and get an answer retrieved from that specific document — not from generic model knowledge.

Built to understand how Retrieval-Augmented Generation (RAG) actually works under the hood, rather than just calling a library.

Features
📄 Upload PDF notes via drag-and-drop or file picker
💬 Ask questions and get answers grounded in the uploaded document
🔍 Real retrieval-based RAG — chunking, embeddings, and semantic search, not "stuff the whole document into the prompt"
🚫 Honest fallback — the assistant says "I don't know" when the answer isn't in the notes, instead of guessing
🗂️ Persistent chat history (SQLite) — conversations reload on every visit
🧹 One-click chat/document reset
🎨 Custom-built chat UI (no frontend framework)

Tech Stack
Layer	Tools
Backend	Python, FastAPI
Frontend	HTML, CSS, JavaScript (vanilla)
LLM	Groq API (OpenAI-compatible)
Embeddings	fastembed (BAAI/bge-small-en-v1.5)
Vector store	ChromaDB
Chat history	SQLite
Templating	Jinja2
How It Works
Upload — a PDF is uploaded and its text extracted (pypdf)
Chunk — the text is split into overlapping word-based chunks (~250-500 words, tuned by testing)
Embed — each chunk is converted into a vector embedding via fastembed and stored in ChromaDB
Ask — a user question is embedded the same way, and ChromaDB returns the most similar chunks
Filter — a relevance-distance threshold rejects weak matches, so unrelated questions don't pull in irrelevant context
Answer — the retrieved chunks (if any) are passed to the LLM (Groq) as grounding context; the model is instructed to answer only from that context
Project Structure
StudyMate/
├── app/
│   ├── main.py         # FastAPI app, routes
│   ├── llm.py           # LLM (Groq) integration and prompt logic
│   ├── rag.py            # Chunking, embeddings, vector store, retrieval
│   └── database.py       # SQLite chat history
├── templates/
│   └── index.html        # Chat UI
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
└── .gitignore
Setup

1. Clone the repo

bash
git clone <your-repo-url>
cd StudyMate

2. Create and activate a virtual environment

Windows:

bash
python -m venv venv
venv\Scripts\activate

Mac/Linux:

bash
python3 -m venv venv
source venv/bin/activate

3. Install dependencies

bash
pip install -r requirements.txt

4. Add your API key

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here

Get a free key at console.groq.com.

5. Run the server

bash
uvicorn app.main:app --reload

Open http://127.0.0.1:8000 in your browser.

Known Limitations / Roadmap
Retrieval currently searches across all uploaded documents together — per-document scoping is planned
No formal evaluation metrics for retrieval quality yet (currently judged manually)
Planning to refactor into LangChain and add a LangGraph decision step, so the system decides when retrieval is actually needed instead of running it on every query
Deployment (currently local-only) is a next step
License

MIT
