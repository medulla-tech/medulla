# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# On remote pulse2-package-server case, this import fails because utils.py is not installed on remote package-server
# So we keep this import for global use in mmc. But it will be ignored on pulse2-package-server
try:
    from .utils import convert
except:
    pass
