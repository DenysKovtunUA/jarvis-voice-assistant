import logging
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

# Должно строго совпадать с "domain" из manifest.json
DOMAIN = "jarvis_voice"

_LOGGER = logging.getLogger(__name__)

class JarvisVoiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Логика автоматического создания интеграции Джарвиса в UI."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Вызывается при клике на имя интеграции в списке служб."""
        
        # Проверяем, не добавлена ли интеграция уже в систему (защита от дубликатов)
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        _LOGGER.info("Jarvis Voice Engine config flow triggered. Automatically registering...")

        # Мгновенно создаем сущность в системе, передавая пустой словарь настроек data,
        # так как все параметры (IP 127.0.0.1 и порт 8090) мы жестко и безопасно зашили в код.
        return self.async_create_entry(
            title="Jarvis v3.1 Engine",
            data={}
        )

