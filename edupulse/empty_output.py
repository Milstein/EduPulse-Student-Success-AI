"""Guarantee the root agent never ends a turn with a blank final response.

Gemini flash-lite models intermittently finish a turn with an empty text part
after an agent-as-tool (sub-agent) returns. In the ADK web UI (SSE streaming)
this surfaces as a blank assistant message, because the framework deliberately
does not turn empty content into an error in SSE mode.

This module wires an ``after_model_callback`` on the root agent. The SSE
aggregator always emits a final chunk with ``partial=False`` that carries the
full accumulated text, so an empty final chunk reliably identifies the blank
case. The callback replaces that chunk with the last sub-agent answer (or a
generic fallback message) before it is yielded and saved, so the UI shows a
single, non-empty assistant message.
"""

import logging

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types

logger = logging.getLogger(__name__)

_FALLBACK_MESSAGE = (
    "I wasn't able to generate a complete answer. "
    "Could you please rephrase your question or try again?"
)


def _parts_text(content) -> str:
    if content is None or not content.parts:
        return ""
    return "".join(part.text for part in content.parts if part.text)


def _sub_agent_answer_from_parts(content) -> str:
    """Extract the sub-agent's answer text from an AgentTool response."""
    if content is None or not content.parts:
        return ""
    for part in content.parts:
        if not part.function_response:
            continue
        response = part.function_response.response or {}
        if isinstance(response, dict):
            result = response.get("result") or response.get("response")
            if isinstance(result, str) and result.strip():
                return result.strip()
    return ""


def _last_sub_agent_answer(session) -> str:
    events = getattr(session, "events", None) or []
    for event in reversed(events):
        if event.author == "user":
            continue
        answer = _sub_agent_answer_from_parts(event.content)
        if answer:
            return answer
        if event.author == "root":
            continue
        text = _parts_text(event.content).strip()
        if text:
            return text
    return ""


async def ensure_non_empty_response(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """Replace an empty final LLM response with a fallback.

    Args:
        callback_context: The callback context for the model call.
        llm_response: The LLM response chunk to inspect.

    Returns:
        An altered ``LlmResponse`` with fallback content when the final chunk
        is empty, otherwise ``None``.
    """
    if llm_response.partial:
        return None

    content = llm_response.content
    if _parts_text(content).strip():
        return None

    has_function_parts = content is not None and content.parts and any(
        part.function_call or part.function_response for part in content.parts
    )
    if has_function_parts:
        return None

    answer = _last_sub_agent_answer(callback_context.session)
    text = answer or _FALLBACK_MESSAGE
    logger.warning(
        "Agent '%s' returned an empty final LLM response; surfacing a fallback",
        callback_context.agent_name,
    )
    return LlmResponse(
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=text)]
        ),
        finish_reason=llm_response.finish_reason,
        partial=llm_response.partial,
        turn_complete=llm_response.turn_complete,
    )
