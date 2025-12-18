import json
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from config import (
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    PROMPTS_DIR,
    DEFAULT_NUM_MCQ,
    DEFAULT_NUM_FREEFORM,
)

try:
    from openai import OpenAI
    from openai import APIConnectionError, APIError, AuthenticationError, RateLimitError
    from openai.types.chat import ChatCompletionSystemMessageParam
except Exception:
    OpenAI = None
    APIConnectionError = APIError = AuthenticationError = RateLimitError = Exception
    ChatCompletionSystemMessageParam = dict  # type: ignore[misc,assignment]

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
except Exception:
    Environment = FileSystemLoader = None
    TemplateNotFound = Exception

load_dotenv()


def _render_template(template_name: str, **kwargs) -> str:
    """Render a Jinja2 prompt template to a string.

    Parameters:
    - template_name: File name of the template in the prompts directory.
    - **kwargs: Variables available to the template during rendering.

    Returns:
    - The rendered template string.

    Raises:
    - RuntimeError: If Jinja2 is not installed or the template cannot be found.
    """
    if Environment is None or FileSystemLoader is None:
        raise RuntimeError("Jinja2 is not installed.")
    env = Environment(
        loader=FileSystemLoader(PROMPTS_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    try:
        template = env.get_template(template_name)
        return template.render(**kwargs)
    except TemplateNotFound as e:
        raise RuntimeError(f"Prompt template not found: {e}")


def _handle_api_errors(func):
    """Decorator that converts OpenAI SDK exceptions into error dicts.

    The wrapped function is expected to return a Dict[str, Any] on success.
    """

    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        """Call func and normalize known exceptions into a uniform error mapping.

        Returns a dict containing either the successful payload or an "error" key
        with standardized {type, message} fields.
        """
        try:
            return func(*args, **kwargs)
        except AuthenticationError as e:
            return {"error": {"type": "AuthenticationError", "message": str(e)}}
        except RateLimitError as e:
            return {"error": {"type": "RateLimitError", "message": str(e)}}
        except APIConnectionError as e:
            return {"error": {"type": "APIConnectionError", "message": str(e)}}
        except APIError as e:
            return {"error": {"type": "APIError", "message": str(e)}}
        except Exception as e:
            return {"error": {"type": type(e).__name__, "message": str(e)}}

    return wrapper


def _parse_json_response(content: str) -> Dict[str, Any]:
    """Parse model JSON response content into a Python dict.

    Returns an error mapping with the raw content if decoding fails.
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError as je:
        return {
            "error": {
                "type": "JSONDecodeError",
                "message": f"Failed to parse model output as JSON: {je}",
            },
            "raw": content,
        }


# === LLM Client ===
class LLMClient:
    """Thin wrapper around the OpenAI Chat Completions API.

    This client assembles prompts from templates and requests structured JSON
    responses from the model. It also normalizes SDK exceptions into a simple
    {"error": {"type", "message"}} mapping so the caller doesn't have to
    catch network or quota errors.
    """

    def __init__(
            self, api_key: Optional[str] = None, model: Optional[str] = None
    ) -> None:
        """Create a client with the provided credentials and model name.

        Parameters:
        - api_key: OpenAI API key. If omitted, uses config.OPENAI_API_KEY.
        - model: Model identifier to use. If omitted, uses config.DEFAULT_MODEL.
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or DEFAULT_MODEL
        self._client = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None

    def _ensure_client(self) -> Optional[Dict[str, Any]]:
        """Ensure the underlying OpenAI client is initialized.

        Returns:
        - None if ready.
        - An error dict if the API key or SDK dependency is missing.
        """
        if not self.api_key:
            return {
                "error": {
                    "type": "MissingAPIKey",
                    "message": "OPENAI_API_KEY is not set in environment.",
                }
            }
        if OpenAI is None:
            return {
                "error": {
                    "type": "MissingDependency",
                    "message": "OpenAI SDK is not installed.",
                }
            }
        if not self._client:
            self._client = OpenAI(api_key=self.api_key)
        return None

    @_handle_api_errors
    def complete(self, prompt: str) -> Dict[str, Any]:
        """Send a prompt expecting a JSON object response from the model.

        Parameters:
        - prompt: The system message content guiding the model.

        Returns:
        - Parsed JSON response as a dict, or an error mapping if the request
          failed or the response was empty/invalid.
        """
        error = self._ensure_client()
        if error:
            return error

        messages: list[ChatCompletionSystemMessageParam] = [
            {"role": "system", "content": prompt}  # type: ignore[typeddict-item]
        ]
        # noinspection PyTypeChecker
        response = self._client.chat.completions.create(
            model=self.model, messages=messages, response_format={"type": "json_object"}
        )
        content = (
            response.choices[0].message.content
            if response and response.choices
            else None
        )
        if not content:
            return {
                "error": {
                    "type": "EmptyResponse",
                    "message": "No content returned by the model.",
                }
            }
        return _parse_json_response(content)


# === Generate Questions ===
def generate_questions(
        topic: str,
        num_mcq: Optional[int] = None,
        num_freeform: Optional[int] = None,
        client: Optional[LLMClient] = None,
) -> Dict[str, Any]:
    """Ask the LLM to generate a batch of questions for a given topic.

    Parameters:
    - topic: The subject area to generate questions about. Must be non-empty.
    - client: Optional LLMClient; if omitted, a default client is created.

    Returns:
    - On success: a dict that should contain a "questions" list of question dicts.
    - On failure: a dict with an "error" key describing the problem. When the
      model returns invalid JSON, an auxiliary "raw" field may hold the text.
    """
    topic = topic.strip()
    if not topic:
        return {
            "error": {
                "type": "ValueError",
                "message": "Topic must be a non-empty string.",
            }
        }

    client = client or LLMClient()
    # Resolve counts using defaults when not provided
    num_mcq = DEFAULT_NUM_MCQ if num_mcq is None else max(0, int(num_mcq))
    num_freeform = (
        DEFAULT_NUM_FREEFORM if num_freeform is None else max(0, int(num_freeform))
    )

    try:
        prompt = _render_template(
            "generate_questions.j2",
            topic=topic,
            num_mcq=num_mcq,
            num_freeform=num_freeform,
        )
    except Exception as e:
        return {"error": {"type": type(e).__name__, "message": str(e)}}

    return client.complete(prompt)


# === Judge Freeform Question ===
def judge_freeform(
        question: str,
        reference_answer: str,
        user_answer: str,
        client: Optional[LLMClient] = None,
) -> Dict[str, Any]:
    """Ask the LLM to judge a freeform answer against a reference answer.

    Parameters:
    - question: The question prompt shown to the user.
    - reference_answer: The canonical or expected answer used for evaluation.
    - user_answer: The user's freeform response.
    - client: Optional LLMClient; if omitted, a default client is created.

    Returns:
    - On success: a dict with keys {"judgment", "explanation"} where
      judgment is "Correct" or "Incorrect" (capitalization may vary) and
      explanation is a human-readable rationale string (possibly empty).
    - On failure: an error dict with an "error" key.
    """
    client = client or LLMClient()
    try:
        prompt = _render_template(
            "evaluate_questions.j2",
            question=question,
            reference_answer=reference_answer,
            user_answer=user_answer,
        )
    except Exception as e:
        return {"error": {"type": type(e).__name__, "message": str(e)}}

    result = client.complete(prompt)
    if "error" in result:
        return result

    return {
        "judgment": (result.get("judgment") or "").strip(),
        "explanation": (result.get("explanation") or "").strip(),
    }
