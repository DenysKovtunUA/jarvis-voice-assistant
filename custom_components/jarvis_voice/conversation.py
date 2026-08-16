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
        # Жестко фиксируем имя, которое будет отображаться в выпадающем списке Голосового Ассистента
        self._attr_name = "Jarvis v3.1 Engine"
        # Генерируем уникальный ID на основе ID интеграции
        self._attr_unique_id = f"{config_entry.entry_id}-agent"

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Объявляем поддержку всех языков, но Квен заточен под английский контур."""
        return ["en", "ru"]

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Основной обработчик: ловит текст от Whisper и пуляет его на порт 8090."""
        user_text = user_input.text.strip()
        conversation_id = user_input.conversation_id or "jarvis_session"
        language = user_input.language
        
        _LOGGER.info("Jarvis Agent captured voice text: '%s'", user_text)

        # По умолчанию шлем на локальный хост Оранж Пи, сеть host прокинет пакет куда надо
        agent_url = "http://127.0.0.1:8090"
        ai_response = "I am ready, Sir."

        # Формируем плоский, легкий payload для нашего voice_interface.py
        payload = {
            "query": user_text,
            "conversation_id": conversation_id,
            "language": language,
            "stream": False  # Намертво отключаем весь этот капризный стриминг
        }

        try:
            # Открываем асинхронную сессию и бьем по порту 8090 с таймаутом в 10 секунд
            async with aiohttp.ClientSession() as session:
                async with session.post(agent_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        res_json = await response.json()
                        # Забираем ответ Квена. Поддерживаем дефолтное поле 'output'
                        ai_response = res_json.get("output", "I am ready, Sir.").strip()
                    else:
                        _LOGGER.error("Jarvis HTTP server returned status %s", response.status)
                        ai_response = "Communication error with Jarvis core, Sir."
                        
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to Jarvis core on port 8090")
            ai_response = "Jarvis core is thinking too long, Sir."
        except Exception as e:
            _LOGGER.error("Critical error connecting to Jarvis core: %s", e)
            ai_response = "Jarvis core is offline, Sir."

        # Формируем системный успешный ответ для Home Assistant Core
        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_speech(ai_response)

        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=conversation_id
        )

