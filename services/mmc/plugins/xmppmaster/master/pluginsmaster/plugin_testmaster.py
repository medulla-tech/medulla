#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.plugins.xmppmaster.master.lib.utils import pluginmastersessionaction
import logging

plugin = {"VERSION": "1.0", "NAME": "testmaster", "TYPE": "master"}


@pluginmastersessionaction("actualise", 20)
def action(xmppobject, action, sessionid, data, message, ret, objsessiondata):
    logging.getLogger().debug(plugin)
    xmppobject.session.affiche()
    pass
