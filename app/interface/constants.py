from __future__ import annotations

from app.variable.constant import Constant
from app.variable.environ import Environ
from app.variable.varkind import VarKind

VARIABLES = [
    Environ(
        name="LCC_APP_LEVEL",
        kind=VarKind.STRING,
        default="INFO",
        choice=["DEBUG", "INFO"],
        description="APP LOG LEVEL, choose from: [DEBUG, INFO]",
    ),
    Environ(
        name="LCC_LOG_FORMAT",
        kind=VarKind.STRING,
        default="TREE",
        choice=["TREE", "TEXT"],
        description="APP LOG FORMAT, choose from: [TREE, TEXT]",
    ),
]
CONSTANTS = [
    Constant(
        name="LCC_APP_NAME",
        kind=VarKind.STRING,
        value="lakecircle",
        description="Application name",
    ),
    Constant(
        name="LCC_APP_ALIAS",
        kind=VarKind.STRING,
        value="江堰",
        description="Application alias",
    ),
]
