#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fake_slixmpp.py - Faux slixmpp pour tester le transporteur hors ligne
=====================================================================

Ce module n'est PAS un composant de production : il remplace `slixmpp` le
temps d'un test, afin de pouvoir executer `Send-DriversOverXmpp.py` de bout en
bout (connexion, emission des trames, ACK, code de sortie) **sans serveur
XMPP, sans ejabberd et sans le paquet pulse_xmpp_agent**.

Il imite l'API et la semantique de slixmpp 1.8.5 telle qu'utilisee par le
transporteur :

  * `connect()` est SYNCHRONE (la connexion est planifiee sur la boucle) ;
  * `waiting_queue` est une vraie `asyncio.Queue` alimentee par `send_message`
    puis videe de facon asynchrone : la contre-pression et l'attente de
    vidage avant fermeture sont donc reellement exercees ;
  * `disconnect(wait=...)` retourne un Future deja resolu ;
  * les echecs sont signales par les EVENEMENTS (`connection_failed`,
    `failed_auth`) et non par une exception de `connect()` : c'est ce que fait
    slixmpp 1.8.5 (`_connect_routine` intercepte les OSError et replanifie).

Chaque message emis est confie a `mock_receiver.Receiver`, qui pilote le VRAI
plugin serveur (`server/plugin_extract_drivers.py`). Les reponses du plugin
(plan, reprise, renvoi, accuse de reception, erreur) sont renvoyees au
transporteur via l'evenement `message`, ce qui valide le contrat complet.

Pilotage par variables d'environnement
--------------------------------------
  FAKE_SLIXMPP_DEPOT        repertoire de depot (obligatoire)
  FAKE_SLIXMPP_FRAMES       fichier JSONL ou journaliser les trames emises
  FAKE_SLIXMPP_REPLIES      fichier JSONL ou journaliser les reponses du plugin
  FAKE_SLIXMPP_ACK          'on' (defaut) : toutes les reponses sont renvoyees ;
                            'nofinal' : plan/reprise/renvois oui, mais jamais
                            l'accuse final (`_done`) ; 'none' : aucune reponse
  FAKE_SLIXMPP_FAIL         'connect' ou 'auth' : simuler un echec
  FAKE_SLIXMPP_SLOW_QUEUE   '1' : ne jamais vider la file d'envoi
  FAKE_SLIXMPP_SPOOF_FROM   JID usurpe pour les reponses
  FAKE_SLIXMPP_DROP_SESSION '1' : reponses sans sessionid (doivent etre ignorees)
  FAKE_SLIXMPP_TLS          '1' : simuler une session chiffree
  FAKE_SLIXMPP_CORRUPT_BLOCK '1' : alterer le premier bloc de donnees emis
  FAKE_SLIXMPP_RESEND       '1' : le recepteur "perd" le premier bloc recu et
                            en demande le renvoi
  FAKE_SLIXMPP_CUT_AFTER    N : la connexion tombe apres N blocs de donnees
                            livres (une seule fois par fichier de marque, voir
                            FAKE_SLIXMPP_CUT_MARK)
  FAKE_SLIXMPP_CUT_MARK     fichier de marque : la coupure n'a lieu que s'il
                            n'existe pas encore (il est cree a la coupure)
  FAKE_SLIXMPP_QUIET        '1' : ne rien ecrire sur la sortie d'erreur
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import zlib

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from mock_receiver import Receiver  # noqa: E402  (import apres ajustement du chemin)

__version__ = "1.8.5-fake"

DEFAULT_MASTER_JID = "master@pulse"


def _flag(name: str) -> bool:
    return os.environ.get(name, "") not in ("", "0", "false", "False")


class _Jid:
    """JID minimal : le transporteur lit `.bare` sur l'expediteur."""

    def __init__(self, value: str):
        self.full = value
        self.bare = value.split("/")[0]
        self.user = self.bare.split("@")[0]
        host = self.bare.split("@")[-1]
        self.host = host

    def __str__(self):
        return self.full


class _Transport:
    """Transport truthy : le transporteur teste `client.transport`."""

    def __init__(self, tls: bool = False):
        self._tls = tls

    def get_extra_info(self, key, default=None):
        if self._tls and key in ("ssl_object", "sslcontext"):
            return object()
        return default

    def close(self):
        pass

    def abort(self):
        pass


class ClientXMPP:
    """Substitut minimal de `slixmpp.ClientXMPP` (API 1.8.5)."""

    def __init__(self, jid_value, password):
        self.jid = jid_value
        self.password = password
        self.boundjid = _Jid(jid_value)
        self.ssl_context = None
        self.transport = None
        self.features = set()
        self._handlers = {}
        self._connected = False

        depot = os.environ.get("FAKE_SLIXMPP_DEPOT")
        if not depot:
            raise RuntimeError("FAKE_SLIXMPP_DEPOT non defini")
        self._receiver = Receiver(depot, self.boundjid.full, logger=self._log)
        self._frames_path = os.environ.get("FAKE_SLIXMPP_FRAMES")
        self._frames_handle = (open(self._frames_path, "a", encoding="utf-8")
                               if self._frames_path else None)
        self._ack_mode = os.environ.get("FAKE_SLIXMPP_ACK", "on")
        self._replies_path = os.environ.get("FAKE_SLIXMPP_REPLIES")
        self._cut_after = int(os.environ.get("FAKE_SLIXMPP_CUT_AFTER", "0") or 0)
        self._cut_mark = os.environ.get("FAKE_SLIXMPP_CUT_MARK", "")
        self._data_delivered = 0
        self._slow_queue = _flag("FAKE_SLIXMPP_SLOW_QUEUE")
        self._corrupt_block = _flag("FAKE_SLIXMPP_CORRUPT_BLOCK")
        self._corrupted = False
        self._resend_sent = False
        # File d'envoi reelle : le transporteur s'en sert pour la
        # contre-pression et pour attendre le vidage avant de fermer.
        self.waiting_queue = asyncio.Queue()

    # -- API slixmpp -----------------------------------------------------

    def add_event_handler(self, name, handler):
        self._handlers.setdefault(name, []).append(handler)

    def connect(self, address=None, use_ssl=None, force_starttls=None,
                disable_starttls=None):
        """
        Comme slixmpp 1.8.5 : methode SYNCHRONE. Un echec de connexion est
        signale par l'evenement `connection_failed`, pas par une exception.
        """
        self.address = address
        self.force_starttls = force_starttls
        self.disable_starttls = disable_starttls
        self._loop = asyncio.get_event_loop()
        failure = os.environ.get("FAKE_SLIXMPP_FAIL", "")

        if failure == "connect":
            self._connected = False
            self._loop.call_soon(self._event, "connection_failed", None)
            return None

        if failure == "auth":
            self._connected = False
            self._loop.call_soon(self._event, "failed_auth", None)
            return None

        self._connected = True
        self.transport = _Transport(tls=_flag("FAKE_SLIXMPP_TLS"))
        if _flag("FAKE_SLIXMPP_TLS"):
            self.features.add("starttls")
        self._loop.call_soon(self._event, "session_start", None)
        return None

    def send_message(self, mto=None, mbody=None, mtype="chat"):
        """Met la trame en file (comme slixmpp) puis la remet au recepteur."""
        if not self._connected:
            raise RuntimeError("send_message avant connexion")
        body = json.loads(mbody)
        self.waiting_queue.put_nowait(body)
        if not self._slow_queue:
            # Vidage asynchrone FIDELE a slixmpp : sa boucle d'envoi fait
            # `await waiting_queue.get()` puis `task_done()`
            # (xmlstream.py:1263,1318). Appeler `task_done()` sans `get()`
            # laisserait `qsize()` croissant et bloquerait definitivement la
            # contre-pression du transporteur des le seuil franchi.
            self._loop.call_later(0.002, self._drain_one)

        if self._frames_handle is not None:
            self._frames_handle.write(json.dumps(
                {"to": mto, "type": mtype, "body": body}, ensure_ascii=False) + "\n")
            self._frames_handle.flush()

        if self._ack_mode == "none":
            return

        data = body.get("data") or {}
        is_data = data.get("type") == "data" and body.get("action") != "big_data"

        # Coupure de connexion apres N blocs livres (reprise apres interruption).
        if (is_data and self._cut_after and self._data_delivered >= self._cut_after
                and not (self._cut_mark and os.path.exists(self._cut_mark))):
            if self._cut_mark:
                open(self._cut_mark, "w").close()
            self._log("COUPURE de la connexion apres %d blocs" % self._data_delivered)
            self._connected = False
            self._loop.call_soon(self._event, "disconnected", None)
            return

        # Le recepteur "perd" le premier bloc recu : il en demande le renvoi AU
        # LIEU de le traiter, et ne finalise donc pas tant qu'il ne l'a pas recu.
        if is_data and _flag("FAKE_SLIXMPP_RESEND") and not self._resend_sent:
            self._resend_sent = True
            self._deliver_replies([{
                "action": "%s_resend" % body.get("action", "extract_drivers"),
                "sessionid": body.get("sessionid"), "ret": 0, "base64": False,
                "data": {"segment_idx": int(data.get("segment_idx", 0))}}], mto)
            return

        delivered = body
        if is_data and self._corrupt_block and not self._corrupted:
            self._corrupted = True
            delivered = json.loads(json.dumps(body))
            # Bloc volontairement altere : le recepteur doit le refuser.
            delivered["data"]["data_b64"] = base64.b64encode(
                zlib.compress(b"corrompu")).decode()
            delivered["data"]["raw_size"] = len(b"corrompu")
        elif is_data:
            self._data_delivered += 1

        self._deliver_replies(self._receiver.feed(delivered), mto)

    def _deliver_replies(self, replies, mto):
        for reply in replies:
            if self._replies_path:
                with open(self._replies_path, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps(reply, ensure_ascii=False) + "\n")
            if self._ack_mode == "nofinal" and str(reply.get("action", "")).endswith(
                    ("_done", "_ack")):
                continue
            reply = dict(reply)
            if _flag("FAKE_SLIXMPP_DROP_SESSION"):
                reply.pop("sessionid", None)
            message = {"body": json.dumps(reply), "from": _Jid(mto), "type": "chat"}
            spoofed = os.environ.get("FAKE_SLIXMPP_SPOOF_FROM")
            if spoofed:
                # JID usurpe : le transporteur doit refuser cette reponse.
                message["from"] = _Jid(spoofed)
            self._loop.call_soon_threadsafe(self._event, "message", message)

    def _drain_one(self):
        """Simule la boucle d'envoi de slixmpp : get() puis task_done()."""
        if self.waiting_queue.empty():
            return
        try:
            self.waiting_queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        self.waiting_queue.task_done()

    def disconnect(self, wait=2.0, reason=None, ignore_send_queue=False):
        """Retourne un Future deja resolu, comme la version reelle."""
        self._connected = False
        if self._frames_handle is not None:
            self._frames_handle.close()
            self._frames_handle = None
        future = self._loop.create_future()
        self._loop.call_soon(future.set_result, None)
        self._event("disconnected", None)
        return future

    # -- utilitaires -----------------------------------------------------

    def _event(self, name, payload):
        for handler in self._handlers.get(name, []):
            handler(payload)

    def _log(self, message):
        if not _flag("FAKE_SLIXMPP_QUIET"):
            sys.stderr.write("[fake-slixmpp] %s\n" % message)
