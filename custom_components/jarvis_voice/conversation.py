import logging
import aiohttp
import asyncio
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Начальная инициализация агента при добавлении интеграции."""
    async_add_entities([JarvisConversationAgent(config_entry)])


class JarvisConversationAgent(conversation.ConversationEntity, conversation.AbstractConversationAgent):
    """Официальный локальный диалоговый агент Джарвиса v3.1."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Инициализация сущности."""
        self._config_entry = config_entry
        self._attr_name = "Jarvis v3.1 Engine"
        self._attr_unique_id = f"{config_entry.entry_id}-agent"

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return ["en", "ru"]

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Основной обработчик: забирает текст и пуляет на порт 8090 с динамическим таймаутом."""
        user_text = user_input.text.strip()
        conversation_id = user_input.conversation_id or "jarvis_session"
        language = user_input.language
        
        _LOGGER.info("Jarvis Agent captured voice text: '%s'", user_text)

        # Вытаскиваем таймаут из настроек интеграции (по умолчанию ставим 45 секунд, если пусто)
        custom_timeout = self._config_entry.data.get("timeout", 45)
        _LOGGER.info("Applying dynamic session timeout: %s seconds", custom_timeout)

        # Подставляем реальный локальный IP твоей Orange Pi 5 Pro
        agent_url = "http://192.168.50.175:8090"
        ai_response = "I am ready, Sir."

        payload = {
            "query": user_text,
            "conversation_id": conversation_id,
            "language": language,
            "stream": False
        }

        try:
            # Обертываем всю операцию в asyncio.timeout, чтобы заблокировать внутренний 10с лимит HA Core
            async with asyncio.timeout(custom_timeout):
                timeout_config = aiohttp.ClientTimeout(total=custom_timeout)
                
                async with aiohttp.ClientSession(timeout=timeout_config) as session:
                    async with session.post(agent_url, json=payload) as response:
                        if response.status == 200:
                            res_json = await response.json()
                            ai_response = res_json.get("output", "I am ready, Sir.").strip()
                        else:
                            _LOGGER.error("Jarvis HTTP server returned status %s", response.status)
                            ai_response = "Communication error with Jarvis core, Sir."
                        
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout after %s seconds connecting to Jarvis core on port 8090", custom_timeout)
            ai_response = "Jarvis core is thinking too long, Sir."
        except Exception as e:
            _LOGGER.error("Critical error connecting to Jarvis core: %s", e)
            ai_response = "Jarvis core is offline, Sir."

        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_speech(ai_response)

        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=conversation_id
        )

