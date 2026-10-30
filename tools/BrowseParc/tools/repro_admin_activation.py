#!/usr/bin/env python3
"""Reproduit l'activation du plugin admin pour voir l'erreur reelle."""
import logging
import sys
import traceback

sys.path.insert(0, "/usr/lib/python3/dist-packages")

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")

from mmc.plugins.admin.config import AdminConfig          # noqa: E402
from pulse2.database.admin import AdminDatabase           # noqa: E402

config = AdminConfig("admin")
print("--- config.disable =", config.disable)
print("--- base =", getattr(config, "base", None), "dbname =", getattr(config, "dbname", None))

database = AdminDatabase()
try:
    result = database.activate(config)
    print("--- activate() ->", result)
except Exception:
    print("--- activate() a leve :")
    traceback.print_exc()
