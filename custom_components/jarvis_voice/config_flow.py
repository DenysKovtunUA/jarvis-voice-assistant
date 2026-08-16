import logging
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "jarvis_voice"
_LOGGER = logging.getLogger(__name__)

class JarvisVoiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Стерильная логика создания интеграции Джарвиса в UI без лишних окон."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Мгновенно создает сущность при добавлении интеграции."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        _LOGGER.info("Jarvis Voice Engine config flow triggered. Automatically registering...")

        return self.async_create_entry(
            title="Jarvis v3.1 Engine",
            data={}
        )
ч

