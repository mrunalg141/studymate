# StudyMate

An AI-powered PDF Q&A assistant. Upload a PDF, ask questions, and get answers grounded strictly in the document's content using Retrieval-Augmented Generation (RAG).

## Features

- Upload a PDF and ask questions about its content
- Answers are grounded only in the document — no hallucinated info outside its context
- Fast inference via the Groq API (OpenAI-compatible)
- Semantic search over document chunks using vector embeddings
- Persistent chat history (SQLite)

## Tech Stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript (vanilla) |
| LLM | Groq API (OpenAI-compatible) |
| Embeddings | fastembed (BAAI/bge-small-en-v1.5) |
| Vector store | ChromaDB |
| Chat history | SQLite |
| Templating | Jinja2 |

## How It Works

1. **Upload** — a PDF is uploaded and its text extracted (`pypdf`)
2. **Chunk** — the text is split into overlapping word-based chunks (~250–500 words, tuned by testing)
3. **Embed** — each chunk is converted into a vector embedding via `fastembed` and stored in ChromaDB
4. **Ask** — a user question is embedded the same way, and ChromaDB returns the most similar chunks
5. **Filter** — a relevance-distance threshold rejects weak matches, so unrelated questions don't pull in irrelevant context
6. **Answer** — the retrieved chunks (if any) are passed to the LLM (Groq) as grounding context; the model is instructed to answer only from that context

## Project Structure

```
StudyMate/
├── app/
│   ├── main.py
│   ├── llm.py
│   ├── rag.py
│   └── database.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
└── .gitignore
```

## Prerequisites

- Python 3.9+
- A [Groq API key](https://console.groq.com)

## Setup

1. **Clone the repo**
   ```bash
   git clone <your-repo-url>
   cd StudyMate
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Groq API key** — create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

5. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Open in your browser**
   ```
   http://127.0.0.1:8000
   ```

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used to authenticate requests to the Groq LLM |

## Usage

1. Open the app in your browser
2. Upload a PDF file
3. Wait for it to be processed (extracted, chunked, and embedded)
4. Ask questions about the document in the chat box
5. Your conversation is saved automatically for the session

## Contributing

Contributions are welcome. Please open an issue to discuss what you'd like to change, then submit a pull request.

## License

Add your license here (e.g. MIT).
