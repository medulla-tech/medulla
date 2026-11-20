# -*- coding: utf-8 -*-
"""
plugin_extract_drivers.py - recepteur serveur (substitut maitre) v2
===================================================================

A deposer dans `pluginsmastersubstitute/` puis redemarrer le service du
substitut maitre. Le nom doit correspondre a l'action envoyee par les postes
(`extract_drivers`).

Protocole `medulla.extractdrivers.v2` (voir PROTOCOLE.md) :

  poste -> serveur  inventory   liste des packages/certificats du poste
  serveur -> poste  _plan       ce qui MANQUE au depot (ou _done si rien)
  poste -> serveur  meta        archive delta (uniquement le manquant)
  serveur -> poste  _resume     premier bloc attendu (reprise apres coupure)
  poste -> serveur  data...     blocs
  serveur -> poste  _done       depot ecrit  /  _error  echec

Regles de securite et d'exploitation :
  * le serveur NE SUPPRIME JAMAIS le contenu existant du depot ;
  * `relative_dir` est valide (3 composants surs), le sous-repertoire du
    depot est impose par le serveur (`DEPOT_SUBDIR`), jamais par le poste ;
  * toute entree d'archive est controlee (zip-slip, liens, doublons, tailles)
    et l'extraction est faite dans un repertoire temporaire, jamais
    directement dans le depot ;
  * les packages sont installes un par un, apres verification de leur
    empreinte contre l'inventaire ;
  * l'etat de reprise est sur disque (`<depot>[/<DEPOT_SUBDIR>]/.incoming/`),
    l'etat de session est porte par `xmppobject` : Medulla peut recharger le
    module du plugin a chaque appel, des variables globales seraient perdues.
"""

import hashlib
import json
import logging
import os
import re
import shutil
import stat
import threading
import time
import base64
import zipfile
import zlib

logger = logging.getLogger()

plugin = {"VERSION": "2.0", "NAME": "extract_drivers", "TYPE": "mastersub"}

# ---------------------------------------------------------------------------
# Configuration (surchargeable par variables d'environnement)
# ---------------------------------------------------------------------------

#: Racine du depot VUE PAR LE SERVEUR (partage monte localement).
DEPOT_ROOT = os.environ.get("MEDULLA_DRIVERS_DEPOT", "/mnt/drivers")

#: Sous-repertoire du depot, impose par le serveur. Vide : les modeles sont
#: ecrits directement sous DEPOT_ROOT (disposition de l'ancien partage SMB).
DEPOT_SUBDIR = os.environ.get("MEDULLA_DRIVERS_SUBDIR", "drivers").strip("/\\ ")

#: True : refuse d'ecrire si DEPOT_ROOT n'est pas un point de montage (evite
#: d'ecrire sur le disque local quand le partage n'est pas monte).
REQUIRE_MOUNTPOINT = os.environ.get("MEDULLA_DRIVERS_REQUIRE_MOUNT", "0") == "1"

SCHEMA = "medulla.extractdrivers.v2"
INCOMING = ".incoming"

MAX_ARCHIVE_BYTES = 8 * 1024 ** 3
MAX_UNPACKED_BYTES = 24 * 1024 ** 3
MAX_ENTRIES = 200000
MAX_PACKAGES = 20000
MAX_CERTS = 5000
MIN_FREE_MARGIN = 1024 ** 3
MIN_SEGMENT_BYTES = 1024
MAX_SEGMENT_BYTES = 48000
MAX_RESEND_PER_BLOCK = 3
PLAN_CHUNK = 4000
STATE_FLUSH_EVERY = 40
SESSION_TTL = 6 * 3600
ACTIVE_TTL = 180
STALE_SECONDS = 7 * 86400

_COMPONENT_RE = re.compile(r'^[^\x00-\x1f\x7f\\/:*?"<>|]{1,200}$')
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MD5_RE = re.compile(r"^[0-9a-f]{32}$")
_THUMB_RE = re.compile(r"^[0-9A-Fa-f]{8,128}$")


class PluginError(Exception):
    """Refus explicite : le message est renvoye au poste."""

    def __init__(self, message, retryable=False):
        super().__init__(message)
        self.retryable = retryable


# ---------------------------------------------------------------------------
# Validation des noms
# ---------------------------------------------------------------------------

def valid_component(value):
    return (isinstance(value, str) and bool(_COMPONENT_RE.match(value))
            and value not in (".", "..") and value == value.strip()
            and not value.endswith("."))


def clean_relative_dir(value):
    """`<OS>/<Fabricant>/<Modele>` : exactement 3 composants surs."""
    parts = value.split("/") if isinstance(value, str) else []
    if len(parts) != 3 or not all(valid_component(p) and not p.startswith(".")
                                  for p in parts):
        raise PluginError("relative_dir invalide : %r" % (value,))
    return "/".join(parts)


def clean_package_id(value):
    """`DRIVERS/<Classe>/<package>`."""
    parts = value.split("/") if isinstance(value, str) else []
    if len(parts) != 3 or parts[0] != "DRIVERS" or not all(
            valid_component(p) for p in parts):
        raise PluginError("identifiant de package invalide : %r" % (value,))
    return "/".join(parts)


def clean_thumbprint(value):
    if not isinstance(value, str) or not _THUMB_RE.match(value):
        raise PluginError("thumbprint invalide : %r" % (value,))
    return value


# ---------------------------------------------------------------------------
# Empreintes
# ---------------------------------------------------------------------------

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def md5_file(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def walk_files(root):
    """[(chemin relatif en '/', chemin complet)] triee, liens symboliques ignores."""
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


def package_digest(root):
    """
    Empreinte canonique d'un package : sha256 des lignes
    `<chemin relatif>\\t<taille>\\t<sha256 du fichier>\\n`, triees par chemin.
    DOIT rester identique a `package_digest` de Send-DriversOverXmpp.py.
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


def dir_signature(root):
    """(nombre de fichiers, octets) d'un repertoire : comparaison peu couteuse."""
    if not os.path.isdir(root):
        return 0, 0
    files = 0
    total = 0
    for _rel, full in walk_files(root):
        files += 1
        total += os.path.getsize(full)
    return files, total


# ---------------------------------------------------------------------------
# Etat, reponses, depot
# ---------------------------------------------------------------------------

def get_state(xmppobject):
    default = {"lock": threading.RLock(), "sessions": {}, "active": {}}
    return vars(xmppobject).setdefault("extract_drivers_state", default)


def bare(jid):
    return str(jid).split("/")[0].lower()


def reply(xmppobject, msg, action, sessionid, suffix, data, ret=0):
    body = {"action": "%s_%s" % (action, suffix), "sessionid": sessionid,
            "ret": ret, "base64": False, "data": data}
    xmppobject.send_message(mto=msg["from"], mbody=json.dumps(body), mtype="chat")


def depot_base():
    root = DEPOT_ROOT
    if not os.path.isdir(root):
        raise PluginError("depot introuvable cote serveur (%s) : partage non monte ?"
                          % root)
    if REQUIRE_MOUNTPOINT and not os.path.ismount(root):
        raise PluginError("le depot n'est pas un point de montage (%s)" % root)
    if ".." in DEPOT_SUBDIR.replace("\\", "/").split("/"):
        raise PluginError("MEDULLA_DRIVERS_SUBDIR invalide : %r" % DEPOT_SUBDIR)
    base = os.path.join(root, DEPOT_SUBDIR) if DEPOT_SUBDIR else root
    os.makedirs(os.path.join(base, INCOMING), exist_ok=True)
    return base


def cleanup_stale(base, active_shas):
    """Supprime les restes d'envois abandonnes (le contenu du depot n'est jamais touche)."""
    incoming = os.path.join(base, INCOMING)
    limit = time.time() - STALE_SECONDS
    for name in os.listdir(incoming):
        if name.split(".")[0] in active_shas:
            continue
        path = os.path.join(incoming, name)
        try:
            if os.path.getmtime(path) < limit:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Phase 1 : inventaire -> plan
# ---------------------------------------------------------------------------

def parse_inventory(data):
    if data.get("schema") != SCHEMA:
        raise PluginError("schema non supporte : %r (attendu %s)"
                          % (data.get("schema"), SCHEMA))
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise PluginError("metadata absentes de l'inventaire")
    relative_dir = clean_relative_dir(metadata.get("relative_dir"))

    packages = data.get("packages")
    certs = data.get("certs")
    if not isinstance(packages, list) or not isinstance(certs, list):
        raise PluginError("inventaire mal forme (packages/certs)")
    if len(packages) > MAX_PACKAGES or len(certs) > MAX_CERTS:
        raise PluginError("inventaire trop volumineux")

    seen = set()
    clean_packages = []
    for item in packages:
        if not isinstance(item, dict):
            raise PluginError("package mal forme")
        pid = clean_package_id(item.get("id"))
        if pid in seen:
            raise PluginError("package en double : %s" % pid)
        seen.add(pid)
        files, size, digest = item.get("files"), item.get("size"), item.get("digest")
        if (not isinstance(files, int) or not isinstance(size, int) or files < 1
                or size < 0 or not isinstance(digest, str)
                or not _SHA256_RE.match(digest)):
            raise PluginError("package %s : champs invalides" % pid)
        clean_packages.append({"id": pid, "files": files, "size": size,
                               "digest": digest})

    seen = set()
    clean_certs = []
    for item in certs:
        if not isinstance(item, dict):
            raise PluginError("certificat mal forme")
        thumb = clean_thumbprint(item.get("thumbprint"))
        if thumb.lower() in seen:
            raise PluginError("certificat en double : %s" % thumb)
        seen.add(thumb.lower())
        size, sha = item.get("size"), item.get("sha256")
        if (not isinstance(size, int) or size < 0 or not isinstance(sha, str)
                or not _SHA256_RE.match(sha)):
            raise PluginError("certificat %s : champs invalides" % thumb)
        clean_certs.append({"thumbprint": thumb, "size": size, "sha256": sha})

    return metadata, relative_dir, clean_packages, clean_certs


def compute_need(base, relative_dir, packages, certs):
    """Indices manquants : packages (>= 0) et certificats (-(i+1))."""
    model_dir = os.path.join(base, *relative_dir.split("/"))
    need = []
    for index, pkg in enumerate(packages):
        path = os.path.join(model_dir, *pkg["id"].split("/"))
        if dir_signature(path) != (pkg["files"], pkg["size"]):
            need.append(index)
    for index, cert in enumerate(certs):
        path = os.path.join(model_dir, "CERTS", cert["thumbprint"] + ".cer")
        present = False
        if os.path.isfile(path) and not os.path.islink(path):
            present = (os.path.getsize(path) == cert["size"]
                       and sha256_file(path) == cert["sha256"])
        if not present:
            need.append(-(index + 1))
    return need


def on_inventory(xmppobject, action, sessionid, data, msg):
    state = get_state(xmppobject)
    metadata, relative_dir, packages, certs = parse_inventory(data)
    base = depot_base()

    with state["lock"]:
        now = time.time()
        for sid in [s for s, v in state["sessions"].items()
                    if now - v["touched"] > SESSION_TTL]:
            state["sessions"].pop(sid, None)
        cleanup_stale(base, set(state["active"]))

    need = compute_need(base, relative_dir, packages, certs)
    if not need:
        logger.info("[extract_drivers] %s : rien a recevoir (%d packages, %d certs deja presents)",
                    relative_dir, len(packages), len(certs))
        reply(xmppobject, msg, action, sessionid, "done", {
            "status": "ok", "nothing_to_send": True,
            "relative_dir": relative_dir,
            "depot_path": os.path.join(base, *relative_dir.split("/")),
            "packages_skipped": len(packages), "certs_skipped": len(certs)})
        return

    with state["lock"]:
        state["sessions"][sessionid] = {
            "sessionid": sessionid, "from": bare(msg["from"]),
            "created": now, "touched": now, "metadata": metadata,
            "relative_dir": relative_dir, "packages": packages, "certs": certs,
            "need": set(need), "meta": None, "received": None,
            "contiguous": 0, "resends": {}, "finalized": False,
            "lock": threading.RLock()}

    chunks = [need[i:i + PLAN_CHUNK] for i in range(0, len(need), PLAN_CHUNK)]
    for number, chunk in enumerate(chunks, start=1):
        reply(xmppobject, msg, action, sessionid, "plan", {
            "status": "plan", "part": number, "parts": len(chunks), "need": chunk,
            "need_total": len(need),
            "packages_skipped": len(packages) - sum(1 for n in need if n >= 0),
            "certs_skipped": len(certs) - sum(1 for n in need if n < 0)})


# ---------------------------------------------------------------------------
# Phase 2 : meta (negociation de reprise) et blocs
# ---------------------------------------------------------------------------

def get_session(state, sessionid, msg):
    with state["lock"]:
        sess = state["sessions"].get(sessionid)
    if sess is None:
        raise PluginError("session inconnue (serveur redemarre ou session expiree) : "
                          "relancer le transfert", retryable=True)
    if sess["from"] != bare(msg["from"]):
        raise PluginError("emetteur different de celui de la session")
    sess["touched"] = time.time()
    return sess


def part_paths(base, sha):
    incoming = os.path.join(base, INCOMING)
    return os.path.join(incoming, sha + ".part"), os.path.join(incoming, sha + ".json")


def write_json_atomic(path, payload):
    # pid + thread : le substitut traite plusieurs trames en parallele.
    tmp = "%s.tmp%d.%d" % (path, os.getpid(), threading.get_ident())
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
    os.replace(tmp, path)


def flush_state(base, sess):
    meta = sess["meta"]
    _part, state_path = part_paths(base, meta["sha256"])
    write_json_atomic(state_path, {
        "version": 1, "size": meta["size"], "segment_bytes": meta["segment_bytes"],
        "segment_total": meta["segment_total"], "contiguous": sess["contiguous"],
        "updated": time.time()})


def load_resume_point(base, meta):
    """Nombre de blocs deja recus et verifies de facon contigue (0 si rien d'exploitable)."""
    part, state_path = part_paths(base, meta["sha256"])
    contiguous = 0
    try:
        with open(state_path, "r", encoding="utf-8") as handle:
            saved = json.load(handle)
        if (saved.get("size") == meta["size"]
                and saved.get("segment_bytes") == meta["segment_bytes"]
                and saved.get("segment_total") == meta["segment_total"]
                and os.path.isfile(part)):
            contiguous = int(saved.get("contiguous", 0))
            on_disk = os.path.getsize(part)
            contiguous = max(0, min(contiguous, meta["segment_total"],
                                    on_disk // meta["segment_bytes"]
                                    if on_disk < meta["size"] else meta["segment_total"]))
    except (OSError, ValueError, TypeError):
        contiguous = 0
    if contiguous == 0:
        for path in (part, state_path):
            try:
                os.remove(path)
            except OSError:
                pass
    return contiguous


def on_meta(xmppobject, action, sessionid, data, msg):
    state = get_state(xmppobject)
    sess = get_session(state, sessionid, msg)
    base = depot_base()

    size, seg, total = data.get("size"), data.get("segment_bytes"), data.get("segment_total")
    sha, md5 = data.get("sha256"), data.get("md5")
    unpacked = data.get("unpacked_size")
    if not (isinstance(size, int) and isinstance(seg, int) and isinstance(total, int)
            and isinstance(unpacked, int)):
        raise PluginError("meta : champs numeriques invalides")
    if not (isinstance(sha, str) and _SHA256_RE.match(sha)
            and isinstance(md5, str) and _MD5_RE.match(md5)):
        raise PluginError("meta : empreintes invalides")
    if not (MIN_SEGMENT_BYTES <= seg <= MAX_SEGMENT_BYTES):
        raise PluginError("meta : segment_bytes hors bornes")
    if size < 1 or size > MAX_ARCHIVE_BYTES or unpacked < 0 or unpacked > MAX_UNPACKED_BYTES:
        raise PluginError("meta : taille d'archive refusee (%d o, max %d)"
                          % (size, MAX_ARCHIVE_BYTES))
    if total != max(1, (size + seg - 1) // seg):
        raise PluginError("meta : segment_total incoherent")

    now = time.time()
    with state["lock"]:
        holder = state["active"].get(sha)
        if (holder and holder["sessionid"] != sessionid and holder["from"] != sess["from"]
                and now - holder["touched"] < ACTIVE_TTL):
            raise PluginError("un transfert identique est deja en cours depuis un autre "
                              "poste", retryable=True)
        state["active"][sha] = {"sessionid": sessionid, "from": sess["from"],
                                "touched": now}

    meta = {"size": size, "segment_bytes": seg, "segment_total": total,
            "sha256": sha, "md5": md5, "unpacked_size": unpacked}
    contiguous = load_resume_point(base, meta)
    part, _state = part_paths(base, sha)
    already = min(size, contiguous * seg)
    free = shutil.disk_usage(base).free
    if free < (size - already) + unpacked + MIN_FREE_MARGIN:
        release_active(state, sha, sessionid)
        raise PluginError("espace disque insuffisant sur le depot (%d Mo libres)"
                          % (free // (1024 * 1024)))
    if not os.path.isfile(part):
        open(part, "wb").close()

    received = bytearray(total)
    for index in range(contiguous):
        received[index] = 1
    sess.update({"meta": meta, "received": received, "contiguous": contiguous,
                 "resends": {}, "finalized": False})
    if contiguous:
        logger.info("[extract_drivers] reprise de %s a partir du bloc %d/%d",
                    sessionid, contiguous, total)

    if contiguous >= total:
        finalize(xmppobject, action, sessionid, sess, msg)
        return
    reply(xmppobject, msg, action, sessionid, "resume", {
        "status": "resume", "next_segment": contiguous, "segment_total": total})


def release_active(state, sha, sessionid):
    with state["lock"]:
        holder = state["active"].get(sha)
        if holder and holder["sessionid"] == sessionid:
            state["active"].pop(sha, None)


def expected_block_size(meta, index):
    if index < meta["segment_total"] - 1:
        return meta["segment_bytes"]
    return meta["size"] - index * meta["segment_bytes"]


def on_data(xmppobject, action, sessionid, data, msg):
    state = get_state(xmppobject)
    sess = get_session(state, sessionid, msg)
    # Les blocs d'une meme session arrivent dans des threads concurrents :
    # on serialise (contiguite, etat disque, finalisation unique).
    with sess["lock"]:
        _on_data_locked(xmppobject, action, sessionid, data, msg, state, sess)


def _on_data_locked(xmppobject, action, sessionid, data, msg, state, sess):
    meta = sess["meta"]
    if meta is None or sess["finalized"]:
        raise PluginError("bloc recu hors negociation (meta absente ou transfert termine)")
    base = depot_base()

    index = data.get("segment_idx")
    if not isinstance(index, int) or not 0 <= index < meta["segment_total"]:
        raise PluginError("segment_idx invalide : %r" % (index,))
    if data.get("segment_total") != meta["segment_total"]:
        raise PluginError("segment_total incoherent")

    expected = expected_block_size(meta, index)
    try:
        packed = base64.b64decode(data.get("data_b64") or "", validate=True)
        decompressor = zlib.decompressobj()
        block = decompressor.decompress(packed, expected + 1)
        bad = bool(decompressor.unconsumed_tail) or not decompressor.eof
    except (ValueError, zlib.error, TypeError):
        block, bad = b"", True
    if (bad or len(block) != expected or data.get("raw_size") != expected
            or hashlib.md5(block).hexdigest() != data.get("md5_segment")):
        count = sess["resends"].get(index, 0) + 1
        sess["resends"][index] = count
        if count > MAX_RESEND_PER_BLOCK:
            raise PluginError("bloc %d corrompu a %d reprises" % (index, count - 1))
        logger.warning("[extract_drivers] bloc %d invalide (session %s) : renvoi demande",
                       index, sessionid)
        reply(xmppobject, msg, action, sessionid, "resend", {"segment_idx": index})
        return

    part, _state = part_paths(base, meta["sha256"])
    with open(part, "r+b") as handle:
        handle.seek(index * meta["segment_bytes"])
        handle.write(block)
    sess["received"][index] = 1
    while sess["contiguous"] < meta["segment_total"] and sess["received"][sess["contiguous"]]:
        sess["contiguous"] += 1

    with state["lock"]:
        holder = state["active"].get(meta["sha256"])
        if holder and holder["sessionid"] == sessionid:
            holder["touched"] = time.time()

    if (sess["contiguous"] % STATE_FLUSH_EVERY == 0
            or sess["contiguous"] >= meta["segment_total"]):
        flush_state(base, sess)

    if sess["contiguous"] >= meta["segment_total"]:
        finalize(xmppobject, action, sessionid, sess, msg)
    elif data.get("last"):
        missing = sess["received"].find(0)
        logger.warning("[extract_drivers] dernier bloc recu mais le bloc %d manque", missing)
        reply(xmppobject, msg, action, sessionid, "resend", {"segment_idx": missing})


# ---------------------------------------------------------------------------
# Phase 3 : verification, extraction sure, installation package par package
# ---------------------------------------------------------------------------

def plan_zip_entries(zf, sess):
    """
    Controle TOUTES les entrees avant la moindre ecriture. Retourne
    ({id package: [(info, parties relatives au package)]}, {thumbprint: info}).
    """
    rel_parts = sess["relative_dir"].split("/")
    allowed_packages = {sess["packages"][i]["id"] for i in sess["need"] if i >= 0}
    allowed_certs = {sess["certs"][-i - 1]["thumbprint"] for i in sess["need"] if i < 0}
    infos = zf.infolist()
    if len(infos) > MAX_ENTRIES:
        raise PluginError("archive : trop d'entrees (%d)" % len(infos))

    packages, certs, seen, unpacked = {}, {}, set(), 0
    for info in infos:
        name = info.filename
        parts = name.rstrip("/").split("/")
        if not all(valid_component(p) for p in parts):
            raise PluginError("archive : chemin dangereux ou invalide : %r" % name)
        if info.flag_bits & 0x1:
            raise PluginError("archive : entree chiffree : %r" % name)
        mode = info.external_attr >> 16
        if mode and (stat.S_ISLNK(mode) or stat.S_ISBLK(mode) or stat.S_ISCHR(mode)):
            raise PluginError("archive : entree speciale refusee : %r" % name)
        if name.endswith("/"):
            continue
        key = name.lower()
        if key in seen:
            raise PluginError("archive : entree en double : %r" % name)
        seen.add(key)
        if parts[:3] != rel_parts or len(parts) < 5:
            raise PluginError("archive : entree hors de %s : %r" % (sess["relative_dir"], name))
        unpacked += info.file_size
        if unpacked > MAX_UNPACKED_BYTES:
            raise PluginError("archive : taille decompressee excessive")
        if parts[3] == "CERTS":
            thumb = parts[4][:-4] if parts[4].lower().endswith(".cer") else None
            if len(parts) != 5 or thumb is None or thumb not in allowed_certs:
                raise PluginError("archive : certificat non demande : %r" % name)
            certs[thumb] = info
        elif parts[3] == "DRIVERS" and len(parts) >= 7:
            pid = "/".join(parts[3:6])
            if pid not in allowed_packages:
                raise PluginError("archive : package non demande : %r" % pid)
            packages.setdefault(pid, []).append((info, parts[6:]))
        else:
            raise PluginError("archive : entree inattendue : %r" % name)
    return packages, certs, unpacked


def extract_member(zf, info, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    remaining = info.file_size
    with zf.open(info) as source, open(dest, "wb") as out:
        while True:
            chunk = source.read(min(1 << 20, remaining + 1))
            if not chunk:
                break
            remaining -= len(chunk)
            if remaining < 0:
                raise PluginError("archive : %r depasse la taille declaree" % info.filename)
            out.write(chunk)
    if remaining:
        raise PluginError("archive : %r plus petit que declare" % info.filename)


def install_tree(src, dst):
    """Rename si la cible n'existe pas, sinon fusion fichier par fichier (rien n'est supprime)."""
    if not os.path.lexists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            os.rename(src, dst)
        except OSError:
            shutil.move(src, dst)
        return
    if os.path.isfile(src):
        pairs = [(dst, src)]
    else:
        pairs = [(os.path.join(dst, *rel.split("/")), full) for rel, full in walk_files(src)]
    for target, full in pairs:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        tmp = "%s.tmp%d" % (target, os.getpid())
        shutil.copyfile(full, tmp)
        os.replace(tmp, target)


def discard_partial(base, sha):
    for path in part_paths(base, sha):
        try:
            os.remove(path)
        except OSError:
            pass


def finalize(xmppobject, action, sessionid, sess, msg):
    state = get_state(xmppobject)
    meta = sess["meta"]
    base = depot_base()
    part, _state = part_paths(base, meta["sha256"])
    tmp_root = os.path.join(base, INCOMING, sessionid.replace("/", "_") + ".x")
    sess["finalized"] = True
    try:
        if os.path.getsize(part) != meta["size"] or md5_file(part) != meta["md5"] \
                or sha256_file(part) != meta["sha256"]:
            discard_partial(base, meta["sha256"])
            raise PluginError("empreinte de l'archive invalide : le transfert repart de "
                              "zero a la prochaine tentative", retryable=True)

        try:
            zf = zipfile.ZipFile(part)
        except zipfile.BadZipFile:
            discard_partial(base, meta["sha256"])
            raise PluginError("archive ZIP illisible")
        with zf:
            packages, certs, unpacked = plan_zip_entries(zf, sess)
            if unpacked != meta["unpacked_size"]:
                raise PluginError("taille decompressee (%d) differente de celle declaree (%d)"
                                  % (unpacked, meta["unpacked_size"]))
            wanted_pk = {sess["packages"][i]["id"]: sess["packages"][i]
                         for i in sess["need"] if i >= 0}
            wanted_ce = {sess["certs"][-i - 1]["thumbprint"]: sess["certs"][-i - 1]
                         for i in sess["need"] if i < 0}
            if set(packages) != set(wanted_pk) or set(certs) != set(wanted_ce):
                raise PluginError("archive incomplete par rapport au plan")

            rel = sess["relative_dir"].split("/")
            shutil.rmtree(tmp_root, ignore_errors=True)
            for pid, entries in packages.items():
                for info, sub in entries:
                    extract_member(zf, info, os.path.join(tmp_root, *rel, *pid.split("/"), *sub))
            for thumb, info in certs.items():
                extract_member(zf, info, os.path.join(tmp_root, *rel, "CERTS", thumb + ".cer"))

        for pid, want in wanted_pk.items():
            digest, files, size = package_digest(os.path.join(tmp_root, *rel, *pid.split("/")))
            if (digest, files, size) != (want["digest"], want["files"], want["size"]):
                raise PluginError("package %s : empreinte differente de l'inventaire" % pid)
        for thumb, want in wanted_ce.items():
            if sha256_file(os.path.join(tmp_root, *rel, "CERTS", thumb + ".cer")) != want["sha256"]:
                raise PluginError("certificat %s : empreinte differente de l'inventaire" % thumb)

        model_dir = os.path.join(base, *rel)
        with state["lock"]:
            for pid in wanted_pk:
                install_tree(os.path.join(tmp_root, *rel, *pid.split("/")),
                             os.path.join(model_dir, *pid.split("/")))
            for thumb in wanted_ce:
                install_tree(os.path.join(tmp_root, *rel, "CERTS", thumb + ".cer"),
                             os.path.join(model_dir, "CERTS", thumb + ".cer"))
            write_json_atomic(os.path.join(model_dir, ".extract-metadata.json"), {
                "received_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "sessionid": sessionid, "metadata": sess["metadata"],
                "archive_sha256": meta["sha256"]})
        discard_partial(base, meta["sha256"])
        logger.info("[extract_drivers] %s : %d package(s), %d certificat(s) deposes",
                    sess["relative_dir"], len(wanted_pk), len(wanted_ce))
        reply(xmppobject, msg, action, sessionid, "done", {
            "status": "ok", "relative_dir": sess["relative_dir"], "depot_path": model_dir,
            "sha256": meta["sha256"], "bytes": meta["size"],
            "packages_received": len(wanted_pk), "certs_received": len(wanted_ce),
            "packages_skipped": len(sess["packages"]) - len(wanted_pk),
            "certs_skipped": len(sess["certs"]) - len(wanted_ce)})
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
        release_active(state, meta["sha256"], sessionid)
        with state["lock"]:
            state["sessions"].pop(sessionid, None)


# ---------------------------------------------------------------------------
# Point d'entree du substitut maitre
# ---------------------------------------------------------------------------

HANDLERS = {"inventory": on_inventory, "meta": on_meta, "data": on_data}


def action(xmppobject, action, sessionid, data, msg, ret, dataerreur):
    try:
        kind = data.get("type") if isinstance(data, dict) else None
        handler = HANDLERS.get(kind)
        if handler is None:
            raise PluginError("type de trame inconnu : %r (protocole %s)" % (kind, SCHEMA))
        handler(xmppobject, action, sessionid, data, msg)
    except PluginError as exc:
        logger.error("[extract_drivers] session %s : %s", sessionid, exc)
        reply(xmppobject, msg, action, sessionid, "error",
              {"status": "error", "message": str(exc), "retryable": exc.retryable}, ret=1)
    except Exception:
        logger.exception("[extract_drivers] erreur interne (session %s)", sessionid)
        reply(xmppobject, msg, action, sessionid, "error",
              {"status": "error", "message": "erreur interne du recepteur (voir le "
               "journal du substitut maitre)", "retryable": False}, ret=1)
