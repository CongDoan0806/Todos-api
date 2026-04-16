from openai import OpenAI
from app.core.config import settings
from .vector_store import search_todos
from .prompt import build_system_prompt
from .schemas import SuggestedAction
import json

openai_client = OpenAI(api_key=settings.openai_api_key)


def build_context(results: dict) -> str:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return "User chưa có công việc nào."

    return "\n".join([
        f"Todo:\n- {doc}\n- Status: {'Completed' if meta.get('is_completed') else 'Pending'}. Column: {meta.get('col')}. Priority: {meta.get('priority')}. Tag: {meta.get('tag')}"
        for doc, meta in zip(documents, metadatas)
    ])


def chat_with_ai(user_id: int, message: str) -> dict:
    relevant_todos = search_todos(user_id, message)
    context = build_context(relevant_todos)
    system_prompt = build_system_prompt(context)

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )

    raw = json.loads(response.choices[0].message.content)
    suggested = None
    if "suggested_action" in raw and raw["suggested_action"]:
        suggested = SuggestedAction(**raw["suggested_action"])

    return {"answer": raw.get("answer", ""), "suggested_action": suggested}