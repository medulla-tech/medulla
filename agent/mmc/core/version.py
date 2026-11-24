# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2011 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
 Provide tools to compute components version
"""

import subprocess


def _get_package_version():
    """Return the installed pulse2-common package version."""
    commands = (
        ("dpkg-query", "-W", "-f=${Version}", "pulse2-common"),
        ("rpm", "-q", "--qf", "%{VERSION}-%{RELEASE}", "pulse2-common"),
    )
    for command in commands:
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            continue
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return ""


def getMedullaVersion():
    """ Extract version number using dpkg or rpm command on mmc-agent package
    command: dpkg-query -W -f='${Version}' pulse2-common 2>/dev/null | cut -d'g' -f1
    """
    return _get_package_version().split("g", 1)[0]


def getMedullaRevision():
    """ Extract revision number using dpkg or rpm command on mmc-agent package
    command: dpkg-query -W -f='${Version}' pulse2-common 2>/dev/null | cut -d't' -f2 | cut -d'.' -f1
    """
    version = _get_package_version()
    if "t" not in version:
        return ""
    return version.split("t", 1)[1].split(".", 1)[0]
