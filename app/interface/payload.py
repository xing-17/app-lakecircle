from __future__ import annotations

import hashlib
import json
from typing import Any

from xlog.format.base import FormatLike

from app.base.component import Component


class Payload(Component):
    """
    Configuration payload encapsulation as Dict-like object.

    Attrs:
        origin: Original flat configuration dictionary.
        content: Structured configuration content.

    Methods:
        build(data): Build structured configuration from flat dictionary.
        get(key, default): Retrieve value by dotted key notation.
        has(key): Check if key exists in payload.
        fingerprint(): Generate short hash of configuration for tracking.
        describe(): Get comprehensive description of payload.

    Example:
    ```python
        data = {
            "APP_NAME": "myapp",
            "APP_LEVEL": "INFO",
            "APP_WORKFLOWS": ["workflow1", "workflow2"]
        }
        payload = Payload(data=data)
        payload.get("APP_NAME")  # 'myapp'
        payload.get("workflow.items")  # ['workflow1', 'workflow2']
        payload.fingerprint()  # 'a1b2c3d4'
    ```
    """

    def __init__(
        self,
        data: dict[str, Any],
        parent: Component | None = None,
        logformat: FormatLike | None = None,
    ) -> None:
        super().__init__(
            parent=parent,
            logformat=logformat,
        )
        self.origin: dict[str, Any] = data
        self.content: dict[str, dict[str, Any]] = self.build(data)

    def _resolve_key(
        self,
        key: str,
    ) -> list[str]:
        if "." in key:
            return key.split(".")
        else:
            return [key]

    def build(
        self,
        data: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        self.debug(
            "Recieved context Ok.",
            context=data,
        )
        # Assert LCC_ENDPOINT is present
        endpoint = data.get("LCC_ENDPOINT")
        if not endpoint:
            msg = "LCC_ENDPOINT is required in payload"
            self.error(msg)
            raise ValueError(msg)
        else:
            if not endpoint.endswith("/"):
                endpoint += "/"

        # Assert AWS account and region are present
        aws_account = data.get("LCC_AWS_ACCOUNT")
        aws_region = data.get("LCC_AWS_REGION")
        if not aws_account:
            msg = "LCC_AWS_ACCOUNT is required in payload"
            self.error(msg)
            raise ValueError(msg)
        if not aws_region:
            msg = "LCC_AWS_REGION is required in payload"
            self.error(msg)
            raise ValueError(msg)

        # Build structured content
        result = {
            "app": {
                "name": data.get("LCC_APP_NAME"),
                "alias": data.get("LCC_APP_ALIAS"),
                "level": data.get("LCC_APP_LEVEL"),
                "logformat": data.get("LCC_LOG_FORMAT"),
            },
            "endpoint": {
                # Base endpoint URI for LakeCircle
                "base": endpoint,
                # Apply definition to current and previous endpoints
                "current": f"{endpoint}current/",
                "previous": f"{endpoint}previous/",
                "history": f"{endpoint}history/",
                # Manual definition endpoint
                "definition": f"{endpoint}definition/",
                # Data and log endpoints
                "data": f"{endpoint}data/",
                "log": f"{endpoint}log/",
            },
            "aws": {
                "account": data.get("LCC_AWS_ACCOUNT"),
                "region": data.get("LCC_AWS_REGION"),
            },
            "work": {
                "actions": data.get("LCC_ACTIONS"),
                "params": data.get("LCC_ACTION_PARAMS"),
            },
        }
        self.info(
            "Payload built successfully.",
            context=result,
        )
        return result

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        keys = self._resolve_key(key)
        value = self.content
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def has(self, key: str) -> bool:
        try:
            self.get(key)
            return True
        except (KeyError, TypeError):
            return False

    def require(self, key: str) -> Any:
        value = self.get(key)
        if value is None:
            msg = f"Key '{key}' is required."
            self.error(msg)
            raise KeyError(msg)
        return value

    def fingerprint(self) -> str:
        content_str = json.dumps(self.origin, sort_keys=True)
        hash_obj = hashlib.sha256(content_str.encode())
        return hash_obj.hexdigest()[:8]

    def describe(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint(),
            "origin": self.origin,
            "content": self.content,
        }
