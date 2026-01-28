from __future__ import annotations

import sys
import traceback

from app.interface.interface import Interface


def main() -> int:
    try:
        app = Interface()
        app.run()
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
