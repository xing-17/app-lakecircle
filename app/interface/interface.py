from __future__ import annotations

from xlog.format.text import Text
from xlog.format.tree import Tree

from app.base.component import Component


class Interface(Component):
    def __init__(self) -> None:
        super().__init__(
            name=f"{self.__class__.__name__}",
            level="INFO",
            logformat=Text(),
            loggroup=True,
        )
        self.setup()
        self.info(f"Initialised module '{self.name}' OK.")

    def setup(self) -> None:
        # Update log level from settings
        level = self.setting.get("LCC_APP_LEVEL", None)
        if level:
            self.level = level.upper()
            self.logstream.set_level(self.level)
            self.debug(f"APP_LEVEL set to '{self.level}'.")

        # Update application name from settings
        name = self.setting.get("LCC_APP_NAME", None)
        if name:
            self.name = name
            self.debug(f"APP_NAME set to '{self.name}'.")

        # Update log format from settings
        format = self.setting.get("LCC_LOG_FORMAT", None)
        if format:
            self.logformat = Tree() if format.upper() == "TREE" else Text()
            self.debug(f"LOG_FORMAT set to '{format}'.")

    def run(self) -> None:
        self.info("Running workflows")
