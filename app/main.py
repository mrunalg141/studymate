import os
import time
import uuid
from pathlib import Path
from app.rag import embedder
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pypdf import PdfReader
import io
from app.rag import index_pdf, clear_collection

from app.rag import index_pdf
from app.llm import get_ai_reply
from app.database import (
    init_db, save_message, get_all_messages,
    init_documents_table, save_document, get_latest_document,
    clear_messages
)

app = FastAPI(title="StudyMate")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()
init_documents_table()

UPLOAD_DIR = Path("./uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ChatMessage(BaseModel):
    message: str

@app.get("/test-embed")
def test_embed():
    texts = ["This is a test sentence about machine learning."] * 8
    t0 = time.time()
    embeddings = list(embedder.embed(texts))
    elapsed = time.time() - t0
    return {"elapsed_seconds": elapsed}

@app.get("/")
def read_root(request: Request):
    messages = get_all_messages()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"messages": messages}
    )

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    original_filename = file.filename or "uploaded.pdf"

    # Save file using a server-side safe and unique filename
    safe_filename = f"{uuid.uuid4().hex}.pdf"
    save_path = (UPLOAD_DIR / safe_filename).resolve()

    if not save_path.is_relative_to(UPLOAD_DIR):
        raise HTTPException(status_code=400, detail="Invalid file destination path.")

    with open(save_path, "wb") as f:
        f.write(pdf_bytes)

    # Extract text (still used for optional raw storage/reference)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    save_document(original_filename, extracted_text)

    # Index into vector DB for RAG retrieval
    num_chunks = index_pdf(str(save_path), doc_id=original_filename)

    return {"message": f"'{original_filename}' uploaded successfully.", "chunks": num_chunks}

@app.post("/chat")
def chat(chat_message: ChatMessage):
    bot_reply = get_ai_reply(chat_message.message)
    save_message(chat_message.message, bot_reply)
    return {"reply": bot_reply}


@app.post("/clear")
def clear_chat():
    clear_messages()
    clear_collection()
    return {"message": "Chat history and uploaded documents cleared."}

