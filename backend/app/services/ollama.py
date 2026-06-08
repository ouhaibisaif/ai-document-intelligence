import httpx

from app.core.config import get_settings
from app.prompts.system import DOCUMENT_ASSISTANT_PROMPT


class OllamaClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def summarize(self, text: str) -> str:
        context = text[:8000]
        prompt = (
            "Write a short, factual summary of this document in 4 to 6 sentences. "
            "Use only the document text.\n\n"
            f"{context}"
        )
        return await self._chat(
            [
                {"role": "system", "content": DOCUMENT_ASSISTANT_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )

    async def answer(self, question: str, context: str) -> str:
        user_prompt = (
            f"Document context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer from the context only."
        )
        return await self._chat(
            [
                {"role": "system", "content": DOCUMENT_ASSISTANT_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
        )

    async def _chat(self, messages: list[dict[str, str]]) -> str:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1},
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip()
