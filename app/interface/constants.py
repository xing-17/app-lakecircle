from __future__ import annotations

from app.variable.constant import Constant
from app.variable.environ import Environ
from app.variable.varkind import VarKind

VARIABLES = [
    Environ(
        name="LCC_ACTION_PARAMS",
        kind=VarKind.DICT,
        default={},
        description="APP ACTION PARAMETERS, e.g., {'force': True}",
    ),
    Environ(
        name="LCC_ACTIONS",
        kind=VarKind.LIST,
        default=["SYNC"],
        choice=[
            "SYNC",  # Apply changes to the bucket
            "DRYRUN",  # Simulate actions without making changes
        ],
        description="APP ACTIONS, choose from: [SYNC, DRYRUN]",
    ),
    Environ(
        name="LCC_ENDPOINT",
        kind=VarKind.STRING,
        description="APP ENDPOINT, e.g.,s3://bucket-name/prefix/path",
    ),
    Environ(
        name="LCC_AWS_ACCOUNT",
        kind=VarKind.STRING,
        description="APP AWS ACCOUNT NUMBER, e.g., 123456789012",
    ),
    Environ(
        name="LCC_AWS_REGION",
        kind=VarKind.STRING,
        description="APP AWS REGION, e.g., us-west-2",
    ),
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
        choice=["TREE", "TEXT", "COLORTREE", "COLORTEXT"],
        description="APP LOG FORMAT, choose from: [TREE, TEXT, COLORTREE, COLORTEXT]",
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
