import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "jarvis_voice"
CONF_TIMEOUT = "timeout"
DEFAULT_TIMEOUT = 30

_LOGGER = logging.getLogger(__name__)

class JarvisVoiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Логика создания интеграции Джарвиса в UI с настройкой таймаута."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Вызывается при первом добавлении интеграции."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            _LOGGER.info("Registering Jarvis Voice Engine with timeout: %ss", user_input[CONF_TIMEOUT])
            return self.async_create_entry(
                title="Jarvis v3.1 Engine",
                data={CONF_TIMEOUT: user_input[CONF_TIMEOUT]}
            )

        # Выводим форму ввода таймаута при создании
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=120)
                )
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Подключаем обработчик изменения параметров через кнопку в UI."""
        return JarvisVoiceOptionsFlowHandler(config_entry)


class JarvisVoiceOptionsFlowHandler(config_entries.OptionsFlow):
    """Управление изменением таймаута через кнопку 'Параметры'."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Инициализация."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Вызывается при клике на 'Параметры' (Configure) на плитке интеграции."""
        if user_input is not None:
            _LOGGER.info("Updating Jarvis Voice Engine timeout parameters to: %ss", user_input[CONF_TIMEOUT])
            # Сохраняем новые настройки обратно в entry.data
            self.hass.config_entries.async_update_entry(
                self.config_entry, 
                data={**self.config_entry.data, CONF_TIMEOUT: user_input[CONF_TIMEOUT]}
            )
            return self.async_create_entry(title="", data={})

        # Получаем текущий сохраненный таймаут или берем дефолтный 30
        current_timeout = self.config_entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

        # Показываем форму редактирования в UI
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_TIMEOUT, default=current_timeout): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=120)
                )
            })
        )

