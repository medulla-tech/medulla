#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send-DriversOverXmpp.py - transport XMPP des drivers/certificats (protocole v2)
===============================================================================

Compagnon de ExtractDrivers-XMPP.ps1. Ce script est execute *sur le poste*
par le script PowerShell (donc par l'agent Medulla, en SYSTEM) et transfere
le dossier de travail (drivers + certificats extraits) vers le serveur
Medulla via XMPP. Il n'y a AUCUN partage SMB, donc aucun identifiant a
stocker dans le script.

Pourquoi Python et pas du PowerShell pur
----------------------------------------
Chaque poste gere par Medulla a deja un agent Python connecte en XMPP
(`pulse_xmpp_agent`, base sur slixmpp). On reutilise donc :

  * le runtime Python de l'agent (`C:\\Program Files\\Python3\\python.exe`) ;
  * sa configuration (`C:\\Program Files\\Medulla\\etc\\agentconf.ini`) ;
  * l'identite XMPP de la machine, calculee EXACTEMENT comme l'agent la
    calcule (voir `derive_jid_via_agent`), afin que le serveur reconnaisse
    l'emetteur comme une machine du parc.

Protocole v2 en trois phases
----------------------------
1. Inventaire. Le poste hache chaque package de drivers
   (`DRIVERS/<classe>/<package>`) et chaque certificat, puis envoie la liste
   (identifiant, nombre de fichiers, octets, empreinte) au plugin serveur,
   par le mecanisme natif `bigdata` de Medulla (`plugin_big_data.py`).
   Le serveur compare avec son depot et repond par un PLAN : les seuls
   elements manquants ou differents. Si le depot est deja a jour, il repond
   directement `_done` (`nothing_to_send`) : rien n'est transfere.
2. Archive differentielle. Le poste construit un ZIP DETERMINISTE des seuls
   elements demandes (meme besoin = meme SHA-256) et en annonce la taille et
   les empreintes dans une trame `meta`. Le serveur repond par `_resume` :
   le numero du premier bloc qui lui manque (0 pour un nouveau transfert).
3. Blocs. L'archive est lue par blocs de `--segment-bytes` (defaut 25 000 o),
   chacun compresse (zlib) puis encode en base64, avec son MD5 ; le dernier
   porte le SHA-256/MD5 globaux. Le serveur ecrit chaque bloc dans un fichier
   partiel, qui survit a une interruption : le transfert reprend au bloc
   suivant, sans renvoyer ce qui est deja arrive. A la fin, il verifie
   l'archive et chaque package contre l'inventaire, puis repond `_done`.

La memoire reste bornee quelle que soit la taille de l'export (un bloc a la
fois, lu directement dans le fichier).

Fiabilite de l'emission
-----------------------
* Toute l'emission se fait DANS la boucle asyncio (aucun thread) : slixmpp
  n'est pas thread-safe et un envoi depuis un thread peut perdre le reveil
  de la boucle et geler l'emission. Seule la construction du ZIP (CPU/disque)
  est deportee dans un thread, sans toucher a slixmpp.
* La file d'envoi de slixmpp sert de contre-pression et elle est videe AVANT
  la fermeture du flux : sans cela, la deconnexion tronquerait l'envoi tout
  en rapportant un succes.
* Seuls les messages du substitut destinataire portant NOTRE session sont
  acceptes (plan, reprise, renvoi de bloc, acquittement).
* Seuls les echecs transitoires sont retentes ; un refus du serveur ne l'est
  pas (sauf s'il le declare `retryable`). Une nouvelle tentative reprend
  grace a la reprise serveur et reutilise l'archive deja construite.

Protocole detaille et contrat du recepteur : voir PROTOCOLE.md.

Dependances
-----------
* Python 3.7+ (celui de l'agent) ;
* slixmpp >= 1.8 (fourni avec l'agent Windows : 1.8.5, API synchrone
  `connect()` + boucle asyncio, comme l'agent Medulla lui-meme) ;
* `pulse_xmpp_agent` importable (optionnel : repli sur une lecture
  autonome de `agentconf.ini` si l'import echoue).

Codes de sortie
---------------
  0  succes : depot mis a jour, ou deja a jour (rien a envoyer)
  2  prerequis manquant / configuration ou metadonnees illisibles, dossier
     de travail vide ou invalide
  3  connexion ou authentification XMPP impossible
  5  echec du transfert (plan/reprise/ACK absents, erreur renvoyee par le
     serveur, emission interrompue)
  99 erreur inattendue

Options de diagnostic utiles
----------------------------
  --check          teste uniquement la connexion XMPP (aucun transfert)
  --self-test      valide inventaire, archive et blocs hors ligne (sans reseau)
  --dump-frames    ecrit toutes les trames emises dans un fichier JSONL
                   (permet de rejouer/valider le protocole sans serveur)
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import configparser
import hashlib
import json
import logging
import os
import platform
import random
import re
import shutil
import ssl
import string
import sys
import time
import zipfile
import zlib

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

SCHEMA = "medulla.extractdrivers.v2"

#: Taille des tranches `bigdata` (identique a Medulla :
#: `agentxmpp.sendbigdatatoagent`, segment_size=65535 caracteres). N'est utilise
#: que pour la trame d'inventaire.
BIGDATA_SEGMENT_CHARS = 65535

#: Taille des blocs bruts de l'archive (identique a Medulla :
#: `plugin_resulttransfertfile` lit 25000 octets).
DEFAULT_SEGMENT_BYTES = 25000

#: Bornes de `--segment-bytes`. La borne haute reste sous la limite usuelle de
#: `max_stanza_size` des serveurs XMPP (65536 octets une fois encode).
MIN_SEGMENT_BYTES = 1024
MAX_SEGMENT_BYTES = 48000

#: Nombre maximal de renvois acceptes pour un meme bloc (meme valeur que le
#: serveur) : evite une boucle si un bloc est refuse en permanence.
MAX_RESENDS_PER_BLOCK = 3

#: Chemin par defaut de la configuration de l'agent (Windows).
DEFAULT_AGENT_CONF_WINDOWS = r"C:\Program Files\Medulla\etc\agentconf.ini"

#: Chemin par defaut de la configuration de l'agent (Linux / macOS, pour les
#: tests et les postes non Windows).
DEFAULT_AGENT_CONF_UNIX = "/etc/pulse-xmpp-agent/agentconf.ini"

#: JID du substitut maitre : c'est lui qui recoit les messages des postes.
DEFAULT_MASTER_JID = "master@pulse"

LOG = logging.getLogger("extractdrivers.xmpp")

EXIT_OK = 0
EXIT_PREREQ = 2
EXIT_CONNECT = 3
EXIT_TRANSFER = 5
EXIT_UNEXPECTED = 99


# ---------------------------------------------------------------------------
# Journalisation
# ---------------------------------------------------------------------------

def setup_logging(log_path: str | None, verbose: bool) -> None:
    """Journalise a la fois sur la sortie standard et dans un fichier."""
    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    LOG.handlers = []

    fmt_file = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s",
                                 datefmt="%Y-%m-%d %H:%M:%S")
    fmt_console = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s",
                                    datefmt="%Y-%m-%d %H:%M:%S")

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(fmt_console)
    LOG.addHandler(console)

    if log_path:
        try:
            directory = os.path.dirname(os.path.abspath(log_path))
            if directory:
                os.makedirs(directory, exist_ok=True)
            handler = logging.FileHandler(log_path, encoding="utf-8")
            handler.setFormatter(fmt_file)
            LOG.addHandler(handler)
        except OSError as exc:  # pragma: no cover - depend de l'environnement
            LOG.warning("Impossible d'ouvrir le journal %s : %s", log_path, exc)


# ---------------------------------------------------------------------------
# Fonctions pures (testables sans slixmpp ni reseau)
# ---------------------------------------------------------------------------

def md5_file(path: str, chunk_size: int = 1 << 20) -> str:
    """MD5 hexadecimale d'un fichier (lecture en flux)."""
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_file(path: str, chunk_size: int = 1 << 20) -> str:
    """SHA-256 hexadecimale d'un fichier (lecture en flux)."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def md5_bytes(data: bytes) -> str:
    """MD5 hexadecimale d'un bloc d'octets."""
    return hashlib.md5(data).hexdigest()


def new_sessionid(prefix: str = "drivers") -> str:
    """Identifiant de session de transfert, lisible et unique."""
    alphabet = string.ascii_lowercase + string.digits
    suffix = "".join(random.choice(alphabet) for _ in range(6))
    return "%s_%s_%d_%s" % (prefix, time.strftime("%Y%m%d%H%M%S"), os.getpid(), suffix)


def read_ini(path: str) -> configparser.ConfigParser:
    """
    Lit un fichier INI de la meme maniere que l'agent : le fichier principal
    puis, s'il existe, sa surcharge `<fichier>.local` (utilisee en production
    pour les valeurs locales).
    """
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # respecte la casse (keyAES32, confserver...)
    if not os.path.isfile(path):
        raise FileNotFoundError("Fichier de configuration introuvable : %s" % path)
    parser.read(path, encoding="utf-8")
    local = path + ".local"
    if os.path.isfile(local):
        parser.read(local, encoding="utf-8")
    return parser


def config_get(parser: configparser.ConfigParser, section: str, option: str,
               default: str = "") -> str:
    """Lecture tolerante (section/cle absente -> valeur par defaut)."""
    try:
        value = parser.get(section, option)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return default
    return value.strip() if isinstance(value, str) else default


def first_of(value: str) -> str:
    """`confserver` peut etre une liste separee par des virgules."""
    return value.split(",")[0].strip() if value else ""


def read_jidsuffixe(infostmp_dir: str) -> str:
    """
    Reproduit `pulse_xmpp_agent.lib.configuration` : le suffixe de JID est un
    code alphanumerique de 3 caracteres stocke dans `INFOSTMP/JIDSUFFIXE`.

    LECTURE SEULE : le transporteur ne cree et ne modifie jamais ce fichier
    (c'est l'agent qui en est proprietaire). S'il est absent, l'appelant
    retombe sur un suffixe deterministe et journalise un avertissement.
    """
    path = os.path.join(infostmp_dir, "JIDSUFFIXE")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            suffix = handle.read()[:3]
    except OSError:
        return ""
    return suffix if suffix.isalnum() else ""


def find_agent_package_dir() -> str | None:
    """
    Repertoire du paquet `pulse_xmpp_agent` installe sur le poste, afin de
    localiser `lib/INFOSTMP/JIDSUFFIXE`. `None` si introuvable.
    """
    candidates = []

    # 1) Le paquet est deja importable : on interroge son emplacement reel.
    try:
        import importlib.util
        spec = importlib.util.find_spec("pulse_xmpp_agent")
        if spec and spec.origin:
            candidates.append(os.path.dirname(os.path.abspath(spec.origin)))
    except Exception:  # pragma: no cover - depend de l'installation
        pass

    # 2) Emplacements standards constates sur les postes Windows / Linux.
    candidates += [
        r"C:\Program Files\Python3\Lib\site-packages\pulse_xmpp_agent",
        r"C:\Program Files (x86)\Python3\Lib\site-packages\pulse_xmpp_agent",
        "/usr/lib/python3/dist-packages/pulse_xmpp_agent",
        "/opt/medulla/lib/python3.11/site-packages/pulse_xmpp_agent",
    ]

    for candidate in candidates:
        if os.path.isdir(os.path.join(candidate, "lib")):
            return candidate
    return None


def derive_jid_minimal(parser: configparser.ConfigParser,
                       agent_package_dir: str | None,
                       resource: str) -> tuple[str, str]:
    """
    Repli autonome : reconstruit le JID complet de la machine sans importer
    `pulse_xmpp_agent`, en suivant `lib/configuration.py` :

        <nom_machine>.<suffixe_alphanumerique_3>@<domaine>/<ressource>

    Retourne (jid_complet, origine) ou l'origine vaut 'minimal'.
    """
    hostname = platform.node().split(".")[0]

    jidsuffixe = ""
    if agent_package_dir:
        jidsuffixe = read_jidsuffixe(os.path.join(agent_package_dir, "lib", "INFOSTMP"))
    if not jidsuffixe:
        # Dernier recours : suffixe DETERMINISTE derive du nom de machine.
        # Ne jamais utiliser hash() ici : Python randomise les hash de chaines
        # a chaque processus, le JID changerait donc a chaque execution et le
        # serveur ne reconnaitrait plus la machine.
        jidsuffixe = hashlib.md5(hostname.encode("utf-8")).hexdigest()[:3]
        LOG.warning("Suffixe de JID de l'agent illisible (INFOSTMP/JIDSUFFIXE) : "
                    "suffixe deterministe %s utilise. Le JID peut differer de "
                    "celui de l'agent si celui-ci n'a jamais demarre.",
                    jidsuffixe)

    username = "%s.%s" % (hostname, jidsuffixe)
    domain = (config_get(parser, "chat", "domain")
              or config_get(parser, "configuration_server", "confdomain")
              or "pulse")

    return "%s@%s/%s" % (username, domain, resource), "minimal"


def derive_jid_via_agent(agent_type: str, resource: str) -> tuple[str, str]:
    """
    Voie preferee : on demande son JID a l'agent lui-meme via
    `pulse_xmpp_agent.lib.configuration.confParameter`, exactement comme le
    fait le service Medulla. Aucune duplication de logique, donc aucune
    divergence possible lors d'une montee de version de l'agent.

    Le JID est ensuite reecrit avec NOTRE ressource XMPP : l'agent tourne en
    permanence avec la sienne (adresse MAC), et deux connexions avec le meme
    JID complet se deconnecteraient mutuellement (conflit XMPP). La partie
    `bare` (machine@domaine) reste identique, c'est elle qui identifie la
    machine aupres du serveur.
    """
    package_dir = find_agent_package_dir()
    if package_dir:
        parent = os.path.dirname(package_dir)
        if parent not in sys.path:
            sys.path.insert(0, parent)

    from pulse_xmpp_agent.lib.configuration import confParameter  # type: ignore

    conf = confParameter(agent_type)
    jid_agent = getattr(conf, "jidagent", "") or ""
    if not jid_agent:
        raise RuntimeError("confParameter n'a pas fourni de jidagent")

    bare = jid_agent.split("/")[0]
    return "%s/%s" % (bare, resource), "agent"


def resolve_connection(parser: configparser.ConfigParser, jid: str,
                       overrides: argparse.Namespace) -> dict:
    """
    Assemble les parametres de connexion :

      * serveur / port : `[connection]` (renseigne par l'agent apres
        configuration), sinon `[configuration_server]` (confserver/confport) ;
      * mot de passe : `[configuration_server] confpassword`, comme l'agent ;
      * domaine : `[chat] domain` puis `confdomain`.
    """
    server = overrides.server or config_get(parser, "connection", "server") \
        or first_of(config_get(parser, "configuration_server", "confserver"))
    port = overrides.port or config_get(parser, "connection", "port") \
        or config_get(parser, "configuration_server", "confport") or "5222"
    password = config_get(parser, "configuration_server", "confpassword") \
        or config_get(parser, "connection", "password")
    domain = config_get(parser, "chat", "domain") \
        or config_get(parser, "configuration_server", "confdomain") or "pulse"

    return {
        "server": first_of(server),
        "port": int(port),
        "password": password,
        "domain": domain,
        "jid": jid,
    }


# --- Framing `bigdata` (natif Medulla) --------------------------------------

def build_bigdata_messages(payload_json: str, sender_full: str,
                           segment_chars: int = BIGDATA_SEGMENT_CHARS) -> list[str]:
    """
    Reproduit `agentxmpp.sendbigdatatoagent` : si la charge utile tient sous
    `segment_chars`, elle part telle quelle ; sinon elle est compressee
    (zlib), encodee en base64 et decoupee en tranches.

    Retourne la liste des corps de messages XMPP a envoyer, dans l'ordre.
    """
    if len(payload_json) <= segment_chars:
        return [payload_json]

    sessionid = new_sessionid("bigdata")
    compressed = zlib.compress(payload_json.encode("utf-8"))
    encoded = base64.b64encode(compressed).decode("utf-8")
    total = (len(encoded) + segment_chars - 1) // segment_chars

    messages = []
    for index in range(total):
        segment = encoded[index * segment_chars:(index + 1) * segment_chars]
        messages.append(json.dumps({
            "action": "big_data",
            "sessionid": sessionid,
            "data": {
                "segment": segment,
                "nb_segment": index + 1,
                "nb_segment_total": total,
                "from": sender_full,
            },
        }))
    return messages


def reassemble_bigdata(messages: list[str]) -> str:
    """
    Contrepartie de `build_bigdata_messages` (utilisee par `--self-test` et
    fournie comme reference dans les tests).

    Attention : on ne peut pas se fier au nombre de messages pour savoir si la
    charge utile a ete decoupee. Une charge utile tres compressible peut tenir
    en UNE seule tranche `big_data` (et non en un message direct). On inspecte
    donc l'action de chaque corps de message.
    """
    frames = []
    for body in messages:
        frame = json.loads(body)
        if frame.get("action") != "big_data":
            # Message direct : une charge utile non decoupee.
            return body
        frames.append(frame)

    parts = {}
    for frame in frames:
        parts[int(frame["data"]["nb_segment"])] = frame["data"]["segment"]
    joined = "".join(parts[index] for index in range(1, len(parts) + 1))
    return zlib.decompress(base64.b64decode(joined)).decode("utf-8")


# --- Inventaire du dossier de travail ---------------------------------------

_COMPONENT_RE = re.compile(r'^[^\x00-\x1f\x7f\\/:*?"<>|]{1,200}$')
_CERT_NAME_RE = re.compile(r"^([0-9A-Fa-f]{8,128})\.cer$", re.IGNORECASE)


def valid_component(value) -> bool:
    """Meme regle que `valid_component` du plugin serveur (a garder identique)."""
    return (isinstance(value, str) and bool(_COMPONENT_RE.match(value))
            and value not in (".", "..") and value == value.strip()
            and not value.endswith("."))


def valid_relative_dir(value) -> bool:
    """`<OS>/<Fabricant>/<Modele>` : exactement 3 composants surs, sans point initial."""
    parts = value.split("/") if isinstance(value, str) else []
    return len(parts) == 3 and all(valid_component(p) and not p.startswith(".")
                                   for p in parts)


def walk_files(root: str) -> list:
    """[(chemin relatif en '/', chemin complet)] trie, liens symboliques ignores."""
    result = []
    for directory, dirs, files in os.walk(root):
        dirs.sort()
        for name in files:
            full = os.path.join(directory, name)
            if os.path.islink(full):
                continue
            result.append((os.path.relpath(full, root).replace(os.sep, "/"), full))
    result.sort(key=lambda item: item[0])
    return result


def package_digest(root: str) -> tuple:
    """
    Empreinte canonique d'un package : sha256 des lignes
    `<chemin relatif>\\t<taille>\\t<sha256 du fichier>\\n`, triees par chemin.
    DOIT rester identique a `package_digest` de server/plugin_extract_drivers.py.
    Retourne (digest, nombre de fichiers, octets).
    """
    digest = hashlib.sha256()
    files = 0
    total = 0
    for rel, full in walk_files(root):
        size = os.path.getsize(full)
        digest.update(("%s\t%d\t%s\n" % (rel, size, sha256_file(full))).encode("utf-8"))
        files += 1
        total += size
    return digest.hexdigest(), files, total


def scan_staging(root: str) -> dict:
    """
    Inventorie `<staging>/<OS>/<Fabricant>/<Modele>` : packages `DRIVERS/<classe>/
    <package>` et certificats `CERTS/<thumbprint>.cer`.

    Tout ce que le serveur refuserait (nom invalide, collision de casse, fichier
    parasite) est exclu ICI avec un avertissement, plutot que de faire rejeter
    l'archive entiere. Retourne {"packages", "certs", "warnings"}.
    """
    warnings: list = []
    packages: list = []
    certs: list = []

    drivers = os.path.join(root, "DRIVERS")
    seen = set()
    for cls in (sorted(os.listdir(drivers)) if os.path.isdir(drivers) else []):
        cdir = os.path.join(drivers, cls)
        if os.path.islink(cdir) or not os.path.isdir(cdir):
            warnings.append("DRIVERS/%s : n'est pas une classe de drivers, ignore." % cls)
            continue
        if not valid_component(cls):
            warnings.append("DRIVERS/%s : nom de classe invalide, ignore." % cls)
            continue
        for pkg in sorted(os.listdir(cdir)):
            pdir = os.path.join(cdir, pkg)
            pid = "DRIVERS/%s/%s" % (cls, pkg)
            if os.path.islink(pdir) or not os.path.isdir(pdir):
                warnings.append("%s : n'est pas un package, ignore." % pid)
                continue
            if not valid_component(pkg):
                warnings.append("%s : nom de package invalide, ignore." % pid)
                continue
            if pid.lower() in seen:
                warnings.append("%s : collision de casse avec un autre package, ignore." % pid)
                continue
            entries = walk_files(pdir)
            if not entries:
                warnings.append("%s : package vide, ignore." % pid)
                continue
            bad = [rel for rel, _ in entries
                   if not all(valid_component(p) for p in rel.split("/"))]
            if bad:
                warnings.append("%s : nom de fichier invalide (%s), package ignore."
                                % (pid, bad[0]))
                continue
            seen.add(pid.lower())
            digest, files, size = package_digest(pdir)
            packages.append({"id": pid, "files": files, "size": size,
                             "digest": digest, "path": pdir})
    packages.sort(key=lambda item: item["id"])

    cdir = os.path.join(root, "CERTS")
    seen = set()
    for name in (sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []):
        full = os.path.join(cdir, name)
        match = _CERT_NAME_RE.match(name)
        if os.path.islink(full) or not os.path.isfile(full) or not match:
            warnings.append("CERTS/%s : pas un certificat <thumbprint>.cer, ignore." % name)
            continue
        thumb = match.group(1)
        if thumb.lower() in seen:
            warnings.append("CERTS/%s : doublon (casse), ignore." % name)
            continue
        seen.add(thumb.lower())
        certs.append({"thumbprint": thumb, "size": os.path.getsize(full),
                      "sha256": sha256_file(full), "path": full})
    certs.sort(key=lambda item: item["thumbprint"].lower())
    return {"packages": packages, "certs": certs, "warnings": warnings}


def inventory_json(action: str, sessionid: str, metadata: dict,
                   packages: list, certs: list) -> str:
    """Message logique d'inventaire (phase 1), avant decoupage `bigdata`."""
    return json.dumps({
        "action": action,
        "sessionid": sessionid,
        "ret": 0,
        "base64": False,
        "data": {
            "type": "inventory",
            "schema": SCHEMA,
            "metadata": metadata,
            "packages": [{"id": p["id"], "files": p["files"], "size": p["size"],
                          "digest": p["digest"]} for p in packages],
            "certs": [{"thumbprint": c["thumbprint"], "size": c["size"],
                       "sha256": c["sha256"]} for c in certs],
        },
    }, ensure_ascii=False)


# --- Archive differentielle et blocs ----------------------------------------

def build_delta_zip(zip_path: str, relative_dir: str, packages: list,
                    certs: list, need: list) -> dict:
    """
    Construit l'archive des seuls elements demandes par le serveur.

    Elle est DETERMINISTE (entrees triees, horodatage fige, attributs neutres,
    pas de metadata.json) : le meme besoin donne le meme SHA-256, ce qui permet
    au serveur de reprendre un transfert interrompu sur son fichier partiel.
    """
    entries = []
    for index in need:
        if index >= 0:
            pkg = packages[index]
            for rel, full in walk_files(pkg["path"]):
                entries.append(("%s/%s/%s" % (relative_dir, pkg["id"], rel), full))
        else:
            cert = certs[-index - 1]
            entries.append(("%s/CERTS/%s.cer" % (relative_dir, cert["thumbprint"]),
                            cert["path"]))
    entries.sort(key=lambda item: item[0])

    tmp_path = zip_path + ".tmp"
    unpacked = 0
    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for arcname, full in entries:
            size = os.path.getsize(full)
            zinfo = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zinfo.create_system = 0
            zinfo.external_attr = 0
            zinfo.file_size = size
            with open(full, "rb") as src, \
                    zf.open(zinfo, "w", force_zip64=size >= (1 << 31)) as dst:
                shutil.copyfileobj(src, dst, 1 << 20)
            unpacked += size
    os.replace(tmp_path, zip_path)
    return {"path": zip_path, "size": os.path.getsize(zip_path),
            "md5": md5_file(zip_path), "sha256": sha256_file(zip_path),
            "unpacked_size": unpacked, "filename": os.path.basename(zip_path)}


def block_total(size: int, segment: int) -> int:
    return max(1, (size + segment - 1) // segment)


def build_meta_frame(action: str, sessionid: str, info: dict, segment: int,
                     metadata: dict, n_packages: int, n_certs: int) -> dict:
    """Trame de metadonnees (phase 2) : decrit l'archive differentielle."""
    return {
        "action": action,
        "sessionid": sessionid,
        "ret": 0,
        "base64": False,
        "data": {
            "type": "meta",
            "schema": SCHEMA,
            "delta": True,
            "size": info["size"],
            "md5": info["md5"],
            "sha256": info["sha256"],
            "segment_bytes": segment,
            "segment_total": block_total(info["size"], segment),
            "unpacked_size": info["unpacked_size"],
            "filename": info["filename"],
            "packages": n_packages,
            "certs": n_certs,
            "metadata": metadata,
        },
    }


def make_data_frame(handle, action: str, sessionid: str, index: int,
                    segment: int, info: dict) -> dict:
    """
    Trame du bloc `index`, lue directement dans l'archive (acces aleatoire :
    sert a la reprise et aux renvois, sans relire les blocs precedents).
    """
    total = block_total(info["size"], segment)
    handle.seek(index * segment)
    block = handle.read(segment)
    data = {
        "type": "data",
        "segment_idx": index,
        "segment_total": total,
        "raw_size": len(block),
        "md5_segment": md5_bytes(block),
        "data_b64": base64.b64encode(zlib.compress(block, 6)).decode("ascii"),
        "last": index == total - 1,
    }
    if index == total - 1:
        data["md5_total"] = info["md5"]
        data["sha256_total"] = info["sha256"]
    return {"action": action, "sessionid": sessionid, "ret": 0,
            "base64": False, "data": data}


# ---------------------------------------------------------------------------
# Client XMPP (slixmpp)
# ---------------------------------------------------------------------------

class XmppFailed(Exception):
    """Prerequis ou configuration invalide (code de sortie 2)."""


def build_ssl_context(verify: bool, ca_cert: str | None):
    """Contexte TLS : verification systeme par defaut, comme l'agent."""
    if not verify:
        LOG.warning("Verification TLS DESACTIVEE (--tls-verify 0) : "
                    "a n'utiliser qu'en diagnostic.")
        return ssl._create_unverified_context()
    context = ssl.create_default_context()
    if ca_cert:
        context.load_verify_locations(cafile=ca_cert)
    return context


def tls_active(client) -> bool:
    """
    Indique si la session XMPP courante est effectivement chiffree.

    slixmpp 1.8.5 ne dispose d'aucun moyen d'EXIGER STARTTLS : il negocie le
    chiffrement si le serveur l'annonce, sinon il poursuit en clair, et
    l'attribut `force_starttls` n'est jamais lu par le code (verifie dans
    slixmpp 1.8.5 : uniquement affecte, jamais consulte). `--require-starttls`
    est donc applique ici, cote transporteur, en verifiant le transport apres
    l'authentification.
    """
    transport = getattr(client, "transport", None)
    if transport is not None:
        for key in ("ssl_object", "sslcontext"):
            try:
                if transport.get_extra_info(key) is not None:
                    return True
            except Exception:  # pragma: no cover - transport atypique
                pass
    # Repli : slixmpp ajoute 'starttls' a ses fonctionnalites negociees.
    try:
        return "starttls" in getattr(client, "features", set())
    except Exception:  # pragma: no cover
        return False


class DriversUploader:
    """
    Pilote slixmpp 1.8.x (API synchrone `connect()` + boucle asyncio), la meme
    que celle utilisee par l'agent Medulla lui-meme.

    Toute l'emission se fait DANS la boucle asyncio, sous forme d'une tache
    (`asyncio.ensure_future`) et non d'un thread :

      * slixmpp n'est pas thread-safe (`send()` reveille la boucle via
        `Future.set_result` sans `call_soon_threadsafe`) : emettre depuis un
        thread peut perdre le reveil et geler l'emission ;
      * la memoire reste bornee : chaque bloc est lu directement dans l'archive
        et jamais accumule ;
      * la file d'envoi de slixmpp (`waiting_queue`) sert de contre-pression,
        et l'on attend qu'elle soit vide avant de fermer le flux.

    Sequence :
      1. `connect()` puis `loop.run_forever()` ;
      2. a `session_start`, une tache d'emission est planifiee ;
      3. la boucle traite les ACK en parallele ;
      4. l'ACK final (ou un delai) ferme proprement puis arrete la boucle.
    """

    #: Nombre maximum de trames en attente dans la file de slixmpp avant de
    #: marquer une pause (contre-pression).
    MAX_PENDING_FRAMES = 200

    #: Duree maximale sans progression de la file d'envoi avant de conclure que
    #: le serveur n'absorbe plus les trames (echec transitoire).
    STALL_TIMEOUT_SECONDS = 120

    def __init__(self, options: argparse.Namespace, connection: dict,
                 action: str, sessionid: str, sender_full: str):
        self.options = options
        self.connection = connection
        self.action = action
        self.sessionid = sessionid
        self.sender_full = sender_full

        # Instancies dans la boucle (voir `_new_loop`).
        self.ready = None
        self.ack = None

        self.ack_payload: dict = {}
        self.resend_requests: list = []
        self.frames_sent = 0
        self.bytes_sent = 0
        self.bytes_total = 0
        self.error = None
        # "connect" si aucune connexion/authentification n'a pu etre etablie
        # (code de sortie 3), None sinon (echec de transfert, code 5).
        self.failure_kind = None
        # True uniquement pour un echec transitoire (coupure, file d'envoi non
        # vide) : un refus explicite du serveur, ou l'absence d'ACK, ne doit
        # PAS declencher un nouvel envoi complet de l'archive (cout reseau).
        self.retryable = False

        # Negociation v2 : plan (quoi envoyer) puis reprise (a partir de quel bloc).
        self.plan_parts: dict = {}
        self.plan_need: list = []
        self.plan_received = False
        self.resume_next = 0
        self.resume_total = 0
        self.nothing_to_send = False
        self.packages_sent = 0
        self.packages_skipped = 0
        self.certs_sent = 0
        self.certs_skipped = 0
        self.resumed_from = 0
        self.archive_info = None
        self.depot_path = ""
        self.resend_counts: dict = {}
        self.plan_evt = None
        self.resume_evt = None

        self.client = None
        self.loop = None
        self.task = None
        self.dump_handle = None
        self._shutting_down = False
        self.stream_done = False

        # Renseignes par `transfer()` avant l'execution.
        self.metadata: dict = {}
        self.scan: dict = {}

    # -- construction du client -------------------------------------------

    def _make_client(self):
        try:
            from slixmpp import ClientXMPP  # type: ignore
        except ImportError as exc:
            raise XmppFailed(
                "slixmpp introuvable : executer ce script avec le Python de "
                "l'agent Medulla (C:\\Program Files\\Python3\\python.exe). "
                "Detail : %s" % exc
            )

        uploader = self

        class _Client(ClientXMPP):
            def __init__(self, jid_value, password):
                super().__init__(jid_value, password)
                self.add_event_handler("session_start", self._on_start)
                self.add_event_handler("message", self._on_message)
                self.add_event_handler("failed_auth", self._on_failed_auth)
                self.add_event_handler("connection_failed", self._on_connection_failed)
                self.add_event_handler("disconnected", self._on_disconnected)

            def _on_start(self, event):
                if uploader.ready is not None:
                    uploader.ready.set()
                # L'exigence de chiffrement est evaluee AVANT le mode --check :
                # c'est justement l'un des points que --check doit valider.
                if uploader.options.require_starttls and not tls_active(self):
                    uploader.error = ("STARTTLS exige (--require-starttls) mais la "
                                      "session XMPP n'est pas chiffree")
                    uploader.failure_kind = "connect"
                    LOG.error("%s", uploader.error)
                    uploader._begin_shutdown()
                    return
                if uploader.options.check:
                    # Mode --check : on valide la connexion puis on s'arrete,
                    # sans demarrer l'emission (aucune charge utile).
                    uploader._begin_shutdown()
                    return
                uploader.task = asyncio.ensure_future(uploader._send_task())

            def _on_failed_auth(self, event):
                uploader.error = "authentification XMPP refusee (mot de passe invalide ?)"
                uploader.failure_kind = "connect"
                if uploader.ready is not None:
                    uploader.ready.set()
                uploader._begin_shutdown()

            def _on_connection_failed(self, event):
                # slixmpp signale les echecs de connexion par cet evenement
                # (`_connect_routine` intercepte les OSError et replanifie) :
                # sans ce gestionnaire, l'echec ne serait vu qu'a l'expiration
                # du delai de connexion.
                if uploader.task is None and uploader.error is None:
                    uploader.error = "connexion XMPP impossible (serveur injoignable ?)"
                    uploader.failure_kind = "connect"
                    if uploader.ready is not None:
                        uploader.ready.set()
                    uploader._begin_shutdown()

            def _on_disconnected(self, event):
                # Ne pas confondre une coupure subie avec la deconnexion que
                # NOUS demandons en fin de transfert (`_shutting_down`) : sinon
                # tout transfert reussi serait signale comme interrompu.
                if not uploader._shutting_down and uploader.error is None:
                    uploader.error = "connexion XMPP interrompue"
                    if uploader.ready is not None and uploader.ready.is_set():
                        # La session etait etablie : c'est un echec de TRANSFERT
                        # (code 5), transitoire, donc retentable. Le classer en
                        # "connexion" (code 3) ferait sortir la boucle de
                        # tentative et rendrait `retryable` inoperant.
                        uploader.failure_kind = None
                        uploader.retryable = True
                    else:
                        # Jamais authentifie : c'est un echec de connexion (3).
                        uploader.failure_kind = "connect"
                uploader._begin_shutdown()

            def _on_message(self, msg):
                uploader._handle_message(msg)

        return _Client

    # -- reception des ACK ------------------------------------------------

    def _handle_message(self, msg) -> None:
        """
        Contrat d'ACK (voir PROTOCOLE-XMPP.md) :

          * `<action>_done`  -> transfert termine cote serveur ;
          * `<action>_ack`   -> accuse ; `data.status` ok/success/done/finished
            termine le transfert, toute autre valeur = progression ;
          * `<action>_error` -> echec cote serveur (non retente tel quel) ;
          * `<action>_resend` avec `data.segment_idx` -> demande de renvoi.

        Securite : seuls les messages du substitut destinataire portant NOTRE
        session sont pris en compte. En cas de doute sur l'emetteur, on
        REFUSE le message (echec ferme) : sans ces controles, n'importe quel
        pair du domaine pourrait declarer le transfert reussi, et un ACK sans
        session serait accepte.
        """
        try:
            sender_bare = str(msg["from"].bare).lower()
        except Exception:
            sender_bare = ""
        expected_bare = self.options.master_jid.split("/")[0].lower()
        if not sender_bare:
            LOG.warning("Message XMPP ignore : emetteur illisible.")
            return
        if sender_bare != expected_bare:
            LOG.warning("Message XMPP ignore : emetteur %s inattendu (attendu %s).",
                        sender_bare, expected_bare)
            return

        try:
            body = json.loads(msg["body"])
        except Exception:
            LOG.debug("Message XMPP non JSON ignore : %r", msg["body"])
            return

        action = body.get("action", "")
        data = body.get("data") or {}
        if not isinstance(data, dict):
            data = {}

        sessionid = body.get("sessionid") or data.get("sessionid")
        if not sessionid:
            LOG.warning("Message XMPP ignore : sessionid absent (action=%s).", action)
            return
        if sessionid != self.sessionid:
            LOG.debug("ACK d'une autre session (%s) ignore", sessionid)
            return

        self.ack_payload = body

        if action == "%s_error" % self.action:
            self.error = "erreur renvoyee par le serveur : %s" % (
                data.get("message") or body.get("message") or "sans detail")
            self.retryable = bool(data.get("retryable"))
            self._wake_all()
            return

        if action == "%s_plan" % self.action:
            self._on_plan(data)
            return

        if action == "%s_resume" % self.action:
            try:
                self.resume_next = int(data.get("next_segment", 0))
                self.resume_total = int(data.get("segment_total", 0))
            except (TypeError, ValueError):
                self.error = "reponse de reprise illisible : %r" % (data,)
                self._wake_all()
                return
            LOG.info("Serveur : reprise au bloc %d sur %d.",
                     self.resume_next, self.resume_total)
            if self.resume_evt is not None:
                self.resume_evt.set()
            return

        if action == "%s_resend" % self.action:
            try:
                self.resend_requests.append(int(data.get("segment_idx", -1)))
            except (TypeError, ValueError):
                pass
            LOG.info("Renvoi du bloc %s demande par le serveur.", data.get("segment_idx"))
            return

        if action == "%s_done" % self.action:
            # Un `_done` reste le signal de succes le plus fort, mais il doit
            # tout de meme porter un statut coherent : un `_done` avec
            # status=error (recepteur mal ecrit) ne doit pas passer pour un
            # depot reussi.
            status = str(data.get("status", "")).lower()
            if status in ("error", "failed", "failure"):
                self.error = "le serveur a signale un echec : %s" % (
                    data.get("message") or data.get("depot_path") or "sans detail")
                self.retryable = bool(data.get("retryable"))
                self._wake_all()
                return
            self.nothing_to_send = bool(data.get("nothing_to_send"))
            self.depot_path = str(data.get("depot_path") or "")
            for key in ("packages_skipped", "certs_skipped"):
                if isinstance(data.get(key), int):
                    setattr(self, key, data[key])
            LOG.info("Transfert confirme par le serveur : %s%s",
                     self.depot_path or "-",
                     " (rien a envoyer : depot deja a jour)" if self.nothing_to_send else "")
            self._wake_all()
            return

        if action in ("%s_ack" % self.action, self.action):
            status = str(data.get("status", "")).lower()
            if status in ("ok", "success", "done", "finished"):
                LOG.info("Accuse de reception recu (status=%s).", status)
                self._wake_all()
            else:
                LOG.debug("Progression serveur : %s", status or "-")
            return

        LOG.debug("Message XMPP ignore (action=%s)", action)

    def _wake_all(self) -> None:
        """Reveille toutes les attentes (la tache d'emission relit alors l'etat)."""
        for event in (self.ack, self.plan_evt, self.resume_evt):
            if event is not None:
                event.set()

    def _on_plan(self, data: dict) -> None:
        """Assemble les tranches du plan (la liste peut depasser une trame)."""
        try:
            part, parts = int(data.get("part", 1)), int(data.get("parts", 1))
            need = [int(i) for i in data.get("need", [])]
            need_total = int(data.get("need_total", len(need)))
        except (TypeError, ValueError):
            self.error = "plan du serveur illisible : %r" % (data,)
            self._wake_all()
            return
        self.plan_parts[part] = need
        for key in ("packages_skipped", "certs_skipped"):
            if isinstance(data.get(key), int):
                setattr(self, key, data[key])
        if len(self.plan_parts) < parts:
            return
        merged = []
        for index in sorted(self.plan_parts):
            merged.extend(self.plan_parts[index])
        if len(merged) != need_total or len(set(merged)) != len(merged):
            self.error = ("plan du serveur incoherent : %d indice(s) recus pour %d "
                          "annonces" % (len(merged), need_total))
            self._wake_all()
            return
        self.plan_need = merged
        self.plan_received = True
        if self.plan_evt is not None:
            self.plan_evt.set()

    # -- emission ---------------------------------------------------------

    def _dump(self, message: str) -> None:
        if self.dump_handle is None:
            return
        try:
            # `to` et `type` sont conserves : le type `chat` est une exigence du
            # dispatcher du substitut maitre, la capture doit donc permettre de
            # la verifier.
            self.dump_handle.write(json.dumps(
                {"sessionid": self.sessionid,
                 "to": self.options.master_jid,
                 "type": "chat",
                 "body": json.loads(message)},
                ensure_ascii=False) + "\n")
            self.dump_handle.flush()
        except Exception as exc:  # pragma: no cover - disque plein, etc.
            LOG.warning("Journalisation --dump-frames interrompue : %s", exc)

    def _emit(self, body: str) -> None:
        """Emet une trame (appele depuis la boucle asyncio uniquement)."""
        self.client.send_message(mto=self.options.master_jid, mbody=body, mtype="chat")
        self._dump(body)
        self.frames_sent += 1

    async def _send_task(self) -> None:
        """
        Tache d'emission : unique ecrivain, dans la boucle asyncio.

        Phases : inventaire -> plan du serveur -> archive differentielle ->
        negociation de reprise -> blocs -> accuse final.
        """
        try:
            await self._phase_inventory()
            if self.error is None and not self.ack.is_set():
                await self._phase_transfer()
            if (self.error is None and not self.ack.is_set()
                    and self.options.ack_mode != "none"):
                await self._wait_final_ack()
        except Exception as exc:  # pragma: no cover - depend du reseau
            self.error = "echec de l'emission : %s" % exc
            self.retryable = True
            LOG.error("Echec de l'emission : %s", exc, exc_info=True)
        finally:
            self.stream_done = True
            self._begin_shutdown()

    async def _await_event(self, event, timeout: float) -> bool:
        """
        Attend `event`. Rend la main aussi des qu'une erreur ou un `_done`
        arrive (le serveur peut conclure ou refuser a n'importe quel moment).
        Retourne False uniquement si le delai expire.
        """
        deadline = time.monotonic() + timeout
        while True:
            if event.is_set() or self.ack.is_set() or self.error is not None:
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            try:
                await asyncio.wait_for(event.wait(), timeout=min(0.25, remaining))
            except asyncio.TimeoutError:
                pass

    async def _phase_inventory(self) -> None:
        scan = self.scan
        payload = inventory_json(self.action, self.sessionid, self.metadata,
                                 scan["packages"], scan["certs"])
        messages = build_bigdata_messages(payload, self.sender_full)
        LOG.info("Inventaire : %d package(s), %d certificat(s), %d trame(s) vers %s.",
                 len(scan["packages"]), len(scan["certs"]), len(messages),
                 self.options.master_jid)
        for message in messages:
            self._emit(message)
            await self._backpressure()

        LOG.info("Attente du plan du serveur (%ss max) ...", self.options.plan_timeout)
        if not await self._await_event(self.plan_evt, self.options.plan_timeout):
            self.error = ("aucune reponse du serveur a l'inventaire apres %ss : le "
                          "plugin %s est-il installe et le substitut maitre "
                          "redemarre ?" % (self.options.plan_timeout, self.action))
            LOG.error("%s", self.error)

    def _build_archive(self, need: list) -> dict:
        """Construit (ou reutilise) l'archive differentielle ; execute dans un thread."""
        scan = self.scan
        key = tuple(need)
        cached = scan.get("zip_cache")
        if (cached and cached["key"] == key and os.path.isfile(scan["zip_path"])
                and os.path.getsize(scan["zip_path"]) == cached["info"]["size"]):
            LOG.info("Archive differentielle deja construite : reutilisee.")
            return cached["info"]
        LOG.info("Construction de l'archive differentielle ...")
        info = build_delta_zip(scan["zip_path"], scan["relative_dir"],
                               scan["packages"], scan["certs"], list(need))
        scan["zip_cache"] = {"key": key, "info": info}
        return info

    async def _phase_transfer(self) -> None:
        scan = self.scan
        packages, certs = scan["packages"], scan["certs"]
        need = sorted(self.plan_need)
        if any(not (0 <= i < len(packages) or -len(certs) <= i < 0) for i in need):
            self.error = "plan du serveur incoherent : indices hors inventaire"
            LOG.error("%s", self.error)
            return
        need_packages = [i for i in need if i >= 0]
        need_certs = [i for i in need if i < 0]
        self.packages_sent, self.certs_sent = len(need_packages), len(need_certs)
        self.packages_skipped = len(packages) - len(need_packages)
        self.certs_skipped = len(certs) - len(need_certs)
        LOG.info("Plan du serveur : %d package(s) et %d certificat(s) a envoyer "
                 "(%d package(s), %d certificat(s) deja presents).",
                 len(need_packages), len(need_certs),
                 self.packages_skipped, self.certs_skipped)

        try:
            info = await self.loop.run_in_executor(None, self._build_archive, need)
        except Exception as exc:
            self.error = "construction de l'archive differentielle impossible : %s" % exc
            LOG.error("%s", self.error, exc_info=True)
            return
        self.archive_info = {key: info[key] for key in
                             ("path", "size", "md5", "sha256", "unpacked_size")}
        self.bytes_total = info["size"]
        LOG.info("Archive differentielle : %d o (%d o decompresses), sha256=%s...",
                 info["size"], info["unpacked_size"], info["sha256"][:16])

        meta = build_meta_frame(self.action, self.sessionid, info,
                                self.options.segment_bytes, self.metadata,
                                len(need_packages), len(need_certs))
        self._emit(json.dumps(meta, ensure_ascii=False))
        if not await self._await_event(self.resume_evt, self.options.resume_timeout):
            self.error = ("aucune reponse du serveur a la negociation de reprise "
                          "apres %ss" % self.options.resume_timeout)
            self.retryable = True
            LOG.error("%s", self.error)
            return
        if self.error is not None or self.ack.is_set():
            return
        await self._send_stream()

    async def _send_stream(self) -> None:
        """
        Emet les blocs a partir de celui demande par le serveur. Chaque bloc est
        lu directement dans l'archive : memoire bornee, meme pour plusieurs Go.
        """
        info = self.archive_info
        segment = self.options.segment_bytes
        total = block_total(info["size"], segment)
        start = self.resume_next
        if not 0 <= start < total:
            self.error = ("reprise incoherente demandee par le serveur (bloc %s sur %d)"
                          % (start, total))
            LOG.error("%s", self.error)
            return
        self.resumed_from = start
        if start:
            LOG.info("Reprise : le serveur possede deja %d/%d bloc(s).", start, total)
        LOG.info("Envoi de %d bloc(s) de %d o vers %s.",
                 total - start, segment, self.options.master_jid)

        sent = 0
        with open(info["path"], "rb") as handle:
            for index in range(start, total):
                if self.error is not None or self.ack.is_set():
                    break
                await self._serve_resends()
                frame = make_data_frame(handle, self.action, self.sessionid, index,
                                        segment, info)
                self.bytes_sent = min(self.bytes_total,
                                      self.bytes_sent + frame["data"]["raw_size"])
                self._emit(json.dumps(frame, ensure_ascii=False))
                sent += 1
                if sent % 200 == 0:
                    LOG.info("  ... %d/%d blocs emis", start + sent, total)
                await self._backpressure()
        LOG.info("  ... %d/%d blocs emis", start + sent, total)

    async def _serve_resends(self) -> None:
        """Renvoie les blocs demandes par le serveur (3 renvois maximum par bloc)."""
        while self.resend_requests:
            index = self.resend_requests.pop(0)
            info = self.archive_info
            segment = self.options.segment_bytes
            if info is None or not 0 <= index < block_total(info["size"], segment):
                LOG.warning("Renvoi demande pour un bloc hors bornes (%s) : ignore.", index)
                continue
            count = self.resend_counts.get(index, 0) + 1
            if count > MAX_RESENDS_PER_BLOCK:
                LOG.warning("Bloc %d deja renvoye %d fois : demande ignoree.",
                            index, count - 1)
                continue
            self.resend_counts[index] = count
            LOG.info("Renvoi du bloc %d.", index)
            with open(info["path"], "rb") as handle:
                frame = make_data_frame(handle, self.action, self.sessionid, index,
                                        segment, info)
            self._emit(json.dumps(frame, ensure_ascii=False))
            await self._backpressure()

    async def _wait_final_ack(self) -> None:
        """
        Attend la confirmation du serveur en traitant, au fil de l'eau, les
        demandes de renvoi de bloc (le recepteur ne decouvre qu'un bloc est
        corrompu, ou manquant, qu'apres l'avoir recu).
        """
        LOG.info("Attente de la confirmation du serveur (%ss max) ...",
                 self.options.ack_timeout)
        deadline = time.monotonic() + self.options.ack_timeout
        while time.monotonic() < deadline:
            if self.resend_requests:
                await self._serve_resends()
                continue
            if self.ack.is_set() or self.error is not None:
                return
            try:
                await asyncio.wait_for(self.ack.wait(), timeout=0.5)
            except asyncio.TimeoutError:
                continue

        if self.ack.is_set() or self.error is not None:
            return
        message = ("aucun accuse de reception du serveur apres %ss"
                   % self.options.ack_timeout)
        if self.options.ack_mode == "required":
            self.error = message
            LOG.error("%s", message)
        else:
            LOG.warning("%s : transfert emis mais NON confirme (utiliser "
                        "--ack-mode required pour en faire un echec).", message)

    async def _backpressure(self) -> None:
        """
        Contre-pression : attend que la file d'envoi de slixmpp redescende sous
        le seuil, puis rend la main a la boucle. Si la file ne redescend plus,
        le serveur n'absorbe plus les trames : echec transitoire (retentable)
        plutot qu'une attente jusqu'au delai global.
        """
        stalled_for = 0.0
        while True:
            pending = 0
            queue = getattr(self.client, "waiting_queue", None)
            if queue is not None:
                try:
                    pending = queue.qsize()
                except Exception:  # pragma: no cover
                    pending = 0
            if pending < self.MAX_PENDING_FRAMES:
                break
            await asyncio.sleep(0.25)
            stalled_for += 0.25
            if stalled_for >= self.STALL_TIMEOUT_SECONDS:
                raise RuntimeError(
                    "le serveur n'absorbe plus les trames XMPP (%d en attente "
                    "depuis %ds)" % (pending, int(stalled_for)))
        if self.options.delay_ms:
            await asyncio.sleep(self.options.delay_ms / 1000.0)
        else:
            await asyncio.sleep(0)  # laisse la boucle traiter les reponses

    # -- cycle de vie -----------------------------------------------------

    def _begin_shutdown(self) -> None:
        """Ferme proprement le client (une seule fois), puis arrete la boucle."""
        if self._shutting_down:
            return
        self._shutting_down = True
        try:
            asyncio.ensure_future(self._async_shutdown())
        except Exception:  # pragma: no cover - boucle deja arretee
            self._stop_loop()

    async def _async_shutdown(self) -> None:
        """
        Attend que la file d'envoi soit VIDE avant de fermer le flux.

        Sans cette attente, `disconnect(wait=N)` abandonne les stanzas encore
        en file au bout de N secondes et la boucle s'arrete : un transfert
        tronque serait rapporte comme reussi.
        """
        try:
            queue = getattr(self.client, "waiting_queue", None)
            if queue is not None and not queue.empty():
                # Plancher volontairement bas (5 s) : `--ack-timeout` exprime la
                # patience de l'operateur, il n'y a pas de raison d'attendre plus
                # longtemps que lui pour vider la file.
                drain_timeout = max(5, min(600, self.options.ack_timeout))
                LOG.info("Attente de l'envoi des %d trame(s) restantes ...",
                         queue.qsize())
                try:
                    await asyncio.wait_for(queue.join(), drain_timeout)
                except asyncio.TimeoutError:
                    self.error = ("file d'envoi XMPP non vide apres %ss : "
                                  "transfert incomplet" % drain_timeout)
                    self.retryable = True
                    LOG.error("%s", self.error)
        except Exception as exc:  # pragma: no cover
            LOG.debug("Attente de la file d'envoi : %s", exc)

        try:
            if self.client is not None and self.client.transport:
                future = self.client.disconnect(wait=5)
                if future is not None:
                    await asyncio.wait_for(asyncio.ensure_future(future), timeout=60)
        except Exception as exc:  # pragma: no cover - fermeture best effort
            LOG.debug("Fermeture XMPP : %s", exc)
        finally:
            self._stop_loop()

    def _stop_loop(self) -> None:
        try:
            if self.loop is not None:
                self.loop.stop()
        except Exception:  # pragma: no cover - boucle deja arretee
            pass

    def _on_connect_timeout(self) -> None:
        if self.ready is not None and not self.ready.is_set() and self.error is None:
            self.error = ("delai de connexion depasse (%ss) vers %s:%s"
                          % (self.options.connect_timeout,
                             self.connection["server"], self.connection["port"]))
            self.failure_kind = "connect"
            LOG.error("%s", self.error)
            self._begin_shutdown()

    def _on_total_timeout(self) -> None:
        if not self.stream_done and self.error is None:
            self.error = ("delai global depasse (%ss) : transfert interrompu"
                          % self.options.total_timeout)
            self.retryable = True
            LOG.error("%s", self.error)
            self._begin_shutdown()

    def _new_loop(self):
        """Cree la boucle et les evenements qui lui sont rattaches."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop
        self.ready = asyncio.Event()
        self.ack = asyncio.Event()
        self.plan_evt = asyncio.Event()
        self.resume_evt = asyncio.Event()
        return loop

    def _cleanup(self, loop) -> None:
        """Nettoyage local apres l'arret de la boucle (client deja ferme)."""
        try:
            pending = [task for task in asyncio.all_tasks(loop) if not task.done()]
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:  # pragma: no cover
            pass
        try:
            loop.close()
        except Exception:  # pragma: no cover
            pass

    def run(self) -> dict:
        """
        Execute la connexion puis le transfert, et retourne un dictionnaire de
        resultat. Ne leve pas : les erreurs sont placees dans `error`.
        """
        started = time.time()
        client_class = self._make_client()
        loop = self._new_loop()

        self.client = client_class(self.connection["jid"], self.connection["password"])
        self.client.ssl_context = build_ssl_context(
            self.options.tls_verify, self.options.ca_cert)

        address = (self.connection["server"], self.connection["port"])
        LOG.info("Connexion XMPP %s:%s (jid=%s, tls_verify=%s)",
                 address[0], address[1], self.connection["jid"],
                 bool(self.options.tls_verify))

        try:
            # `disable_starttls` est le seul levier reel de slixmpp 1.8.5 ;
            # `force_starttls` n'y est jamais lu (voir `tls_active`).
            self.client.connect(
                address=address,
                force_starttls=None,
                disable_starttls=bool(self.options.no_starttls))
        except Exception as exc:
            self.error = "connexion impossible a %s:%s (%s)" % (
                address[0], address[1], exc)
            self.failure_kind = "connect"
            self._cleanup(loop)
            return self._result(started, "connect")

        loop.call_later(self.options.connect_timeout, self._on_connect_timeout)
        loop.call_later(self.options.total_timeout, self._on_total_timeout)

        try:
            loop.run_forever()
        finally:
            self._cleanup(loop)

        if self.task is not None and not self.task.done():
            self.task.cancel()

        status = "ok"
        if self.error:
            # Une impossibilite de se connecter/authentifier doit sortir en
            # code 3 (prerequis reseau), pas en code 5 (echec de transfert).
            status = "connect" if self.failure_kind == "connect" else "error"
        elif self.options.ack_mode != "none" and not (self.ack and self.ack.is_set()):
            status = "unconfirmed"
        return self._result(started, status)

    def _result(self, started: float, status: str) -> dict:
        """Resultat machine, ecrit sur disque et sur stdout par `main()`."""
        if self.failure_kind == "connect":
            exit_code = EXIT_CONNECT
        elif status == "ok":
            exit_code = EXIT_OK
        elif status == "unconfirmed":
            exit_code = EXIT_OK if self.options.ack_mode == "optional" else EXIT_TRANSFER
        elif status == "connect":
            exit_code = EXIT_CONNECT
        else:
            exit_code = EXIT_TRANSFER

        return {
            "schema": SCHEMA,
            "status": status,
            "exit_code": exit_code,
            "retryable": bool(self.retryable),
            "sessionid": self.sessionid,
            "action": self.action,
            "jid": self.connection["jid"],
            "master_jid": self.options.master_jid,
            "server": self.connection["server"],
            "port": self.connection["port"],
            "frames_sent": self.frames_sent,
            "bytes": self.bytes_sent,
            "bytes_total": self.bytes_total,
            "nothing_to_send": self.nothing_to_send,
            "packages_sent": self.packages_sent,
            "packages_skipped": self.packages_skipped,
            "certs_sent": self.certs_sent,
            "certs_skipped": self.certs_skipped,
            "resumed_from_block": self.resumed_from,
            "archive": self.archive_info,
            "depot_path": self.depot_path,
            "confirmed": bool(self.ack and self.ack.is_set()),
            "ack_action": (self.ack_payload or {}).get("action"),
            "duration_s": round(time.time() - started, 2),
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def prepare_inventory(options: argparse.Namespace, metadata: dict) -> dict:
    """
    Inventorie le dossier de travail (une seule fois, meme en cas de nouvelle
    tentative : le hachage d'un export de plusieurs Go est couteux).
    """
    if not options.staging:
        raise XmppFailed("Aucun dossier de travail fourni (--staging).")
    staging = os.path.abspath(options.staging)
    if not os.path.isdir(staging):
        raise XmppFailed("Dossier de travail introuvable : %s" % staging)
    relative_dir = metadata.get("relative_dir")
    if not valid_relative_dir(relative_dir):
        raise XmppFailed("relative_dir absent ou invalide dans les metadonnees : %r"
                         % (relative_dir,))
    root = os.path.join(staging, *relative_dir.split("/"))
    if not os.path.isdir(root):
        raise XmppFailed("Arborescence %s introuvable dans %s" % (relative_dir, staging))

    LOG.info("Inventaire de %s ...", root)
    scan = scan_staging(root)
    for warning in scan["warnings"]:
        LOG.warning("%s", warning)
    if not scan["packages"] and not scan["certs"]:
        raise XmppFailed("Rien a envoyer : aucun package de drivers ni certificat "
                         "exploitable dans %s" % root)
    scan["relative_dir"] = relative_dir
    scan["zip_path"] = options.delta_zip or os.path.join(
        os.path.dirname(staging), "extract-drivers-delta.zip")
    LOG.info("Inventaire : %d package(s), %d certificat(s), %d Mo.",
             len(scan["packages"]), len(scan["certs"]),
             sum(p["size"] for p in scan["packages"]) // (1024 * 1024))
    return scan


def transfer(options: argparse.Namespace, metadata: dict, scan: dict | None) -> dict:
    """
    Execute une tentative de transfert ; retourne le resultat.

    En mode `--check`, aucun inventaire n'est requis : on valide seulement la
    configuration, la resolution du JID, la connexion et l'authentification.
    """
    metadata = dict(metadata)

    # --- Configuration agent --------------------------------------------
    try:
        parser = read_ini(options.config)
    except FileNotFoundError as exc:
        raise XmppFailed(str(exc))
    except configparser.Error as exc:
        raise XmppFailed("Fichier de configuration illisible (%s) : %s"
                         % (options.config, exc))
    agent_package_dir = find_agent_package_dir()

    # `confParameter` de l'agent lit toujours le chemin standard
    # (C:\Program Files\Medulla\etc\agentconf.ini) : il ne peut pas honorer un
    # `--config` explicite. Melanger les deux sources donnerait un JID issu d'un
    # fichier et des parametres de connexion issus d'un autre -> on resout
    # alors le JID de facon autonome, sur le fichier reellement fourni.
    config_source = options.config_source
    if config_source == "auto" and getattr(options, "config_explicit", False):
        LOG.info("--config explicite : resolution autonome du JID (le JID de "
                 "l'agent proviendrait d'un autre fichier).")
        config_source = "minimal"

    resource = options.resource or ("extractdrivers-%d" % os.getpid())
    jid, jid_source = options.jid, "override"
    if not jid:
        if config_source in ("auto", "agent"):
            try:
                jid, jid_source = derive_jid_via_agent(options.agent_type, resource)
            except Exception as exc:
                if config_source == "agent":
                    raise XmppFailed(
                        "JID introuvable via l'agent (%s). Reessayer avec "
                        "--config-source minimal." % exc)
                LOG.warning("Lecture du JID via l'agent impossible (%s) : "
                            "repli sur la lecture autonome de agentconf.ini.", exc)
                jid, jid_source = derive_jid_minimal(
                    parser, agent_package_dir, resource)
        else:
            jid, jid_source = derive_jid_minimal(parser, agent_package_dir, resource)
    else:
        jid = jid if "/" in jid else "%s/%s" % (jid, resource)

    connection = resolve_connection(parser, jid, options)
    if not connection["server"]:
        raise XmppFailed(
            "Serveur XMPP introuvable : renseigner [connection] server ou "
            "[configuration_server] confserver dans %s, ou utiliser --server."
            % options.config)
    if not connection["password"]:
        raise XmppFailed(
            "Mot de passe XMPP introuvable ([configuration_server] confpassword) "
            "dans %s." % options.config)

    LOG.info("Identite XMPP (%s) : %s", jid_source, connection["jid"])
    LOG.info("Substitut destinataire : %s", options.master_jid)

    if options.check:
        # Copie AVANT construction de l'uploader (qui conserve la reference) :
        # on ne mute pas le Namespace de `main()`, partage avec la boucle de
        # tentative, et le transporteur voit bien l'absence d'attente d'ACK.
        options = argparse.Namespace(**vars(options))
        options.ack_mode = "none"
        LOG.info("Mode --check : test de connexion uniquement (aucun transfert).")

    # Un identifiant par tentative : le serveur lie son etat a la session, la
    # reprise s'appuie sur l'empreinte de l'archive, pas sur la session.
    sessionid = new_sessionid("drivers")
    uploader = DriversUploader(options, connection, options.action, sessionid,
                               connection["jid"])
    uploader.dump_handle = getattr(options, "_dump_handle", None)
    uploader.metadata = metadata
    uploader.scan = scan

    result = uploader.run()
    if scan is not None:
        result["relative_dir"] = scan["relative_dir"]
        result["inventory"] = {"packages": len(scan["packages"]),
                               "certs": len(scan["certs"]),
                               "warnings": list(scan["warnings"])}
    return result


# ---------------------------------------------------------------------------
# Mode --self-test : validation hors ligne du protocole
# ---------------------------------------------------------------------------

def self_test() -> int:
    """
    Valide hors ligne (sans reseau ni slixmpp) l'inventaire, l'archive
    differentielle deterministe et le decoupage en blocs.

    Portee : coherence interne de l'emetteur. La conformite avec le recepteur
    reel (`server/plugin_extract_drivers.py`) est verifiee par
    `tests/test_protocol.py`, qui execute les deux ensemble.
    """
    import tempfile

    failures = []

    def check(name, condition, detail=""):
        state = "OK " if condition else "ECHEC"
        print("  [%s] %s%s" % (state, name, (" - " + detail) if detail else ""))
        if not condition:
            failures.append(name)

    print("Self-test du protocole de transport drivers/certificats v2")

    # 1) bigdata (inventaire) : court, volumineux, compressible
    small = json.dumps({"action": "extract_drivers", "sessionid": "s1",
                        "ret": 0, "base64": False, "data": {"type": "inventory"}})
    messages = build_bigdata_messages(small, "pc@pulse/res")
    check("bigdata : message court non decoupe",
          len(messages) == 1 and reassemble_bigdata(messages) == small)
    big = json.dumps({"action": "extract_drivers", "sessionid": "s2", "ret": 0,
                      "base64": False,
                      "data": {"blob": base64.b64encode(os.urandom(300000)).decode()}})
    messages = build_bigdata_messages(big, "pc@pulse/res")
    check("bigdata : message volumineux decoupe et reassemble",
          len(messages) > 1 and reassemble_bigdata(messages) == big,
          "%d trames" % len(messages))
    compact = json.dumps({"action": "extract_drivers", "sessionid": "s2b", "ret": 0,
                          "base64": False, "data": {"blob": "x" * 400000}})
    messages = build_bigdata_messages(compact, "pc@pulse/res")
    check("bigdata : charge compressible = 1 trame big_data",
          len(messages) == 1 and json.loads(messages[0])["action"] == "big_data"
          and reassemble_bigdata(messages) == compact)

    with tempfile.TemporaryDirectory() as temporary:
        root = os.path.join(temporary, "Windows10", "DellInc", "OptiPlex")
        files = {
            "DRIVERS/Net/rtl.inf_a/rtl.inf": os.urandom(3000),
            "DRIVERS/Net/rtl.inf_a/sub/rtl.sys": os.urandom(70000),
            "DRIVERS/Display/gpu.inf_b/gpu.inf": b"gpu" * 100,
            "DRIVERS/Display/bad:name/x.inf": b"x",
            "DRIVERS/Net/rtl.inf_a/vide/.keep": b"",
            "CERTS/AABBCCDDEEFF0011.cer": os.urandom(900),
            "CERTS/notacert.txt": b"x",
        }
        for rel, content in files.items():
            path = os.path.join(root, *rel.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(content)

        # 2) inventaire
        scan = scan_staging(root)
        ids = [p["id"] for p in scan["packages"]]
        check("inventaire : packages valides tries, nom invalide exclu",
              ids == ["DRIVERS/Display/gpu.inf_b", "DRIVERS/Net/rtl.inf_a"], str(ids))
        check("inventaire : 1 certificat, fichier parasite ignore",
              [c["thumbprint"] for c in scan["certs"]] == ["AABBCCDDEEFF0011"])
        check("inventaire : avertissements (nom invalide + fichier ignore)",
              len(scan["warnings"]) >= 2, "%d" % len(scan["warnings"]))
        net = scan["packages"][1]
        check("inventaire : comptage fichiers/octets",
              net["files"] == 3 and net["size"] == 73000, "%d/%d" % (net["files"], net["size"]))
        check("inventaire : empreinte stable et recalculable",
              package_digest(os.path.join(root, "DRIVERS", "Net", "rtl.inf_a"))
              == (net["digest"], net["files"], net["size"]))

        # 3) archive differentielle deterministe
        need = [1, -1]
        zip_a = os.path.join(temporary, "a.zip")
        zip_b = os.path.join(temporary, "b.zip")
        info_a = build_delta_zip(zip_a, "Windows10/DellInc/OptiPlex",
                                 scan["packages"], scan["certs"], need)
        time.sleep(1.1)
        info_b = build_delta_zip(zip_b, "Windows10/DellInc/OptiPlex",
                                 scan["packages"], scan["certs"], need)
        check("archive : deterministe (meme SHA-256 a 1 s d'ecart)",
              info_a["sha256"] == info_b["sha256"], info_a["sha256"][:16])
        import zipfile
        with zipfile.ZipFile(zip_a) as zf:
            names = zf.namelist()
            check("archive : uniquement le delta, tri alphabetique",
                  names == sorted(names) and len(names) == 4
                  and all(n.startswith("Windows10/DellInc/OptiPlex/") for n in names)
                  and not any("Display" in n for n in names), str(names))
            check("archive : pas de metadata.json (non deterministe)",
                  not any(n.endswith("metadata.json") for n in names))
            check("archive : contenu identique a la source",
                  zf.read("Windows10/DellInc/OptiPlex/CERTS/AABBCCDDEEFF0011.cer")
                  == files["CERTS/AABBCCDDEEFF0011.cer"]
                  and zf.testzip() is None)
        check("archive : taille decompressee annoncee",
              info_a["unpacked_size"] == 73000 + 900, str(info_a["unpacked_size"]))

        # 4) blocs : decoupage, reprise, alteration
        size = info_a["size"]
        seg = 4096
        total = block_total(size, seg)
        meta_frame = build_meta_frame("extract_drivers", "s3", info_a, seg,
                                      {"relative_dir": "Windows10/DellInc/OptiPlex"}, 2, 1)
        check("meta : champs v2", meta_frame["data"]["type"] == "meta"
              and meta_frame["data"]["delta"] is True
              and meta_frame["data"]["segment_total"] == total
              and meta_frame["data"]["unpacked_size"] == info_a["unpacked_size"])
        blocks = {}
        with open(zip_a, "rb") as handle:
            for index in range(total):
                frame = make_data_frame(handle, "extract_drivers", "s3", index, seg, info_a)
                data = frame["data"]
                raw = zlib.decompress(base64.b64decode(data["data_b64"]))
                if md5_bytes(raw) != data["md5_segment"]:
                    raise AssertionError("md5 bloc")
                blocks[index] = raw
                if index == total - 1:
                    check("blocs : dernier bloc marque last avec empreintes",
                          data["last"] is True
                          and data["sha256_total"] == info_a["sha256"]
                          and data["md5_total"] == info_a["md5"])
        content = b"".join(blocks[i] for i in range(total))
        with open(zip_a, "rb") as handle:
            check("blocs : reassemblage fidele", content == handle.read())
        with open(zip_a, "rb") as handle:
            frame = make_data_frame(handle, "extract_drivers", "s3", total - 1, seg, info_a)
            check("blocs : lecture directe d'un bloc quelconque (reprise/renvoi)",
                  zlib.decompress(base64.b64decode(frame["data"]["data_b64"]))
                  == blocks[total - 1])

    print("")
    if failures:
        print("Self-test : ECHEC (%d) -> %s" % (len(failures), ", ".join(failures)))
        return 1
    print("Self-test : OK (tous les controles passes)")
    return 0


# ---------------------------------------------------------------------------
# Ligne de commande
# ---------------------------------------------------------------------------

def segment_bytes(value: str) -> int:
    """Type argparse : borne `--segment-bytes` (0 ou negatif = division par 0)."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("valeur entiere attendue, recu %r" % value)
    if not (MIN_SEGMENT_BYTES <= number <= MAX_SEGMENT_BYTES):
        raise argparse.ArgumentTypeError(
            "doit etre compris entre %d et %d octets (recu %d)"
            % (MIN_SEGMENT_BYTES, MAX_SEGMENT_BYTES, number))
    return number


def positive_int(value: str) -> int:
    """Type argparse : entier strictement positif."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("valeur entiere attendue, recu %r" % value)
    if number <= 0:
        raise argparse.ArgumentTypeError("doit etre strictement positif (recu %d)"
                                         % number)
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Send-DriversOverXmpp.py",
        description="Transfere les drivers et certificats extraits vers le serveur "
                    "Medulla via XMPP (protocole v2 : inventaire, envoi "
                    "differentiel, reprise ; aucun SMB).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemple :\n"
               "  Send-DriversOverXmpp.py --staging C:\\\\Temp\\\\staging \\\n"
               "      --metadata C:\\\\Temp\\\\staging\\\\metadata.json \\\n"
               "      --log C:\\\\ProgramData\\\\Medulla\\\\ExtractDrivers\\\\xmpp-send.log\n")

    parser.add_argument("--staging",
                        help="Dossier de travail : <staging>/<OS>/<Fabricant>/<Modele>/"
                             "DRIVERS|CERTS (obligatoire sauf --check/--self-test).")
    parser.add_argument("--metadata",
                        help="Fichier JSON de metadonnees produit par le script "
                             "PowerShell (defaut : <staging>/metadata.json).")
    parser.add_argument("--delta-zip", default=None,
                        help="Chemin de l'archive differentielle temporaire (defaut : "
                             "extract-drivers-delta.zip a cote du dossier de travail).")
    parser.add_argument("--keep-archive", action="store_true",
                        help="Conserve l'archive differentielle apres un succes.")
    parser.add_argument("--action", default="extract_drivers",
                        help="Action XMPP logique (nom du plugin serveur). "
                             "Defaut : extract_drivers.")
    parser.add_argument("--master-jid", default=DEFAULT_MASTER_JID,
                        help="JID du substitut destinataire. Defaut : master@pulse.")
    parser.add_argument("--config", default=None,
                        help="Chemin de agentconf.ini (defaut : installation "
                             "standard Medulla).")
    parser.add_argument("--config-source", choices=["auto", "agent", "minimal"],
                        default="auto",
                        help="Origine du JID : pile de l'agent, lecture autonome, "
                             "ou auto.")
    parser.add_argument("--agent-type", default="machine",
                        help="Type d'agent lu dans la configuration "
                             "(machine par defaut).")
    parser.add_argument("--jid", default=None, help="Force le JID complet (diagnostic).")
    parser.add_argument("--resource", default=None,
                        help="Ressource XMPP locale (une ressource differente de "
                             "celle de l'agent est necessaire pour ne pas le "
                             "deconnecter).")
    parser.add_argument("--server", default=None, help="Force le serveur XMPP.")
    parser.add_argument("--port", type=positive_int, default=None,
                        help="Force le port XMPP.")
    parser.add_argument("--tls-verify", type=int, choices=[0, 1], default=1,
                        help="Verification du certificat TLS. Defaut : 1.")
    parser.add_argument("--ca-cert", default=None,
                        help="Bundle CA a utiliser (CA Medulla privee).")
    parser.add_argument("--require-starttls", action="store_true",
                        help="Echouer si la session n'est pas chiffree "
                             "(applique par le transporteur : slixmpp 1.8.5 "
                             "n'applique pas force_starttls).")
    parser.add_argument("--no-starttls", action="store_true",
                        help="Ne jamais monter en TLS (diagnostic uniquement ; "
                             "incompatible avec --require-starttls).")
    parser.add_argument("--segment-bytes", type=segment_bytes,
                        default=DEFAULT_SEGMENT_BYTES,
                        help="Taille des blocs bruts de l'archive "
                             "(defaut : 25000, bornes %d-%d)."
                             % (MIN_SEGMENT_BYTES, MAX_SEGMENT_BYTES))
    parser.add_argument("--delay-ms", type=int, default=0,
                        help="Pause supplementaire entre deux trames (ms). "
                             "Defaut : 0 (contre-pression automatique).")
    parser.add_argument("--connect-timeout", type=positive_int, default=30,
                        help="Delai maximum de connexion/authentification (s). "
                             "Defaut : 30.")
    parser.add_argument("--plan-timeout", type=positive_int, default=120,
                        help="Attente du plan du serveur apres l'inventaire (s). "
                             "Defaut : 120.")
    parser.add_argument("--resume-timeout", type=positive_int, default=120,
                        help="Attente de la reponse de reprise apres la trame meta "
                             "(s). Defaut : 120.")
    parser.add_argument("--ack-timeout", type=positive_int, default=300,
                        help="Attente de l'ACK final du serveur (s). Defaut : 300.")
    parser.add_argument("--total-timeout", type=positive_int, default=3600,
                        help="Delai global du transfert (s). Defaut : 3600.")
    parser.add_argument("--ack-mode", choices=["none", "optional", "required"],
                        default="required",
                        help="Exigence d'accuse de reception final. Defaut : required. "
                             "(Le plan et la reprise sont, eux, toujours negocies.)")
    parser.add_argument("--max-retries", type=positive_int, default=3,
                        help="Tentatives de transfert. Defaut : 3.")
    parser.add_argument("--retry-delay", type=positive_int, default=15,
                        help="Delai entre deux tentatives (s). Defaut : 15.")
    parser.add_argument("--log", default=None, help="Fichier de journal.")
    parser.add_argument("--result", default=None, help="Fichier JSON de resultat.")
    parser.add_argument("--dump-frames", default=None,
                        help="Ecrit les trames emises (JSONL) pour validation "
                             "hors ligne. Le fichier est reinitialise au debut du "
                             "script et contient toutes les tentatives.")
    parser.add_argument("--check", action="store_true",
                        help="Teste la connexion XMPP puis quitte (aucun transfert).")
    parser.add_argument("--self-test", action="store_true",
                        help="Valide le protocole hors ligne (sans reseau).")
    parser.add_argument("--verbose", action="store_true", help="Journal detaille.")
    return parser


def load_metadata(path: str | None) -> dict:
    """Charge le JSON de metadonnees produit par le script PowerShell."""
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv=None) -> int:
    parser = build_parser()
    options = parser.parse_args(argv)

    if options.self_test:
        return self_test()

    # Combinaison contradictoire : sans garde-fou, la session serait
    # systematiquement refusee avec un message trompeur.
    if options.require_starttls and options.no_starttls:
        parser.error("--require-starttls et --no-starttls sont incompatibles")

    # Distingue "chemin par defaut" de "chemin impose par l'operateur" :
    # voir la note sur la coherence de la source du JID dans `transfer()`.
    options.config_explicit = options.config is not None
    if not options.config:
        options.config = (DEFAULT_AGENT_CONF_WINDOWS
                          if sys.platform.startswith("win")
                          else DEFAULT_AGENT_CONF_UNIX)

    setup_logging(options.log, options.verbose)

    if not options.check and not options.staging:
        parser.error("--staging est obligatoire (sauf avec --check ou --self-test)")

    # Fichier de trames : reinitialise une fois pour toutes les tentatives, afin
    # qu'un echec au premier essai reste analysable.
    if options.dump_frames:
        try:
            directory = os.path.dirname(os.path.abspath(options.dump_frames))
            if directory:
                os.makedirs(directory, exist_ok=True)
            options._dump_handle = open(options.dump_frames, "w", encoding="utf-8")
        except OSError as exc:
            LOG.error("Impossible d'ouvrir --dump-frames (%s) : %s",
                      options.dump_frames, exc)
            options._dump_handle = None
    else:
        options._dump_handle = None

    result = None
    try:
        metadata_path = options.metadata
        if not metadata_path and options.staging:
            metadata_path = os.path.join(options.staging, "metadata.json")
        metadata = load_metadata(metadata_path) if metadata_path else {}

        # Inventaire unique : hacher plusieurs Go est couteux, et l'archive
        # differentielle construite est reutilisee d'une tentative a l'autre.
        scan = None if options.check else prepare_inventory(options, metadata)

        answer = None
        for attempt in range(1, max(1, options.max_retries) + 1):
            if attempt > 1:
                LOG.warning("Nouvelle tentative %d/%d dans %ds ...",
                            attempt, options.max_retries, options.retry_delay)
                time.sleep(options.retry_delay)
            answer = transfer(options, metadata, scan)
            status = answer.get("status")
            if status in ("ok", "unconfirmed"):
                break
            if answer.get("exit_code") in (EXIT_CONNECT, EXIT_PREREQ):
                break  # Connexion/config : retenter n'apporte rien ici.
            if not answer.get("retryable"):
                # Refus explicite du serveur (SHA invalide, droits, chemin) ou
                # absence d'ACK : renvoyer une nouvelle fois toute l'archive
                # couterait cher sans changer le resultat.
                LOG.warning("Echec non transitoire : aucune nouvelle tentative.")
                break
        result = answer or {"status": "error", "exit_code": EXIT_UNEXPECTED,
                            "error": "aucune tentative executee"}
        if (scan and result.get("status") in ("ok", "unconfirmed")
                and not options.keep_archive):
            for leftover in (scan["zip_path"], scan["zip_path"] + ".tmp"):
                try:
                    os.remove(leftover)
                except OSError:
                    pass

    except XmppFailed as exc:
        LOG.error("%s", exc)
        result = {"schema": SCHEMA, "status": "error", "exit_code": EXIT_PREREQ,
                  "error": str(exc)}
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        # Fichier de metadonnees absent ou illisible : c'est un probleme de
        # prerequis/configuration, pas une erreur interne (code 2, pas 99).
        LOG.error("Metadonnees illisibles (%s) : %s", options.metadata, exc)
        result = {"schema": SCHEMA, "status": "error", "exit_code": EXIT_PREREQ,
                  "error": "metadonnees illisibles : %s" % exc}
    except Exception as exc:  # pragma: no cover - filet de securite
        LOG.error("Erreur inattendue : %s", exc, exc_info=True)
        result = {"schema": SCHEMA, "status": "error", "exit_code": EXIT_UNEXPECTED,
                  "error": str(exc)}
    finally:
        if options._dump_handle is not None:
            try:
                options._dump_handle.close()
            except Exception:  # pragma: no cover
                pass

    # Resultat machine : fichier + stdout (le script PowerShell lit le fichier,
    # stdout est journalise pour le diagnostic).
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if options.result:
        try:
            directory = os.path.dirname(os.path.abspath(options.result))
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(options.result, "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
        except OSError as exc:
            LOG.error("Ecriture du resultat impossible (%s) : %s", options.result, exc)

    exit_code = int(result.get("exit_code", EXIT_UNEXPECTED))
    level = logging.INFO if exit_code == EXIT_OK else logging.ERROR
    LOG.log(level, "Resultat : %s", payload)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
