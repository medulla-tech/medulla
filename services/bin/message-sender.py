#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from slixmpp import ClientXMPP
from slixmpp import jid
from slixmpp.xmlstream import handler, matcher
from slixmpp.xmlstream.stanzabase import ET
from slixmpp.exceptions import *
import slixmpp
import asyncio
import os
import logging
from argparse import ArgumentParser

logger = logging.getLogger("message-sender")
# Additionnal path


class MyXMPPClient(ClientXMPP):
    def __init__(
        self,
        jid,
        password,
        message,
        timeout=20,
        toagent="master@medulla",
        ipv4="127.0.0.1",
        port=5222,
    ):
        super().__init__(jid, password)
        self.stanzamessage = message
        self.timeout = timeout
        self.toagent = toagent
        self.ipv4 = ipv4
        self.port = port

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("register", self.register)
        self.add_event_handler("connecting", self.handle_connecting)
        self.add_event_handler("connection_failed", self.connection_failed)
        self.add_event_handler("disconnected", self.handle_disconnected)
        self.add_event_handler("connected", self.handle_connected)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        # We're only concerned about registering, so nothing more to do here.
        self.send_message(mto=self.toagent, mbody=self.stanzamessage, mtype="chat")
        self.disconnect()

    async def message(self, msg):
        # msg["body"]
        # msg["type"]
        # msg["from"]
        logging.debug("Message : %s" % msg["body"])

    async def stop(self):
        logger.debug("Stopping XMPP client...")
        self.disconnect()

    def handle_connecting(self, data):
        """
        success connecting agent
        """
        logger.debug("Connected")

    def connection_failed(self, data):
        """
        on connection failed on libere la connection
        """
        logger.debug("Failed to connect to %s : %s" % (self.boundjid, data))
        self.disconnect()

    def handle_disconnected(self, data):
        logger.debug("Disconnected")

    def handle_connected(self, data):
        """
        success connecting agentconnect(
        """
        logger.debug("connected to %s" % (self.boundjid))

    async def register(self, iq):
        """
        Fill out and submit a registration form.

        The form may be composed of basic registration fields, a data form,
        an out-of-band link, or any combination thereof. Data forms and OOB
        links can be checked for as so:

        if iq.match('iq/register/form'):
            # do stuff with data form
            # iq['register']['form']['fields']
        if iq.match('iq/register/oob'):
            # do stuff with OOB URL
            # iq['register']['oob']['url']

        To get the list of basic registration fields, you can use:
            iq['register']['fields']
        """
        resp = self.Iq()
        resp["type"] = "set"
        resp["register"]["username"] = self.boundjid.user
        resp["register"]["password"] = self.password
        try:
            await resp.send()
            logger.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logger.error("Could not register account: %s" % e.iq["error"]["text"])
            self.disconnect()
        except IqTimeout:
            logger.error("No response from server.")
            self.disconnect()


async def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-P",
        "--port",
        dest="port",
        type=int,
        default=5222,
        help="port utilisé (par défaut: 5222)",
    )
    parser.add_argument(
        "-I",
        "--ipv4",
        dest="ipv4",
        default="127.0.0.1",
        help="adresse IPv4 de destination",
    )
    parser.add_argument("-j", "--jid", dest="jid", help="JID à utiliser")
    parser.add_argument(
        "-p", "--password", dest="password", help="mot de passe à utiliser"
    )
    parser.add_argument("-m", "--message", dest="message", help="message envoyé")
    parser.add_argument(
        "-T",
        "--timeout",
        dest="timeout",
        type=int,
        default=5,
        help="timeout en secondes (par défaut: 5)",
    )
    parser.add_argument(
        "-t",
        "--toagent",
        dest="toagent",
        default="master@medulla",
        help="agent destinataire du message)",
    )
    parser.add_argument(
        "-L",
        "--levellog",
        dest="levellog",
        default="DEBUG",
        help="niveau de journalisation (par défaut: DEBUG)",
    )
    parser.add_argument(
        "-F",
        "--filelog",
        dest="filelog",
        default="/var/log/medulla/message-sender.log",
        help="fichier de journal (par défaut: /var/log/medulla/message-sender.log)",
    )
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    log_dir = os.path.dirname(args.filelog)
    print(log_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=args.levellog.upper(),
        format="%(levelname)-8s %(message)s",
        filename=args.filelog,
    )
    # self.logger = logging.getLogger('message-sender')
    if sys.platform.startswith("linux") and os.getuid() != 0:
        logging.error("Agent must be running as root")
        sys.exit(0)
    elif sys.platform.startswith("win") and isWinUserAdmin() == 0:
        logging.error("Medulla agent must be running as Administrator")
        sys.exit(0)
    elif sys.platform.startswith("darwin") and not isMacOsUserAdmin():
        logging.error("Medulla agent must be running as root")
        sys.exit(0)
    # xmpp = MyXMPPClient(jid, password, message, timeout, toagent, ipv4, port)
    xmpp = MyXMPPClient(
        args.jid,
        args.password,
        args.message,
        args.timeout,
        args.toagent,
        args.ipv4,
        args.port,
    )
    xmpp.register_plugin("xep_0030")  # Service Discovery
    xmpp.register_plugin("xep_0045")  # Multi-User Chat
    xmpp.register_plugin("xep_0004")  # Data Forms
    xmpp.register_plugin("xep_0050")  # Adhoc Commands
    xmpp.register_plugin(
        "xep_0199",
        {"keepalive": True, "frequency": 600, "interval": 600, "timeout": 500},
    )
    xmpp.register_plugin("xep_0077")  # In-band Registration
    xmpp["xep_0077"].force_registration = True
    # Démarre le client XMPP dans une boucle asyncio

    xmpp.connect()
    # Temporisateur pour déclencher l'événement après 10 secondes
    await asyncio.sleep(10)
    # Déclenche l'événement d'arrêt pour déconnecter proprement le client XMPP
    await xmpp.stop()


if __name__ == "__main__":
    asyncio.run(main())
