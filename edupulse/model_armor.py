"""Google Model Armor integration for EduPulse agents.

Provides before_model_callback and after_model_callback functions
that sanitize user prompts and LLM responses via the Model Armor API.

Usage in agent definitions:
    from edupulse.model_armor import create_model_armor_guard

    guard = create_model_armor_guard()
    agent = LlmAgent(
        ...,
        before_model_callback=guard.before_model_callback,
        after_model_callback=guard.after_model_callback,
    )
"""

import logging
import os
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

logger = logging.getLogger(__name__)

_BLOCKED_INPUT_MESSAGE = (
    "I apologize, but I cannot process this request. "
    "Your message was flagged by our security filters. "
    "Please rephrase your question and try again."
)

_BLOCKED_OUTPUT_MESSAGE = (
    "I apologize, but my response was filtered for security reasons. Could you please rephrase your question?"
)


class ModelArmorGuard:
    """Sanitizes LLM prompts and responses using Google Model Armor."""

    def __init__(
        self,
        project_id: str,
        location_id: str,
        template_id: str,
        block_on_match: bool = True,
    ) -> None:
        from google.cloud import modelarmor_v1

        self._project_id = project_id
        self._location_id = location_id
        self._template_id = template_id
        self._block_on_match = block_on_match
        self._template_name = f"projects/{project_id}/locations/{location_id}/templates/{template_id}"

        self._client = modelarmor_v1.ModelArmorClient(
            client_options=ClientOptions(api_endpoint=f"modelarmor.{location_id}.rep.googleapis.com"),
        )
        logger.info(
            "Model Armor guard initialized for template %s in %s",
            template_id,
            location_id,
        )

    def _sanitize_user_prompt(self, text: str):
        from google.cloud import modelarmor_v1

        request = modelarmor_v1.SanitizeUserPromptRequest(
            name=self._template_name,
            user_prompt_data=modelarmor_v1.DataItem(text=text),
        )
        return self._client.sanitize_user_prompt(request=request)

    def _sanitize_model_response(self, text: str):
        from google.cloud import modelarmor_v1

        request = modelarmor_v1.SanitizeModelResponseRequest(
            name=self._template_name,
            model_response_data=modelarmor_v1.DataItem(text=text),
        )
        return self._client.sanitize_model_response(request=request)

    def _has_match(self, response) -> bool:
        result = response.sanitization_result
        if not result:
            return False
        return result.filter_match_state == 2

    def _extract_user_text(self, llm_request: LlmRequest) -> Optional[str]:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts:
                texts = [part.text for part in content.parts if part.text]
                if texts:
                    return "\n".join(texts).strip() or None
        return None

    def _extract_model_text(self, llm_response: LlmResponse) -> Optional[str]:
        if not llm_response.content or not llm_response.content.parts:
            return None
        texts = [part.text for part in llm_response.content.parts if part.text]
        return "\n".join(texts).strip() or None

    async def before_model_callback(
        self,
        callback_context: CallbackContext,
        llm_request: LlmRequest,
    ) -> Optional[LlmResponse]:
        user_text = self._extract_user_text(llm_request)
        if not user_text:
            return None

        try:
            response = self._sanitize_user_prompt(user_text)
            if self._has_match(response) and self._block_on_match:
                logger.warning("Model Armor blocked user prompt")
                return LlmResponse(
                    content=types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=_BLOCKED_INPUT_MESSAGE)],
                    )
                )
        except Exception as e:
            logger.error("Model Armor input scan failed (fail-open): %s", e)

        return None

    async def after_model_callback(
        self,
        callback_context: CallbackContext,
        llm_response: LlmResponse,
    ) -> Optional[LlmResponse]:
        model_text = self._extract_model_text(llm_response)
        if not model_text:
            return None

        try:
            response = self._sanitize_model_response(model_text)
            if self._has_match(response) and self._block_on_match:
                logger.warning("Model Armor blocked model response")
                return LlmResponse(
                    content=types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=_BLOCKED_OUTPUT_MESSAGE)],
                    )
                )
        except Exception as e:
            logger.error("Model Armor output scan failed (fail-open): %s", e)

        return None


def create_model_armor_guard() -> Optional[ModelArmorGuard]:
    """Create a ModelArmorGuard from environment variables.

    Returns None if Model Armor is not configured, allowing agents
    to function without security filtering.
    """
    project_id = os.environ.get("MODEL_ARMOR_PROJECT_ID") or os.environ.get("PROJECT_ID", "")
    location_id = os.environ.get("MODEL_ARMOR_LOCATION", "us-east1")
    template_id = os.environ.get("MODEL_ARMOR_TEMPLATE_ID", "")

    if not project_id or not template_id:
        logger.warning(
            "Model Armor not configured (missing MODEL_ARMOR_PROJECT_ID or MODEL_ARMOR_TEMPLATE_ID). "
            "Agent will run without LLM security filtering."
        )
        return None

    return ModelArmorGuard(
        project_id=project_id,
        location_id=location_id,
        template_id=template_id,
    )
