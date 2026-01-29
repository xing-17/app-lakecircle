from __future__ import annotations

from xlog.format import (
    ColorText,
    ColorTree,
    Text,
    Tree,
)

from app.base.component import Component
from app.interface.constants import CONSTANTS, VARIABLES
from app.interface.payload import Payload
from app.variable.setting import Setting
from app.work.summarise import SummariseWork
from app.work.sync import SyncWork


class Interface(Component):
    def __init__(self) -> None:
        super().__init__(
            name=f"{self.__class__.__name__}",
            level="DEBUG",
            logformat=Text(),
            loggroup=True,
        )
        self.setup()
        self.info(f"Initialised module '{self.name}' OK.")

    def setup(self) -> None:
        # Initialize settings
        self.setting = Setting(
            parent=self,
            variables=VARIABLES,
            constants=CONSTANTS,
        )

        # Update log level from settings
        level = self.setting.get("LCC_APP_LEVEL", None)
        if level:
            self.level = level.upper()
            self.logstream.set_level(self.level)
            self.debug(f"POST_RUN: APP_LEVEL set to '{self.level}'.")

        # Update application name from settings
        name = self.setting.get("LCC_APP_NAME", None)
        if name:
            self.name = name
            self.debug(f"POST_RUN: APP_NAME set to '{self.name}'.")

        # Update log format from settings
        format = self.setting.get("LCC_LOG_FORMAT", None)
        if format:
            if format.upper() == "TREE":
                self.logformat = Tree()
            elif format.upper() == "COLORTREE":
                self.logformat = ColorTree()
            elif format.upper() == "COLORTEXT":
                self.logformat = ColorText()
            else:
                self.logformat = Text()
            self.logstream.set_format(self.logformat)
            self.debug(f"POST_RUN: LOG_FORMAT set to '{format}'.")

    def run(self) -> None:
        self.info("Running workflows")
        self.payload = Payload(
            parent=self,
            data=self.setting.context,
        )
        actions = self.payload.get("work.actions", [])
        for action in actions:
            if action.upper() == "SYNC":
                work = SyncWork(
                    parent=self,
                    payload=self.payload,
                )
                self.info(f"Executing action '{action}'")
                work.run()
            elif action.upper() == "SUMMARISE":
                work = SummariseWork(
                    parent=self,
                    payload=self.payload,
                )
                self.info(f"Executing action '{action}'")
                work.run()
            else:
                msg = f"Unsupported action '{action}'"
                self.warning(msg)
                continue
