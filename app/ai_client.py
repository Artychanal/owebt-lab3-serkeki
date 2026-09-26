import asyncio

from google import genai


class AIServiceError(RuntimeError):
    """A user-safe error raised when Gemini cannot return an answer."""


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def ask(self, prompt: str) -> str:
        try:
            async with asyncio.timeout(45):
                response = await self._client.aio.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config={
                        "system_instruction": (
                            "Відповідай зрозуміло та доброзичливо. "
                            "Використовуй мову запиту користувача."
                        ),
                        "max_output_tokens": 1200,
                    },
                )
        except TimeoutError as error:
            raise AIServiceError("AI не встиг відповісти. Спробуйте ще раз.") from error
        except Exception as error:
            raise AIServiceError(
                "Не вдалося отримати відповідь від AI. Спробуйте пізніше."
            ) from error

        answer = (response.text or "").strip()
        if not answer:
            raise AIServiceError("AI не повернув текстову відповідь.")
        return answer

