import os
import time
from app.rag import embedder
from fastapi import FastAPI, Request, UploadFile, File
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

os.makedirs("./uploads", exist_ok=True)

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

    # Save file to disk so index_pdf can read it
    save_path = f"./uploads/{file.filename}"
    with open(save_path, "wb") as f:
        f.write(pdf_bytes)

    # Extract text (still used for optional raw storage/reference)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    save_document(file.filename, extracted_text)

    # Index into vector DB for RAG retrieval
    num_chunks = index_pdf(save_path, doc_id=file.filename)

    return {"message": f"'{file.filename}' uploaded successfully.", "chunks": num_chunks}

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

