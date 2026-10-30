#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_protocol.py - Validation de bout en bout du depot XMPP v2 (hors ligne)
==========================================================================

Execute le VRAI transporteur `Send-DriversOverXmpp.py` dans un processus
dedie, avec `tests/fake_slixmpp.py` a la place de slixmpp, et le VRAI plugin
serveur `server/plugin_extract_drivers.py` a la place du substitut maitre
(via `tests/mock_receiver.py`). Aucun reseau, aucun serveur XMPP, aucune
dependance externe.

Ce qui est verifie :
  * self-test du transporteur ;
  * premier transfert (depot vide) : plan, archive differentielle, depot
    identique a la source, trames conformes au dispatcher ;
  * second passage : "rien a envoyer", aucun bloc emis (code 0) ;
  * envoi differentiel : seuls le package modifie et le certificat nouveau
    partent, le contenu existant du depot est conserve ;
  * reprise apres interruption (dans la meme execution et entre deux
    executions) ;
  * renvoi d'un bloc perdu ou corrompu ;
  * accuse final absent (`required` / `optional`), pas de plan, reponses
    usurpees ou sans session, file d'envoi bloquee ;
  * refus du serveur : aucun nouvel envoi complet ;
  * echecs de connexion / d'authentification, `--check`, STARTTLS ;
  * validation des parametres et du dossier de travail ;
  * resolution du JID (voie agent et voie autonome) ;
  * rejeu d'une capture ; gros transfert (contre-pression) ;
  * plugin serveur : zip-slip, `relative_dir` invalide, package ou certificat
    non demande, empreinte differente de l'inventaire, interdiction de
    supprimer, concordance client/serveur du calcul d'empreinte.

Usage :
    python3 tests/test_protocol.py
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SENDER = os.path.join(ROOT, "Send-DriversOverXmpp.py")
RECEIVER = os.path.join(HERE, "mock_receiver.py")
sys.path.insert(0, HERE)

import mock_receiver  # noqa: E402

OS_DIR = "Windows10"
MANUF = "DellInc"
MODEL = "OptiPlex_7090"
REL = "%s/%s/%s" % (OS_DIR, MANUF, MODEL)

FAILURES: list = []
CHECKS = 0


def check(name: str, condition: bool, detail: str = "") -> bool:
    global CHECKS
    CHECKS += 1
    print("  [%s] %s%s" % ("OK " if condition else "ECHEC", name,
                           (" - " + detail) if detail else ""))
    if not condition:
        FAILURES.append(name)
    return bool(condition)


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_hashes(root: str) -> dict:
    result = {}
    for directory, _dirs, files in os.walk(root):
        for name in files:
            full = os.path.join(directory, name)
            result[os.path.relpath(full, root).replace("\\", "/")] = sha256_file(full)
    return result


def model_tree(depot: str) -> dict:
    """Contenu du dossier modele du depot, sans le fichier de suivi du serveur."""
    tree = tree_hashes(os.path.join(depot, "drivers", *REL.split("/")))
    tree.pop(".extract-metadata.json", None)
    return tree


def staging_tree(staging: str) -> dict:
    return tree_hashes(os.path.join(staging, *REL.split("/")))


# ---------------------------------------------------------------------------
# Jeu de donnees : un dossier de travail comme celui du script PowerShell
# ---------------------------------------------------------------------------

def write_package(staging: str, device_class: str, package: str, files: dict) -> None:
    base = os.path.join(staging, OS_DIR, MANUF, MODEL, "DRIVERS", device_class, package)
    for rel, content in files.items():
        path = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(content)


def write_cert(staging: str, thumbprint: str, content: bytes = None) -> None:
    certs = os.path.join(staging, OS_DIR, MANUF, MODEL, "CERTS")
    os.makedirs(certs, exist_ok=True)
    with open(os.path.join(certs, "%s.cer" % thumbprint), "wb") as handle:
        handle.write(content if content is not None else b"0\x82\x01\x00" + os.urandom(64))


def write_metadata(staging: str) -> dict:
    metadata = {
        "schema": "medulla.extractdrivers.v2",
        "collected_at": "2026-10-10T18:30:00Z",
        "hostname": "PC-TEST-001",
        "os": OS_DIR,
        "os_caption": "Microsoft Windows 10 Pro",
        "manufacturer": "Dell Inc.",
        "manufacturer_dir": MANUF,
        "model": "OptiPlex 7090",
        "model_dir": MODEL,
        "serial": "ABC1234",
        "relative_dir": REL,
        "depot_subdir": "drivers",
        "extract_method": "pnp",
        "drivers_count": 3,
        "certs_count": 2,
    }
    os.makedirs(staging, exist_ok=True)
    with open(os.path.join(staging, "metadata.json"), "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, ensure_ascii=False, indent=2)
    return metadata


def build_staging(staging: str, blob_size: int = 120000) -> dict:
    """3 packages (dont un avec sous-dossier) et 2 certificats."""
    write_package(staging, "Net", "netrtl8111", {
        "rtl8111.inf": b"[Version]\nClass=Net\n", "rtl8111.sys": os.urandom(blob_size)})
    write_package(staging, "Media", "hdaudio", {
        "hdaudio.inf": b"[Version]\nClass=Media\n", "hdaudio.sys": os.urandom(blob_size)})
    write_package(staging, "Display", "gfx", {
        "gfx.inf": b"[Version]\nClass=Display\n", "bin/gfx.dll": os.urandom(5000)})
    write_cert(staging, "AABBCCDDEEFF00112233")
    write_cert(staging, "00112233445566778899")
    return write_metadata(staging)


def sender_args(workdir: str, staging: str, name: str, extra: list = None) -> list:
    args = [
        "--staging", staging,
        "--metadata", os.path.join(staging, "metadata.json"),
        "--delta-zip", os.path.join(workdir, "delta_%s.zip" % name),
        "--ack-mode", "required",
        "--plan-timeout", "15",
        "--resume-timeout", "15",
        "--ack-timeout", "15",
        "--max-retries", "1",
        "--retry-delay", "1",
    ]
    return args + (extra or [])


def write_config(path: str) -> None:
    """agentconf.ini minimal, suffisant pour la resolution autonome du JID."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(
            "[global]\n"
            "log_level = INFO\n"
            "\n"
            "[configuration_server]\n"
            "confserver = 127.0.0.1\n"
            "confport = 5222\n"
            "confpassword = motdepasse-de-test\n"
            "confdomain = pulse\n"
            "keyAES32 = 0123456789abcdef0123456789abcdef\n"
            "\n"
            "[chat]\n"
            "domain = pulse\n"
            "\n"
            "[connection]\n"
            "server = 127.0.0.1\n"
            "port = 5222\n"
            "password = motdepasse-de-test\n"
            "\n"
            "[substitute]\n"
            "registration = master_reg@pulse\n"
        )


# ---------------------------------------------------------------------------
# Execution du transporteur
# ---------------------------------------------------------------------------

def run_sender(workdir: str, args: list, env_extra: dict,
               with_config: bool = True) -> tuple:
    """
    Lance le transporteur dans un processus separe, avec le faux slixmpp.

    Retourne (code_de_sortie, resultat_json, sortie_combinee).
    """
    result_path = os.path.join(workdir, "result.json")
    if os.path.exists(result_path):
        os.remove(result_path)

    environment = dict(os.environ)
    environment.update({
        # fake_modules/ EN PREMIER : `import slixmpp` et `import
        # pulse_xmpp_agent` doivent resoudre vers les faux paquets.
        "PYTHONPATH": os.pathsep.join(
            [os.path.join(HERE, "fake_modules"), HERE,
             environment.get("PYTHONPATH", "")]),
        "PYTHONIOENCODING": "utf-8",
        "FAKE_SLIXMPP_DEPOT": env_extra.get("depot", os.path.join(workdir, "depot")),
        "FAKE_SLIXMPP_QUIET": "1",
    })
    for key, value in env_extra.items():
        if key != "depot":
            environment[key] = value
    if "inexistant" not in environment["FAKE_SLIXMPP_DEPOT"]:
        os.makedirs(environment["FAKE_SLIXMPP_DEPOT"], exist_ok=True)

    command = [sys.executable, SENDER, "--result", result_path]
    if with_config:
        command += ["--config", os.path.join(workdir, "agentconf.ini"),
                    "--config-source", "minimal"]
    command += args

    completed = subprocess.run(command, capture_output=True, text=True,
                               env=environment, cwd=workdir, timeout=180)

    payload = {}
    if os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    return completed.returncode, payload, (completed.stdout or "") + (completed.stderr or "")


def dump_entries(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def dump_sessions(path: str) -> set:
    return {entry["body"]["sessionid"] for entry in dump_entries(path)
            if "sessionid" in entry.get("body", {})}


def scenario_jid_via_agent(workdir: str) -> None:
    print("\nResolution du JID par la voie de l'agent (--)")
    depot = os.path.join(workdir, "depot_jid")
    environment = {"depot": depot}

    # Sans --config-source : le transporteur doit interroger le paquet
    # pulse_xmpp_agent (ici son substitut de test) et reprendre son JID.
    result_path = os.path.join(workdir, "result.json")
    command = [sys.executable, SENDER, "--result", result_path,
               "--config", os.path.join(workdir, "agentconf.ini"),
               "--config-source", "agent", "--check"]
    environment.update({
        "PYTHONPATH": os.pathsep.join(
            [os.path.join(HERE, "fake_modules"), HERE]),
        "PYTHONIOENCODING": "utf-8",
        "FAKE_SLIXMPP_DEPOT": depot,
        "FAKE_SLIXMPP_QUIET": "1",
    })
    completed = subprocess.run(command, capture_output=True, text=True,
                               env={**os.environ, **environment}, cwd=workdir,
                               timeout=120)
    payload = {}
    if os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

    check("JID via l'agent : code de sortie 0", completed.returncode == 0,
          "code %s - %s" % (completed.returncode, payload.get("error")))
    check("JID via l'agent : partie bare celle de l'agent",
          str(payload.get("jid", "")).startswith("pc-stub.7zz@pulse/"),
          str(payload.get("jid")))
    check("JID via l'agent : ressource propre au transporteur",
          "extractdrivers" in str(payload.get("jid", "")),
          str(payload.get("jid")))


def scenario_jid_minimal(workdir: str) -> None:
    print("\nSuffixe de JID lu dans INFOSTMP/JIDSUFFIXE (voie autonome)")
    # Second faux paquet, avec un suffixe DIFFERENT : si le transporteur lit
    # bien le fichier, le JID doit contenir ce suffixe.
    alt = os.path.join(workdir, "alt_modules")
    alt_pkg = os.path.join(alt, "pulse_xmpp_agent")
    os.makedirs(os.path.join(alt_pkg, "lib", "INFOSTMP"), exist_ok=True)
    for path in (os.path.join(alt_pkg, "__init__.py"),
                 os.path.join(alt_pkg, "lib", "__init__.py")):
        open(path, "w").close()
    with open(os.path.join(alt_pkg, "lib", "INFOSTMP", "JIDSUFFIXE"), "w") as handle:
        handle.write("ZZZ")

    result_path = os.path.join(workdir, "result_jidmin.json")
    environment = {
        "PYTHONPATH": os.pathsep.join([alt, os.path.join(HERE, "fake_modules"), HERE]),
        "PYTHONIOENCODING": "utf-8",
        "FAKE_SLIXMPP_DEPOT": os.path.join(workdir, "depot_jidmin"),
        "FAKE_SLIXMPP_QUIET": "1",
    }
    command = [sys.executable, SENDER,
               "--config", os.path.join(workdir, "agentconf.ini"),
               "--config-source", "minimal", "--check",
               "--result", result_path]
    completed = subprocess.run(command, capture_output=True, text=True,
                               env={**os.environ, **environment}, cwd=workdir,
                               timeout=120)
    payload = {}
    if os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

    check("JID autonome : code de sortie 0", completed.returncode == 0,
          "code %s - %s" % (completed.returncode, payload.get("error")))
    check("JID autonome : suffixe JIDSUFFIXE reellement lu (ZZZ)",
          ".ZZZ@" in str(payload.get("jid", "")), str(payload.get("jid")))


# ---------------------------------------------------------------------------
# Outils d'analyse des trames
# ---------------------------------------------------------------------------

def logical_frames(entries: list) -> list:
    """Trames logiques : les tranches big_data sont reassemblees comme le fait le serveur."""
    result, pending = [], {}
    for entry in entries:
        body = entry["body"]
        if body.get("action") == "big_data":
            bucket = pending.setdefault(body["sessionid"], {})
            bucket[int(body["data"]["nb_segment"])] = body["data"]["segment"]
            if len(bucket) == int(body["data"]["nb_segment_total"]):
                joined = "".join(bucket[i] for i in sorted(bucket))
                result.append(json.loads(zlib.decompress(base64.b64decode(joined))))
                del pending[body["sessionid"]]
        else:
            result.append(body)
    return result


def frames_of_type(frames: list, kind: str) -> list:
    return [f for f in frames if (f.get("data") or {}).get("type") == kind]


def replies_of(path: str) -> list:
    return dump_entries(path)


# ---------------------------------------------------------------------------
# Scenarios du transporteur
# ---------------------------------------------------------------------------

def scenario_self_test() -> None:
    print("\nSelf-test interne du transporteur (--self-test)")
    completed = subprocess.run([sys.executable, SENDER, "--self-test"],
                               capture_output=True, text=True, timeout=120)
    check("self-test retourne 0", completed.returncode == 0, "code %s" % completed.returncode)
    check("self-test annonce OK", "Self-test : OK" in completed.stdout)


def scenario_first_transfer(workdir: str, staging: str) -> str:
    print("\nPremier transfert (depot vide) : plan, archive differentielle, depot")
    depot = os.path.join(workdir, "depot_main")
    wire = os.path.join(workdir, "wire_first.jsonl")
    dump = os.path.join(workdir, "dump_first.jsonl")
    delta = os.path.join(workdir, "delta_first.zip")
    code, payload, output = run_sender(workdir, sender_args(workdir, staging, "first", [
        "--dump-frames", dump]), {"depot": depot, "FAKE_SLIXMPP_FRAMES": wire})
    detail = "code %s - %s" % (code, payload.get("error") or output.strip()[-300:])

    check("code de sortie 0", code == 0, detail)
    check("statut ok et accuse recu", payload.get("status") == "ok"
          and payload.get("confirmed") is True, str(payload.get("status")))
    check("rien-a-envoyer = faux", payload.get("nothing_to_send") is False)
    check("3 packages et 2 certificats envoyes",
          (payload.get("packages_sent"), payload.get("certs_sent")) == (3, 2),
          "%s/%s" % (payload.get("packages_sent"), payload.get("certs_sent")))
    check("aucun element deja present", (payload.get("packages_skipped"),
          payload.get("certs_skipped")) == (0, 0))
    check("relative_dir remonte", payload.get("relative_dir") == REL,
          str(payload.get("relative_dir")))
    check("contenu du depot identique a la source",
          model_tree(depot) == staging_tree(staging),
          str(sorted(set(model_tree(depot)) ^ set(staging_tree(staging)))[:5]))
    check("fichier de suivi du serveur ecrit",
          os.path.isfile(os.path.join(depot, "drivers", *REL.split("/"),
                                      ".extract-metadata.json")))
    check("aucun reste de transfert dans .incoming",
          not [n for n in os.listdir(os.path.join(depot, "drivers", ".incoming"))
               if n.endswith((".part", ".json", ".x"))])
    check("archive differentielle supprimee apres succes", not os.path.exists(delta))

    wire_entries = dump_entries(wire)
    check("toutes les trames sont de type chat vers master@pulse",
          bool(wire_entries) and all(e.get("type") == "chat" and e.get("to") == "master@pulse"
                                     for e in wire_entries))
    check("une seule session de transfert", len(dump_sessions(wire)) == 1,
          str(sorted(dump_sessions(wire))))
    frames = logical_frames(wire_entries)
    kinds = [(f.get("data") or {}).get("type") for f in frames]
    check("sequence : inventory, meta, data...", kinds[:2] == ["inventory", "meta"]
          and set(kinds[2:]) == {"data"}, str(kinds[:4]))
    data = frames_of_type(frames, "data")
    check("blocs numerotes 0..N-1", [f["data"]["segment_idx"] for f in data]
          == list(range(len(data))), "%d blocs" % len(data))
    check("dernier bloc marque last avec les empreintes globales",
          data[-1]["data"].get("last") is True and "sha256_total" in data[-1]["data"])
    meta = frames_of_type(frames, "meta")[0]["data"]
    check("meta : delta, schema v2, sha256 coherent avec le resultat",
          meta.get("delta") is True and meta.get("schema") == "medulla.extractdrivers.v2"
          and meta.get("sha256") == payload.get("archive", {}).get("sha256"))
    inventory = frames_of_type(frames, "inventory")[0]["data"]
    check("inventaire : 3 packages DRIVERS/<classe>/<package> et 2 certificats",
          sorted(p["id"] for p in inventory["packages"]) ==
          ["DRIVERS/Display/gfx", "DRIVERS/Media/hdaudio", "DRIVERS/Net/netrtl8111"]
          and len(inventory["certs"]) == 2)
    check("l'inventaire ne contient aucun contenu de fichier",
          "archive_b64" not in json.dumps(inventory)
          and len(json.dumps(inventory)) < 4000)
    return depot


def scenario_nothing_to_send(workdir: str, staging: str, depot: str) -> None:
    print("\nSecond passage : depot deja a jour, rien a envoyer")
    wire = os.path.join(workdir, "wire_again.jsonl")
    before = tree_hashes(depot)
    code, payload, output = run_sender(workdir, sender_args(workdir, staging, "again"),
                                       {"depot": depot, "FAKE_SLIXMPP_FRAMES": wire})
    check("code de sortie 0", code == 0, "code %s - %s" % (code, payload.get("error")))
    check("nothing_to_send = vrai", payload.get("nothing_to_send") is True)
    check("statut ok, confirme par le serveur", payload.get("status") == "ok"
          and payload.get("confirmed") is True)
    check("3 packages et 2 certificats deja presents",
          (payload.get("packages_skipped"), payload.get("certs_skipped")) == (3, 2))
    kinds = [(f.get("data") or {}).get("type")
             for f in logical_frames(dump_entries(wire))]
    check("seul l'inventaire est emis (ni meta ni bloc)", kinds == ["inventory"], str(kinds))
    check("archive jamais construite",
          not os.path.exists(os.path.join(workdir, "delta_again.zip")))
    after = tree_hashes(depot)
    changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
    check("depot strictement inchange", not changed, str(sorted(changed)[:3]))


def scenario_differential(workdir: str, staging: str, depot: str) -> None:
    print("\nEnvoi differentiel : package modifie + certificat nouveau, depot conserve")
    # Un autre poste du meme modele a depose un package que celui-ci n'a pas.
    foreign = os.path.join(depot, "drivers", *REL.split("/"), "DRIVERS", "Net", "autre_poste")
    os.makedirs(foreign, exist_ok=True)
    with open(os.path.join(foreign, "autre.inf"), "wb") as handle:
        handle.write(b"autre poste")

    stage2 = os.path.join(workdir, "staging_diff")
    shutil.copytree(staging, stage2)
    write_package(stage2, "Media", "hdaudio", {"hdaudio.inf": b"[Version]\nClass=Media\nv2\n"})
    # (hdaudio.sys d'origine est conserve ; l'INF change : package different)
    write_cert(stage2, "FFEEDDCCBBAA99887766")
    write_metadata(stage2)

    wire = os.path.join(workdir, "wire_diff.jsonl")
    code, payload, output = run_sender(workdir, sender_args(workdir, stage2, "diff"),
                                       {"depot": depot, "FAKE_SLIXMPP_FRAMES": wire})
    check("code de sortie 0", code == 0, "code %s - %s" % (code, payload.get("error")))
    check("1 package et 1 certificat envoyes",
          (payload.get("packages_sent"), payload.get("certs_sent")) == (1, 1),
          "%s/%s" % (payload.get("packages_sent"), payload.get("certs_sent")))
    check("2 packages et 2 certificats ignores",
          (payload.get("packages_skipped"), payload.get("certs_skipped")) == (2, 2),
          "%s/%s" % (payload.get("packages_skipped"), payload.get("certs_skipped")))
    first = len(frames_of_type(logical_frames(dump_entries(
        os.path.join(workdir, "wire_first.jsonl"))), "data"))
    now = len(frames_of_type(logical_frames(dump_entries(wire)), "data"))
    check("beaucoup moins de blocs que le premier envoi", now < first,
          "%d blocs contre %d" % (now, first))
    expected = staging_tree(stage2)
    got = model_tree(depot)
    extra = {k for k in got if k not in expected}
    check("depot = nouvelle source, a l'exception du fichier d'un autre poste",
          all(got.get(k) == v for k, v in expected.items())
          and extra == {"DRIVERS/Net/autre_poste/autre.inf"}, str(sorted(extra)))
    check("le fichier d'un autre poste n'a pas ete supprime", os.path.isfile(
        os.path.join(foreign, "autre.inf")))


def scenario_resume_same_run(workdir: str, staging: str) -> None:
    print("\nReprise apres coupure, dans la meme execution (nouvelle tentative)")
    depot = os.path.join(workdir, "depot_cut1")
    wire = os.path.join(workdir, "wire_cut1.jsonl")
    mark = os.path.join(workdir, "mark_cut1")
    code, payload, output = run_sender(workdir, sender_args(workdir, staging, "cut1", [
        "--segment-bytes", "2048", "--max-retries", "2"]),
        {"depot": depot, "FAKE_SLIXMPP_FRAMES": wire,
         "FAKE_SLIXMPP_CUT_AFTER": "60", "FAKE_SLIXMPP_CUT_MARK": mark})
    check("code de sortie 0 apres reprise", code == 0,
          "code %s - %s" % (code, payload.get("error") or output.strip()[-300:]))
    check("la coupure a bien eu lieu", os.path.exists(mark))
    check("depot identique a la source", model_tree(depot) == staging_tree(staging))
    resumed = payload.get("resumed_from_block")
    check("reprise a un bloc > 0 (point de controle serveur)",
          isinstance(resumed, int) and 0 < resumed <= 60, str(resumed))
    frames = logical_frames(dump_entries(wire))
    sessions = []
    for f in frames:
        if f["sessionid"] not in sessions:
            sessions.append(f["sessionid"])
    check("deux sessions (une par tentative)", len(sessions) == 2, str(sessions))
    second = [f["data"]["segment_idx"] for f in frames_of_type(frames, "data")
              if f["sessionid"] == sessions[-1]]
    total = frames_of_type(frames, "meta")[0]["data"]["segment_total"]
    check("la seconde tentative n'envoie que la fin de l'archive",
          bool(second) and min(second) == resumed and len(second) == total - resumed,
          "%d blocs, du %s au %s / total %d" % (len(second), min(second or [0]),
                                                max(second or [0]), total))


def scenario_resume_across_runs(workdir: str, staging: str) -> None:
    print("\nReprise apres coupure, entre deux executions du script")
    depot = os.path.join(workdir, "depot_cut2")
    mark = os.path.join(workdir, "mark_cut2")
    env = {"depot": depot, "FAKE_SLIXMPP_CUT_AFTER": "60", "FAKE_SLIXMPP_CUT_MARK": mark}
    args = sender_args(workdir, staging, "cut2", ["--segment-bytes", "2048"])
    code, payload, _ = run_sender(workdir, args, env)
    check("premiere execution : echec de transfert (code 5)", code == 5, "code %s" % code)
    check("premiere execution : archive conservee pour analyse",
          os.path.exists(os.path.join(workdir, "delta_cut2.zip")))
    check("premiere execution : rien n'est installe dans le depot",
          not os.path.isdir(os.path.join(depot, "drivers", *REL.split("/"))))
    parts = [n for n in os.listdir(os.path.join(depot, "drivers", ".incoming"))
             if n.endswith(".part")]
    check("premiere execution : fichier partiel conserve par le serveur", len(parts) == 1,
          str(parts))

    code, payload, output = run_sender(workdir, args, env)
    check("seconde execution : code 0", code == 0,
          "code %s - %s" % (code, payload.get("error") or output.strip()[-300:]))
    resumed = payload.get("resumed_from_block")
    check("seconde execution : reprise au point de controle", isinstance(resumed, int)
          and resumed > 0, str(resumed))
    check("seconde execution : depot identique a la source",
          model_tree(depot) == staging_tree(staging))
    check("seconde execution : fichier partiel nettoye",
          not [n for n in os.listdir(os.path.join(depot, "drivers", ".incoming"))
               if n.endswith(".part")])


def scenario_resend(workdir: str, staging: str) -> None:
    print("\nBloc perdu puis bloc corrompu : renvoi demande par le serveur")
    for label, flag in (("perdu", "FAKE_SLIXMPP_RESEND"), ("corrompu", "FAKE_SLIXMPP_CORRUPT_BLOCK")):
        depot = os.path.join(workdir, "depot_resend_%s" % label)
        wire = os.path.join(workdir, "wire_resend_%s.jsonl" % label)
        replies = os.path.join(workdir, "replies_resend_%s.jsonl" % label)
        code, payload, _ = run_sender(workdir, sender_args(workdir, staging, "rs_" + label),
                                      {"depot": depot, "FAKE_SLIXMPP_FRAMES": wire,
                                       "FAKE_SLIXMPP_REPLIES": replies, flag: "1"})
        check("bloc %s : code 0" % label, code == 0,
              "code %s - %s" % (code, payload.get("error")))
        asked = [r for r in replies_of(replies) if r["action"].endswith("_resend")]
        check("bloc %s : le serveur a demande un renvoi" % label, len(asked) == 1,
              "%d demandes" % len(asked))
        first = [f for f in frames_of_type(logical_frames(dump_entries(wire)), "data")
                 if f["data"]["segment_idx"] == (asked[0]["data"]["segment_idx"] if asked else -1)]
        check("bloc %s : le bloc a ete emis deux fois" % label, len(first) == 2,
              "%d emissions" % len(first))
        check("bloc %s : depot conforme" % label, model_tree(depot) == staging_tree(staging))


def scenario_no_final_ack(workdir: str, staging: str) -> None:
    print("\nAccuse final absent (le plan et la reprise fonctionnent)")
    for mode, expected_code, expected_status in (("required", 5, "error"),
                                                 ("optional", 0, "unconfirmed")):
        depot = os.path.join(workdir, "depot_nofinal_%s" % mode)
        wire = os.path.join(workdir, "wire_nofinal_%s.jsonl" % mode)
        args = sender_args(workdir, staging, "nf_" + mode)
        args[args.index("--ack-mode") + 1] = mode
        args[args.index("--ack-timeout") + 1] = "2"
        args += ["--max-retries", "3"]
        code, payload, _ = run_sender(workdir, args, {
            "depot": depot, "FAKE_SLIXMPP_FRAMES": wire, "FAKE_SLIXMPP_ACK": "nofinal"})
        check("%s : code de sortie %d" % (mode, expected_code), code == expected_code,
              "code %s" % code)
        check("%s : statut %s, confirmed=false" % (mode, expected_status),
              payload.get("status") == expected_status and payload.get("confirmed") is False,
              str(payload.get("status")))
        check("%s : aucun nouvel envoi complet" % mode, len(dump_sessions(wire)) == 1,
              "%d sessions" % len(dump_sessions(wire)))


def scenario_no_plan(workdir: str, staging: str) -> None:
    print("\nServeur muet : pas de plan -> echec explicite, sans nouvel envoi")
    wire = os.path.join(workdir, "wire_noplan.jsonl")
    args = sender_args(workdir, staging, "np", ["--max-retries", "3"])
    args[args.index("--plan-timeout") + 1] = "2"
    code, payload, _ = run_sender(workdir, args, {
        "depot": os.path.join(workdir, "depot_noplan"), "FAKE_SLIXMPP_ACK": "none",
        "FAKE_SLIXMPP_FRAMES": wire})
    check("code de sortie 5", code == 5, "code %s" % code)
    check("message : aucune reponse a l'inventaire", "inventaire" in (payload.get("error") or "").lower(),
          str(payload.get("error")))
    check("echec non transitoire : une seule session malgre --max-retries 3",
          len(dump_sessions(wire)) == 1, "%d sessions" % len(dump_sessions(wire)))
    check("seul l'inventaire a ete emis", [
        (f.get("data") or {}).get("type") for f in logical_frames(dump_entries(wire))]
        == ["inventory"])


def scenario_untrusted_replies(workdir: str, staging: str) -> None:
    print("\nReponses non fiables : emetteur usurpe / sans sessionid -> ignorees")
    for label, env in (("emetteur usurpe", {"FAKE_SLIXMPP_SPOOF_FROM": "attaquant@pulse/evil"}),
                       ("sans sessionid", {"FAKE_SLIXMPP_DROP_SESSION": "1"})):
        args = sender_args(workdir, staging, "ut")
        args[args.index("--plan-timeout") + 1] = "2"
        e = {"depot": os.path.join(workdir, "depot_ut")}
        e.update(env)
        code, payload, _ = run_sender(workdir, args, e)
        check("%s : ignore (code 5, pas de plan)" % label, code == 5, "code %s" % code)
        check("%s : confirmed=false" % label, payload.get("confirmed") is False)


def scenario_server_refusal(workdir: str, staging: str) -> None:
    print("\nRefus du serveur (depot absent) : message remonte, aucun nouvel envoi")
    wire = os.path.join(workdir, "wire_refusal.jsonl")
    code, payload, _ = run_sender(workdir, sender_args(workdir, staging, "rf", [
        "--max-retries", "3"]), {
        "depot": os.path.join(workdir, "depot_inexistant"), "FAKE_SLIXMPP_FRAMES": wire})
    check("code de sortie 5", code == 5, "code %s" % code)
    check("message du serveur remonte", "depot" in (payload.get("error") or "").lower(),
          str(payload.get("error")))
    check("retryable=false", payload.get("retryable") is not True)
    check("une seule session malgre --max-retries 3", len(dump_sessions(wire)) == 1)


def scenario_stuck_queue(workdir: str, staging: str) -> None:
    print("\nFile d'envoi jamais videe : echec explicite, pas un faux succes")
    args = sender_args(workdir, staging, "sq")
    args[args.index("--ack-mode") + 1] = "none"
    args[args.index("--ack-timeout") + 1] = "6"
    code, payload, _ = run_sender(workdir, args, {
        "depot": os.path.join(workdir, "depot_stuck"), "FAKE_SLIXMPP_SLOW_QUEUE": "1"})
    check("code de sortie 5", code == 5, "code %s" % code)
    check("statut error", payload.get("status") == "error", str(payload.get("status")))
    check("message sur la file d'envoi", "file d'envoi" in (payload.get("error") or ""),
          str(payload.get("error")))


def scenario_connection(workdir: str, staging: str) -> None:
    print("\nEchecs de connexion/authentification, --check et STARTTLS")
    for label, mode in (("authentification", "auth"), ("connexion", "connect")):
        code, payload, _ = run_sender(workdir, sender_args(workdir, staging, "cx"), {
            "depot": os.path.join(workdir, "depot_" + mode), "FAKE_SLIXMPP_FAIL": mode})
        check("%s en echec : code 3" % label, code == 3, "code %s" % code)
    code, payload, _ = run_sender(workdir, ["--check"],
                                  {"depot": os.path.join(workdir, "depot_check")})
    check("--check : code 0, aucune trame emise", code == 0 and payload.get("frames_sent") == 0,
          "code %s" % code)
    code, payload, _ = run_sender(workdir, ["--check", "--require-starttls"],
                                  {"depot": os.path.join(workdir, "depot_tls_ko")})
    check("--require-starttls sans TLS : code 3", code == 3 and "starttls" in
          (payload.get("error") or "").lower(), "code %s" % code)
    code, payload, _ = run_sender(workdir, ["--check", "--require-starttls"],
                                  {"depot": os.path.join(workdir, "depot_tls_ok"),
                                   "FAKE_SLIXMPP_TLS": "1"})
    check("--require-starttls avec TLS : code 0", code == 0, "code %s" % code)


def scenario_parameters(workdir: str, staging: str) -> None:
    print("\nValidation des parametres et du dossier de travail (code 2)")
    env = {"depot": os.path.join(workdir, "depot_param")}
    for value in ("0", "-1", "999999", "abc"):
        code, _, _ = run_sender(workdir, sender_args(workdir, staging, "pm", [
            "--segment-bytes", value]), env)
        check("--segment-bytes %s refuse (code 2)" % value, code == 2, "code %s" % code)

    code, payload, _ = run_sender(workdir, sender_args(
        workdir, os.path.join(workdir, "inexistant"), "pm"), env)
    check("dossier de travail absent : code 2", code == 2, "code %s" % code)

    empty = os.path.join(workdir, "staging_vide")
    write_metadata(empty)
    code, payload, _ = run_sender(workdir, sender_args(workdir, empty, "pm"), env)
    check("dossier sans driver ni certificat : code 2", code == 2, "code %s" % code)

    bad = os.path.join(workdir, "staging_bad_rel")
    build_staging(bad, blob_size=100)
    meta_path = os.path.join(bad, "metadata.json")
    meta = json.load(open(meta_path, encoding="utf-8"))
    meta["relative_dir"] = "../../etc/passwd"
    json.dump(meta, open(meta_path, "w", encoding="utf-8"))
    code, payload, _ = run_sender(workdir, sender_args(workdir, bad, "pm"), env)
    check("relative_dir dangereux refuse cote client : code 2", code == 2, "code %s" % code)

    odd = os.path.join(workdir, "staging_odd_names")
    build_staging(odd, blob_size=100)
    write_package(odd, "Net", "ok_pkg", {"a.inf": b"x"})
    open(os.path.join(odd, OS_DIR, MANUF, MODEL, "DRIVERS", "Net", "ok_pkg", "bad?name.inf"),
         "wb").close() if os.name != "nt" else None
    depot = os.path.join(workdir, "depot_odd")
    code, payload, _ = run_sender(workdir, sender_args(workdir, odd, "odd"), {"depot": depot})
    check("nom de fichier invalide exclu sans faire echouer l'envoi", code == 0,
          "code %s - %s" % (code, payload.get("error")))
    check("le package au nom invalide n'est pas depose", not os.path.isdir(
        os.path.join(depot, "drivers", *REL.split("/"), "DRIVERS", "Net", "ok_pkg"))
        or not os.path.exists(os.path.join(depot, "drivers", *REL.split("/"), "DRIVERS",
                                           "Net", "ok_pkg", "bad?name.inf")))


def scenario_replay(workdir: str, staging: str) -> None:
    print("\nRejeu d'une capture de trames (mock_receiver --frames)")
    frames = os.path.join(workdir, "frames_replay.jsonl")
    depot_emit = os.path.join(workdir, "depot_emit")
    depot_replay = os.path.join(workdir, "depot_replay")
    code, _, _ = run_sender(workdir, sender_args(workdir, staging, "rp", [
        "--dump-frames", frames]), {"depot": depot_emit})
    check("transfert initial OK", code == 0, "code %s" % code)
    completed = subprocess.run(
        [sys.executable, RECEIVER, "--frames", frames, "--depot", depot_replay],
        capture_output=True, text=True, timeout=120)
    check("mock_receiver retourne 0", completed.returncode == 0,
          (completed.stdout + completed.stderr).strip()[-300:])
    check("depot rejoue identique au depot du transfert direct",
          model_tree(depot_replay) == model_tree(depot_emit))

    depot_flat = os.path.join(workdir, "depot_flat")
    os.makedirs(depot_flat, exist_ok=True)
    flat = mock_receiver.Receiver(depot_flat)
    flat.plugin.DEPOT_SUBDIR = ""
    answers = []
    with open(frames, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                answers += flat.feed(json.loads(line)["body"])
    check("sous-dossier vide : transfert accepte",
          any(a["action"].endswith("_done") for a in answers)
          and not any(a["action"].endswith("_error") for a in answers))
    check("sous-dossier vide : modele directement sous la racine",
          os.path.isdir(os.path.join(depot_flat, "Windows10", "DellInc", "OptiPlex_7090", "DRIVERS"))
          and not os.path.exists(os.path.join(depot_flat, "drivers")))
    flat.plugin.DEPOT_SUBDIR = "../hors"
    try:
        flat.plugin.depot_base()
        refused = False
    except flat.plugin.PluginError:
        refused = True
    check("sous-dossier avec .. : refuse", refused)


def scenario_concurrent_blocks(workdir: str, staging: str) -> None:
    print("\nBlocs recus en parallele (substitut multi-thread)")
    from concurrent.futures import ThreadPoolExecutor
    sys.path.insert(0, HERE)
    import mock_receiver
    frames = os.path.join(workdir, "frames_conc.jsonl")
    depot_seq = os.path.join(workdir, "depot_conc_seq")
    depot_par = os.path.join(workdir, "depot_conc_par")
    code, _, _ = run_sender(workdir, sender_args(workdir, staging, "conc", [
        "--dump-frames", frames, "--segment-bytes", "1024"]), {"depot": depot_seq})
    check("capture initiale OK", code == 0, "code %s" % code)
    bodies = []
    with open(frames, "r", encoding="utf-8") as handle:
        bodies = [json.loads(line)["body"] for line in handle if line.strip()]
    data = [b for b in bodies if b.get("action") == "extract_drivers"
            and b["data"].get("type") == "data"]
    head = [b for b in bodies if b not in data]
    check("capture avec beaucoup de blocs (> 80)", len(data) > 80, "%d" % len(data))

    os.makedirs(depot_par, exist_ok=True)
    receiver = mock_receiver.Receiver(depot_par)
    for body in head:
        receiver.feed(body)
    errors = []

    # Ecriture d'etat lente : force le chevauchement des ecritures concurrentes
    # (c'est ce qui provoquait FileNotFoundError sur le .json.tmp partage).
    real_json = receiver.plugin.json

    class SlowJson:
        def __getattr__(self, name):
            return getattr(real_json, name)

        @staticmethod
        def dump(*args, **kwargs):
            real_json.dump(*args, **kwargs)
            time.sleep(0.02)

    receiver.plugin.json = SlowJson()

    def push(body):
        try:
            receiver.feed(body)
        except Exception as exc:  # noqa: BLE001
            errors.append(repr(exc))

    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(push, data))
    check("aucune exception en reception parallele", not errors, "; ".join(errors[:2]))
    refusals = [m["body"]["data"].get("message") for m in receiver.xmpp.outbox
                if m["body"]["action"].endswith("_error")]
    check("aucune reponse d'erreur du plugin", not refusals, "; ".join(map(str, refusals[:2])))
    finals = [m["body"] for m in receiver.xmpp.outbox
              if m["body"]["action"].endswith("_done")
              and m["body"]["data"].get("packages_received") is not None]
    check("une seule finalisation", len(finals) == 1, "%d" % len(finals))
    check("depot identique au transfert sequentiel",
          model_tree(depot_par) == model_tree(depot_seq))


def scenario_backpressure(workdir: str) -> None:
    print("\nGros transfert : contre-pression sur plusieurs lots de la file")
    staging = os.path.join(workdir, "staging_gros")
    write_package(staging, "Net", "gros", {"gros.sys": os.urandom(8 * 1024 * 1024)})
    write_metadata(staging)
    depot = os.path.join(workdir, "depot_bp")
    started = time.time()
    code, payload, _ = run_sender(workdir, sender_args(workdir, staging, "bp", [
        "--ack-timeout", "60"]), {"depot": depot})
    duration = time.time() - started
    check("code de sortie 0", code == 0, "code %s - %s" % (code, payload.get("error")))
    check("plus de 200 trames emises", (payload.get("frames_sent") or 0) > 200,
          "%s trames" % payload.get("frames_sent"))
    check("depot conforme", model_tree(depot) == staging_tree(staging))
    check("duree raisonnable (< 120 s)", duration < 120, "%.1f s" % duration)


# ---------------------------------------------------------------------------
# Scenarios du plugin serveur (appel direct, trames fabriquees a la main)
# ---------------------------------------------------------------------------

def load_sender_module():
    spec = importlib.util.spec_from_file_location("sender_under_test", SENDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Crafted:
    """Pilote le plugin avec des trames fabriquees (client malveillant ou defaillant)."""

    def __init__(self, depot: str, sid: str = "drivers_crafted_1"):
        os.makedirs(depot, exist_ok=True)
        self.depot = depot
        self.sid = sid
        self.receiver = mock_receiver.Receiver(depot)
        self.plugin = self.receiver.plugin
        self.replies: list = []

    def send(self, data: dict) -> list:
        body = {"action": "extract_drivers", "sessionid": self.sid, "ret": 0,
                "base64": False, "data": data}
        out = self.receiver.feed(body)
        self.replies.extend(out)
        return out

    def last(self) -> dict:
        return self.replies[-1] if self.replies else {}

    def is_error(self) -> bool:
        return str(self.last().get("action", "")).endswith("_error")

    def message(self) -> str:
        return str((self.last().get("data") or {}).get("message", ""))

    def run(self, relative_dir: str, packages: list, certs: list, entries: list,
            segment: int = 25000) -> None:
        self.send({"type": "inventory", "schema": "medulla.extractdrivers.v2",
                   "metadata": {"relative_dir": relative_dir},
                   "packages": packages, "certs": certs})
        if self.is_error() or not str(self.last().get("action", "")).endswith("_plan"):
            return
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, content in entries:
                zf.writestr(name, content)
        raw = buffer.getvalue()
        total = max(1, (len(raw) + segment - 1) // segment)
        self.send({"type": "meta", "schema": "medulla.extractdrivers.v2", "delta": True,
                   "size": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                   "sha256": hashlib.sha256(raw).hexdigest(), "segment_bytes": segment,
                   "segment_total": total, "unpacked_size": sum(len(c) for _, c in entries),
                   "filename": "x.zip", "packages": len(packages), "certs": len(certs),
                   "metadata": {"relative_dir": relative_dir}})
        if self.is_error():
            return
        for index in range(total):
            block = raw[index * segment:(index + 1) * segment]
            self.send({"type": "data", "segment_idx": index, "segment_total": total,
                       "raw_size": len(block), "md5_segment": hashlib.md5(block).hexdigest(),
                       "data_b64": base64.b64encode(zlib.compress(block)).decode(),
                       "last": index == total - 1})
            if self.is_error():
                return


def package_entry(plugin, workdir: str, name: str, files: dict) -> dict:
    """Fabrique un package source et retourne l'entree d'inventaire correcte."""
    root = os.path.join(workdir, "craft_src_" + name)
    shutil.rmtree(root, ignore_errors=True)
    for rel, content in files.items():
        path = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "wb").write(content)
    digest, count, size = plugin.package_digest(root)
    return {"id": "DRIVERS/Net/%s" % name, "files": count, "size": size, "digest": digest}


def scenario_plugin_security(workdir: str) -> None:
    print("\nPlugin serveur : refus des archives et inventaires dangereux")
    base = os.path.join(workdir, "plug")
    rel = "Windows10/DellInc/OptiPlex_7090"
    good_files = {"a.inf": b"[Version]\n", "sub/b.sys": b"binaire"}

    def fresh(name):
        depot = os.path.join(base, name, "depot")
        return Crafted(depot, "drivers_%s" % name), depot

    def model_dir(depot):
        return os.path.join(depot, "drivers", *rel.split("/"))

    # 0. cas nominal fabrique a la main (valide les outils de test eux-memes)
    crafted, depot = fresh("ok")
    pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
    crafted.run(rel, [pkg], [], [("%s/DRIVERS/Net/pkg/a.inf" % rel, good_files["a.inf"]),
                                 ("%s/DRIVERS/Net/pkg/sub/b.sys" % rel, good_files["sub/b.sys"])])
    check("trames fabriquees valides : acceptees", str(crafted.last().get("action", "")
          ).endswith("_done"), crafted.message() or str(crafted.last())[:120])

    # 1. zip-slip
    crafted, depot = fresh("slip")
    pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
    crafted.run(rel, [pkg], [], [("%s/DRIVERS/Net/pkg/a.inf" % rel, good_files["a.inf"]),
                                  ("%s/DRIVERS/Net/pkg/../../../../../evil.txt" % rel, b"x")])
    check("zip-slip refuse", crafted.is_error(), crafted.message())
    check("zip-slip : rien ecrit hors du depot",
          not os.path.exists(os.path.join(base, "slip", "evil.txt"))
          and not os.path.exists(os.path.join(depot, "evil.txt")))
    check("zip-slip : rien installe dans le depot", not os.path.isdir(model_dir(depot)))

    # 2. chemin absolu / lecteur Windows / antislash
    for label, name in (("absolu", "/etc/cron.d/x"), ("lecteur", "C:/Windows/x"),
                        ("antislash", "%s\\DRIVERS\\Net\\pkg\\a.inf" % rel)):
        crafted, depot = fresh("abs_" + label)
        pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
        crafted.run(rel, [pkg], [], [(name, b"x")])
        check("entree %s refusee" % label, crafted.is_error(), crafted.message())
        check("entree %s : depot intact" % label, not os.path.isdir(model_dir(depot)))

    # 3. relative_dir hors contrat
    for label, bad in (("remontant", "../../etc/x"), ("2 composants", "Windows10/DellInc"),
                       ("absolu", "/Windows10/DellInc/x"), ("point", ".hidden/a/b"),
                       ("antislash", "Windows10\\DellInc\\x")):
        crafted, depot = fresh("rel_" + re.sub(r"\W", "", label))
        crafted.send({"type": "inventory", "schema": "medulla.extractdrivers.v2",
                      "metadata": {"relative_dir": bad}, "packages": [{
                          "id": "DRIVERS/Net/p", "files": 1, "size": 1,
                          "digest": "0" * 64}], "certs": []})
        check("relative_dir %s refuse" % label, crafted.is_error(), crafted.message())

    # 4. package non demande dans l'archive
    crafted, depot = fresh("unknown")
    pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
    crafted.run(rel, [pkg], [], [("%s/DRIVERS/Net/pkg/a.inf" % rel, good_files["a.inf"]),
                                  ("%s/DRIVERS/Net/pkg/sub/b.sys" % rel, good_files["sub/b.sys"]),
                                  ("%s/DRIVERS/Net/pirate/x.inf" % rel, b"x")])
    check("package non demande refuse", crafted.is_error(), crafted.message())
    check("package non demande : depot intact", not os.path.isdir(model_dir(depot)))

    # 5. entree hors du dossier modele
    crafted, depot = fresh("other_model")
    pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
    crafted.run(rel, [pkg], [], [("Windows10/Autre/Modele/DRIVERS/Net/pkg/a.inf", b"x")])
    check("entree d'un autre modele refusee", crafted.is_error(), crafted.message())

    # 6. contenu different de l'inventaire (empreinte de package)
    crafted, depot = fresh("digest")
    pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
    crafted.run(rel, [pkg], [], [("%s/DRIVERS/Net/pkg/a.inf" % rel, good_files["a.inf"]),
                                  ("%s/DRIVERS/Net/pkg/sub/b.sys" % rel, b"BINAIRE")])
    check("package different de l'inventaire : refuse", crafted.is_error()
          and "inventaire" in crafted.message(), crafted.message())
    check("package different : depot intact", not os.path.isdir(model_dir(depot)))

    # 7. certificat different de l'inventaire
    crafted, depot = fresh("cert")
    cert = {"thumbprint": "AABBCCDDEEFF0011", "size": 4,
            "sha256": hashlib.sha256(b"vrai").hexdigest()}
    crafted.run(rel, [], [cert], [("%s/CERTS/AABBCCDDEEFF0011.cer" % rel, b"faux")])
    check("certificat different de l'inventaire : refuse", crafted.is_error()
          and "inventaire" in crafted.message(), crafted.message())
    crafted, depot = fresh("cert_ok")
    crafted.run(rel, [], [cert], [("%s/CERTS/AABBCCDDEEFF0011.cer" % rel, b"vrai")])
    check("certificat conforme : accepte", str(crafted.last().get("action", "")
          ).endswith("_done"), crafted.message())

    # 8. un fichier existant du depot n'est jamais supprime
    crafted, depot = fresh("keep")
    keep = os.path.join(model_dir(depot), "DRIVERS", "Net", "pkg", "ancien.inf")
    os.makedirs(os.path.dirname(keep))
    open(keep, "wb").write(b"ancien")
    pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
    crafted.run(rel, [pkg], [], [("%s/DRIVERS/Net/pkg/a.inf" % rel, good_files["a.inf"]),
                                  ("%s/DRIVERS/Net/pkg/sub/b.sys" % rel, good_files["sub/b.sys"])])
    check("fusion : fichier ancien conserve, nouveaux fichiers ajoutes",
          os.path.isfile(keep) and os.path.isfile(os.path.join(
              os.path.dirname(keep), "sub", "b.sys")))

    # 9. trame inconnue / session inconnue / emetteur different
    crafted, depot = fresh("misc")
    crafted.send({"type": "bidon"})
    check("type de trame inconnu : erreur", crafted.is_error(), crafted.message())
    crafted.send({"type": "data", "segment_idx": 0, "segment_total": 1, "raw_size": 1,
                  "md5_segment": "0", "data_b64": "", "last": True})
    check("bloc sans session : erreur retryable", crafted.is_error()
          and crafted.last()["data"].get("retryable") is True, crafted.message())
    pkg = package_entry(crafted.plugin, workdir, "pkg", good_files)
    crafted.send({"type": "inventory", "schema": "medulla.extractdrivers.v2",
                  "metadata": {"relative_dir": rel}, "packages": [pkg], "certs": []})
    check("inventaire valide : plan renvoye", str(crafted.last().get("action", "")
          ).endswith("_plan") and crafted.last()["data"]["need"] == [0])
    crafted.receiver.sender_jid = "pirate@pulse/res"
    crafted.send({"type": "meta", "schema": "medulla.extractdrivers.v2", "size": 1,
                  "md5": "0" * 32, "sha256": "0" * 64, "segment_bytes": 2048,
                  "segment_total": 1, "unpacked_size": 0})
    check("emetteur different de celui de la session : refuse", crafted.is_error()
          and "emetteur" in crafted.message(), crafted.message())

    # 10. schema inconnu
    crafted, depot = fresh("schema")
    crafted.send({"type": "inventory", "schema": "medulla.extractdrivers.v1",
                  "metadata": {"relative_dir": rel}, "packages": [], "certs": []})
    check("schema v1 refuse", crafted.is_error() and "schema" in crafted.message(),
          crafted.message())


def scenario_digest_crosscheck(workdir: str, staging: str) -> None:
    print("\nConcordance client/serveur du calcul d'empreinte des packages")
    sender = load_sender_module()
    plugin = mock_receiver.load_plugin(os.path.join(workdir, "depot_x"))
    root = os.path.join(staging, *REL.split("/"), "DRIVERS")
    same = True
    for cls in sorted(os.listdir(root)):
        for pkg in sorted(os.listdir(os.path.join(root, cls))):
            path = os.path.join(root, cls, pkg)
            same &= tuple(sender.package_digest(path)) == tuple(plugin.package_digest(path))
    check("package_digest identique cote poste et cote serveur", same)
    names = ["ok", "a b", "x" * 200, "x" * 201, "a.", " a", "a ", "..", ".", "a:b", "a*b",
             "", "a\x01", "dossier\\x", "con.txt", "é"]
    mismatched = [n for n in names if bool(sender.valid_component(n))
                  != bool(plugin.valid_component(n))]
    check("valid_component identique cote poste et cote serveur", not mismatched,
          str(mismatched))
    rels = [REL, "a/b", "a/b/c/d", "../a/b", ".a/b/c", "a/b/.c", "a//b", "a/b/c/", "",
            "a\\b\\c", "a/b/c.", None, 5]
    mismatched = [r for r in rels if bool(sender.valid_relative_dir(r))
                  != bool(plugin_ok(plugin, r))]
    check("relative_dir : memes regles cote poste et cote serveur", not mismatched,
          str(mismatched))


def plugin_ok(plugin, value) -> bool:
    try:
        return bool(plugin.clean_relative_dir(value))
    except Exception:
        return False


# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)

    for path in (SENDER, os.path.join(HERE, "fake_slixmpp.py"),
                 os.path.join(ROOT, "server", "plugin_extract_drivers.py")):
        if not os.path.isfile(path):
            print("Fichier introuvable : %s" % path, file=sys.stderr)
            return 2

    print("Validation de bout en bout du depot XMPP v2 drivers/certificats")
    print("Transporteur : %s" % SENDER)

    with tempfile.TemporaryDirectory(prefix="drivers_test_") as workdir:
        staging = os.path.join(workdir, "staging")
        build_staging(staging)
        write_config(os.path.join(workdir, "agentconf.ini"))

        scenario_self_test()
        depot = scenario_first_transfer(workdir, staging)
        scenario_nothing_to_send(workdir, staging, depot)
        scenario_differential(workdir, staging, depot)
        scenario_resume_same_run(workdir, staging)
        scenario_resume_across_runs(workdir, staging)
        scenario_resend(workdir, staging)
        scenario_no_final_ack(workdir, staging)
        scenario_no_plan(workdir, staging)
        scenario_untrusted_replies(workdir, staging)
        scenario_server_refusal(workdir, staging)
        scenario_stuck_queue(workdir, staging)
        scenario_connection(workdir, staging)
        scenario_parameters(workdir, staging)
        scenario_jid_via_agent(workdir)
        scenario_jid_minimal(workdir)
        scenario_replay(workdir, staging)
        scenario_backpressure(workdir)
        scenario_concurrent_blocks(workdir, staging)
        scenario_plugin_security(workdir)
        scenario_digest_crosscheck(workdir, staging)

    print("\n" + "=" * 70)
    if FAILURES:
        print("RESULTAT : ECHEC (%d controle(s) en echec sur %d)" % (len(FAILURES), CHECKS))
        for failure in FAILURES:
            print("  - %s" % failure)
        return 1
    print("RESULTAT : OK (%d controles passes)" % CHECKS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
