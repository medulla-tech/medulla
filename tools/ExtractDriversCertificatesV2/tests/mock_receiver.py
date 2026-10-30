#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mock_receiver.py - Substitut maitre de test autour du VRAI plugin serveur
=========================================================================

Il n'y a plus de recepteur "de reference" distinct (v1) : ce module charge le
plugin de production `server/plugin_extract_drivers.py` et le pilote comme le
ferait le substitut maitre de Medulla :

  * les trames `big_data` sont reassemblees comme `plugin_big_data.py`
    (concatenation des tranches, base64, zlib, JSON) puis reinjectees dans le
    plugin avec `msg["from"] = data["from"]` ;
  * les autres trames appellent directement
    `action(xmppobject, action, sessionid, data, msg, ret, dataerreur)` ;
  * le `xmppobject` est un faux qui capture `send_message` (les reponses du
    plugin : plan, reprise, accuse de reception, renvoi, erreur).

Le depot du plugin est redirige vers un repertoire de test (`DEPOT_ROOT`).
Aucune autre logique de protocole n'est dupliquee ici : ce qui est teste est
exactement le code qui sera deploye.

Usage en rejeu d'une capture (`Send-DriversOverXmpp.py --dump-frames`) :
    python3 tests/mock_receiver.py --frames trames.jsonl --depot /tmp/depot
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import os
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_PATH = os.path.join(os.path.dirname(HERE), "server", "plugin_extract_drivers.py")


def load_plugin(depot: str):
    """Charge une instance neuve du module plugin, pointee sur `depot`."""
    spec = importlib.util.spec_from_file_location("plugin_extract_drivers_under_test",
                                                  PLUGIN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DEPOT_ROOT = depot
    module.REQUIRE_MOUNTPOINT = False
    return module


class FakeXmppObject:
    """Remplace l'objet substitut : capture les messages envoyes par le plugin."""

    def __init__(self):
        self.outbox = []

    def send_message(self, mto=None, mbody=None, mtype="chat"):
        self.outbox.append({"to": str(mto), "type": mtype, "body": json.loads(mbody)})


class Receiver:
    """
    `feed(body)` remet une trame (dict deja decode) au plugin et retourne la
    liste des reponses (dict) que le plugin a emises, dans l'ordre.
    """

    def __init__(self, depot: str, sender_jid: str = "pc-001.ab1@pulse/extractdrivers-1",
                 logger=None):
        self.depot = depot
        self.sender_jid = sender_jid
        self.log = logger or (lambda message: None)
        self.plugin = load_plugin(depot)
        self.xmpp = FakeXmppObject()
        self._bigdata = {}

    # -- big_data : meme algorithme que plugin_big_data.py ---------------

    def _bigdata_feed(self, body):
        data = body["data"]
        session = body["sessionid"]
        bucket = self._bigdata.setdefault(session, {})
        bucket[int(data["nb_segment"])] = data["segment"]
        if len(bucket) < int(data["nb_segment_total"]):
            return None
        joined = "".join(bucket[i] for i in sorted(bucket))
        del self._bigdata[session]
        logical = json.loads(zlib.decompress(base64.b64decode(joined)).decode("utf-8"))
        return logical, data["from"]

    def feed(self, body: dict) -> list:
        before = len(self.xmpp.outbox)
        sender = self.sender_jid
        if body.get("action") == "big_data":
            assembled = self._bigdata_feed(body)
            if assembled is None:
                return []
            body, sender = assembled
        msg = {"from": sender, "type": "chat"}
        self.plugin.action(self.xmpp, body["action"], body["sessionid"], body["data"],
                           msg, body.get("ret", 0), {})
        return [item["body"] for item in self.xmpp.outbox[before:]]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--frames", required=True, help="capture JSONL du transporteur")
    parser.add_argument("--depot", required=True, help="racine du depot de test")
    parser.add_argument("--from", dest="sender", default="pc-001.ab1@pulse/extractdrivers-1")
    parser.add_argument("--verbose", action="store_true")
    options = parser.parse_args(argv)

    os.makedirs(options.depot, exist_ok=True)
    receiver = Receiver(options.depot, options.sender)
    final = None
    with open(options.frames, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            frame = json.loads(line)
            for answer in receiver.feed(frame["body"]):
                if options.verbose:
                    print("<- %s %s" % (answer["action"], json.dumps(answer["data"])[:200]))
                if answer["action"].endswith(("_done", "_error")):
                    final = answer
    if final is None:
        print("Aucune reponse finale du plugin.", file=sys.stderr)
        return 1
    print(json.dumps(final["data"], indent=2))
    return 0 if final["action"].endswith("_done") else 1


if __name__ == "__main__":
    sys.exit(main())
