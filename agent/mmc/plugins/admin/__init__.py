# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
VERSION = "5.4.5"
APIVERSION = "0:0:0"
REVISION = ""


def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = AdminConfig("admin")

    if config.disable:
        logger.warning("Plugin admin: disabled by configuration.")
        return False

    if not AdminDatabase().activate(config):
        logger.warning(
            "Plugin admin: an error occurred during the database initialization"
        )
        return False
    return True
