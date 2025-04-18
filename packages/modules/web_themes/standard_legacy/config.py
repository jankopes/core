from helpermodules.auto_str import auto_str

from modules.common.abstract_device import DeviceDescriptor


@auto_str
class StandardLegacyWebThemeConfiguration:
    def __init__(self,
                 history_chart_range: int = 30 * 60 * 1000  # 30 minutes in milliseconds
                 ) -> None:
        self.history_chart_range = history_chart_range


@auto_str
class StandardLegacyWebTheme:
    def __init__(self,
                 name: str = "Standard",
                 type: str = "standard_legacy",
                 official: bool = True,
                 configuration: StandardLegacyWebThemeConfiguration = None) -> None:
        self.name = name
        self.type = type
        self.official = official
        self.configuration = configuration or StandardLegacyWebThemeConfiguration()


theme_descriptor = DeviceDescriptor(configuration_factory=StandardLegacyWebTheme)
