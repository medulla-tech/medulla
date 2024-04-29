# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later
from setuptools import setup

import os
import sys

if sys.platform.startswith("linux"):
    fileconf = os.path.join("/", "etc", "medulla")
elif sys.platform.startswith("win"):
    fileconf = os.path.join(os.environ["ProgramFiles"], "Medulla", "etc")
elif sys.platform.startswith("darwin"):
    fileconf = os.path.join("/", "Library", "Application Support", "Medulla", "etc")

setup(
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GPL License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords="medulla",
    name="medulla",
    version='5.1.0',  # fmt: skip
    debian_distro="stretch",  # fmt: skip
    description="medulla",
    url="https://www.siveo.net/",
    packages=["medulla"],
    test_suite="",
    package_data={},
    entry_points={},
    extras_require={},
    install_requires=[],
)
