from __future__ import annotations

from typing import Any

from xlog.format import FormatLike, Text
from xlog.group import GroupLike, LogGroup
from xlog.stream import LogStream


class Component:
    """Base component class providing hierarchical logging infrastructure.

    The Component class serves as the foundation for all application components,
    providing automatic logging configuration inheritance and consistent behavior
    across the component hierarchy. Child components inherit configuration from
    their parent, enabling a unified logging approach throughout the application.

    Attributes:
        parent (Component | None): Optional parent component for inheritance.
        name (str): Resolved component name (uses class name if not specified).
        level (str): Log level for this component (INFO, DEBUG, WARNING, ERROR).
        loggroup (GroupLike | None): Optional log grouping for organizing output.
        logformat (FormatLike): Log format implementation for output formatting.
        logstream (LogStream): Configured stream for emitting log messages.

    Methods:
        log(message: str, **kwargs: Any) -> None:
            Log message at INFO level with optional context.

        info(message: str, **kwargs: Any) -> None:
            Log informational message with optional context.

        debug(message: str, **kwargs: Any) -> None:
            Log debug message (only visible when level=DEBUG).

        warning(message: str, **kwargs: Any) -> None:
            Log warning message for potential issues.

        error(message: str, **kwargs: Any) -> None:
            Log error message for failures and exceptions.

        get_root() -> Component:
            Get the root component in the hierarchy.

        get_depth() -> int:
            Get the depth of this component in the hierarchy (0 for root).

    Example:
        >>> root = Component(name="root", level="INFO")
        >>> child = Component(parent=root)
        >>> child.info("hello", context={"key": "value"})

        # With hierarchy
        >>> interface = Component(name="Interface", level="DEBUG")
        >>> runtime = Component(parent=interface)
        >>> runtime.debug("Runtime initialized")  # Inherits DEBUG level

    Note:
        - Components automatically inherit logging configuration from parents
        - Use parent parameter to establish hierarchy and share configuration
        - Log levels: DEBUG < INFO < WARNING < ERROR
        - Context can be passed via **kwargs to any logging method
    """

    def __init__(
        self,
        name: str | None = None,
        level: str | None = None,
        parent: Component | None = None,
        logformat: FormatLike | None = None,
        loggroup: GroupLike | bool | None = None,
    ) -> None:
        self.parent = parent
        self.name = self._resolve_name(name)
        self.level = self._resolve_level(level)
        self.loggroup = self._resolve_loggroup(loggroup)
        self.logformat = self._resolve_logformat(logformat)
        self.logstream = self._resolve_logstream()

    def _resolve_name(
        self,
        name: str | None = None,
    ) -> str:
        default = self.__class__.__name__
        if not name:
            if self.parent and hasattr(self.parent, "name"):
                return f"{self.parent.name}::{default}"
            return default
        return name

    def _resolve_level(
        self,
        level: str | None = None,
    ) -> str:
        default = "INFO"
        if not level:
            if self.parent and hasattr(self.parent, "level"):
                return self.parent.level
            return default
        return level.upper()

    def _resolve_logformat(
        self,
        logformat: FormatLike | None = None,
    ) -> FormatLike:
        default = Text()
        if not logformat:
            if self.parent and hasattr(self.parent, "logformat"):
                return self.parent.logformat
            return default
        return logformat

    def _resolve_loggroup(
        self,
        group: GroupLike | bool | None = None,
    ) -> GroupLike | None:
        if isinstance(group, bool):
            return LogGroup(name=f"{self.name}::group") if group else None
        if isinstance(group, GroupLike):
            return group
        if self.parent and hasattr(self.parent, "loggroup"):
            return self.parent.loggroup
        return None

    def _resolve_logstream(
        self,
    ) -> LogStream:
        groups: list[GroupLike] = [] if self.loggroup is None else [self.loggroup]
        return LogStream(
            name=f"{self.name}::stream",
            level=self.level,
            verbose=True,
            format=self.logformat,
            groups=groups,
        )

    def get_root(self) -> Component:
        current = self
        while current.parent is not None:
            current = current.parent
        return current

    def get_depth(self) -> int:
        depth = 0
        current = self
        while current.parent is not None:
            depth += 1
            current = current.parent
        return depth

    def log(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.logstream.log(
            level="INFO",
            message=message,
            **kwargs,
        )

    def info(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.logstream.log(
            level="INFO",
            message=message,
            **kwargs,
        )

    def error(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.logstream.log(
            level="ERROR",
            message=message,
            **kwargs,
        )

    def debug(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.logstream.log(
            level="DEBUG",
            message=message,
            **kwargs,
        )

    def warning(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.logstream.log(
            level="WARNING",
            message=message,
            **kwargs,
        )
