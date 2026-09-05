import os
from dotenv import load_dotenv
from openai import OpenAI
from app.rag import retrieve_context

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def get_ai_reply(user_message: str) -> str:
    context = retrieve_context(user_message)

    system_prompt = (
        "You are StudyMate, a study tutor who explains concepts FAST and SIMPLE.\n"
        "STRICT RULES:\n"
        "- Maximum 4-5 sentences OR 3-4 short bullet points. Never more.\n"
        "- No headers, no markdown titles, no multi-section breakdowns unless the user explicitly asks for 'detailed' or 'full explanation'.\n"
        "- Explain like you're texting a friend before an exam — quick and clear, not a textbook chapter.\n"
        "- Use your own words. Never copy sentences from the notes.\n"
        "- If no relevant notes are found, say \"Not in your notes, but here's a quick explanation:\" then answer briefly.\n"
        "- Never refuse to answer."
    )

    user_prompt = (
        f"NOTES CONTEXT:\n{context}\n\nQUESTION: {user_message}"
        if context else
        f"QUESTION: {user_message}"
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=220,       # hard cap — forces brevity
        temperature=0.4
    )
    return response.choices[0].message.content

def get_answer(question):
    context = retrieve_context(question)

    system_prompt = """You are a study tutor.
- If context is provided, explain it in your own words, briefly and clearly — never copy text verbatim.
- If no context is given or it's unrelated, say "This isn't in your notes, but here's a general explanation:" then answer from your own knowledge.
- Never refuse to answer."""

    user_prompt = f"Context:\n{context}\n\nQuestion: {question}" if context else f"Question: {question}"

    # your existing LLM call here, using system_prompt + user_prompt
    ...