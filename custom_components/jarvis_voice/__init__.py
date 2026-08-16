import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Указываем, что наша интеграция содержит сущность типа Conversation
PLATFORMS: list[Platform] = [Platform.CONVERSATION]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Вызывается, когда интеграция успешно активируется в UI."""
    _LOGGER.info("Initializing Jarvis v3.1 Voice Engine Component...")
    
    # Передаем управление коду в conversation.py для регистрации агента
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Вызывается, если пользователь решит удалить или отключить интеграцию в UI."""
    _LOGGER.info("Unloading Jarvis v3.1 Voice Engine Component...")
    
    # Чисто выгружаем сущности из памяти Home Assistant
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

