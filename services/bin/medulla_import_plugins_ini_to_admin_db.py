#!/usr/bin/env python3

# Script d'import des paramètres plugins INI vers la base MySQL admin.
#
# Principe général:
# - lire les fichiers plugin.ini et plugin.ini.local depuis un dossier donné,
# - appliquer la surcharge: *.ini.local > *.ini,
# - mapper chaque plugin vers sa table <plugin>_conf (ou variante *_master -> *_conf),
# - faire un UPSERT en base (INSERT si absent, UPDATE si présent),
# - afficher des stats (traitées / insérées / mises à jour / inchangées).

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def require_binary(binary: str) -> None:
    # Vérifie qu'une dépendance CLI est disponible dans le PATH.
    if shutil.which(binary) is None:
        raise RuntimeError(f"Binaire requis manquant: {binary}")


def sql_escape(value: str) -> str:
    # Échappement SQL minimal pour l'injection de chaînes dans les requêtes.
    # (anti quote/backslash, dans la logique actuelle basée sur mysql CLI)
    return value.replace("\\", "\\\\").replace("'", "''")


def infer_type(value: str) -> str:
    # Déduit le type attendu par le schéma (ENUM type):
    # booleen / entier / decimal / string.
    lowered = value.strip().lower()
    if lowered in {"true", "false", "yes", "no", "on", "off"}:
        return "booleen"
    if re.fullmatch(r"-?\d+", value):
        if value in {"0", "1"}:
            return "booleen"
        return "entier"
    if re.fullmatch(r"-?\d+\.\d+", value):
        return "decimal"
    return "string"


def parse_schema_tables(schema_file: Path) -> set[str]:
    # Extrait les noms de table depuis un fichier SQL (CREATE TABLE IF NOT EXISTS ...).
    # Utilisé uniquement si un schéma SQL est passé en argument.
    pattern = re.compile(
        r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+`?([a-zA-Z0-9_]+)`?",
        re.IGNORECASE,
    )
    tables: set[str] = set()
    content = schema_file.read_text(encoding="utf-8", errors="ignore")
    for match in pattern.finditer(content):
        tables.add(match.group(1))
    return tables


def run_crudini(args: list[str]) -> str:
    # Wrapper d'appel à crudini.
    # Retourne "" si la commande échoue (section/clé absente, fichier absent, etc.).
    proc = subprocess.run(
        ["crudini", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def get_ini_sections(ini_file: Path) -> list[str]:
    # Retourne la liste des sections d'un INI via crudini.
    sections = [line.strip() for line in run_crudini(["--get", str(ini_file)]).splitlines() if line.strip()]
    return sections


def parse_ini_section_lines(raw: str) -> dict[str, str]:
    # Parse le format "lines" de crudini pour une section, ex:
    #   [ main ] disable = 1
    # et renvoie {"disable": "1"}.
    # Les commentaires (#, ;) et lignes vides sont ignorés.
    data: dict[str, str] = {}
    section_prefix_pattern = re.compile(r"^\[\s*[^\]]+\s*\]\s*")
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        stripped = section_prefix_pattern.sub("", stripped)
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key:
            data[key] = value
    return data


def read_ini_section_with_local_override(ini_file: Path, section: str) -> dict[str, str]:
    # Lit la section depuis fichier.ini puis applique la surcharge éventuelle
    # depuis fichier.ini.local (les clés du .local remplacent celles du .ini).
    base_data = parse_ini_section_lines(run_crudini(["--get", "--format=lines", str(ini_file), section]))
    local_file = Path(f"{ini_file}.local")
    if local_file.exists():
        local_data = parse_ini_section_lines(run_crudini(["--get", "--format=lines", str(local_file), section]))
        base_data.update(local_data)
    return base_data


def get_db_from_admin_ini(admin_ini: Path) -> tuple[str, str, str, str]:
    # Lit les paramètres de connexion DB depuis admin.ini (+ admin.ini.local en surcharge)
    # avec possibilité de forcer via variables d'environnement.
    def get_value(key: str, default: str) -> str:
        local_file = Path(f"{admin_ini}.local")
        base = run_crudini(["--get", str(admin_ini), "database", key]).strip()
        if local_file.exists():
            local = run_crudini(["--get", str(local_file), "database", key]).strip()
            if local:
                return local
        return base or default

    db_host = os.environ.get("DB_HOST") or get_value("dbhost", "localhost")
    db_port = os.environ.get("DB_PORT") or get_value("dbport", "3306")
    db_user = os.environ.get("DB_USER") or get_value("dbuser", "mmc")
    db_password = os.environ.get("DB_PASSWORD") or get_value("dbpasswd", "mmc")
    return db_host, db_port, db_user, db_password


def mysql_exec(
    host: str,
    port: str,
    user: str,
    password: str,
    sql: str,
    db_name: str | None = None,
) -> tuple[int, str, str]:
    # Exécute une requête SQL via le client mysql.
    # Retour: (code_retour, stdout, stderr)
    cmd = ["mysql", "-h", host, "-P", str(port), "-u", user, f"-p{password}", "-Nse", sql]
    if db_name:
        cmd.extend(["-D", db_name])
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def table_exists(host: str, port: str, user: str, password: str, db_name: str, table: str) -> bool:
    # Vérifie l'existence d'une table dans information_schema.
    sql = (
        "SELECT COUNT(*) "
        "FROM information_schema.tables "
        f"WHERE table_schema='{sql_escape(db_name)}' AND table_name='{sql_escape(table)}';"
    )
    code, out, _ = mysql_exec(host, port, user, password, sql)
    return code == 0 and out.isdigit() and int(out) > 0


def get_conf_tables_from_db(host: str, port: str, user: str, password: str, db_name: str) -> set[str]:
    # Liste les tables *\_conf présentes en base (mode sans schéma SQL).
    sql = (
        "SELECT table_name "
        "FROM information_schema.tables "
        f"WHERE table_schema='{sql_escape(db_name)}' "
        "AND table_name LIKE '%\\_conf' ESCAPE '\\\\';"
    )
    code, out, err = mysql_exec(host, port, user, password, sql)
    if code != 0:
        raise RuntimeError(f"Impossible de lister les tables _conf depuis la base {db_name}: {err or 'echec mysql'}")
    tables = {line.strip() for line in out.splitlines() if line.strip()}
    return tables


def resolve_table_name(plugin: str, schema_tables: set[str]) -> str | None:
    # Résout la table cible d'un plugin:
    # - plugin -> plugin_conf
    # - fallback: *master -> *_conf (xmppmaster -> xmpp_conf)
    candidate = f"{plugin}_conf"
    if candidate in schema_tables:
        return candidate
    if plugin.endswith("master"):
        short_candidate = f"{plugin[:-6]}_conf"
        if short_candidate in schema_tables:
            return short_candidate
    return None


def get_plugin_stems(plugins_dir: Path) -> list[str]:
    # Construit la liste des plugins à partir des fichiers:
    # - *.ini
    # - *.ini.local
    # Le résultat est dédupliqué et trié.
    stems: set[str] = set()
    for ini_file in plugins_dir.glob("*.ini"):
        stems.add(ini_file.stem)
    for ini_local_file in plugins_dir.glob("*.ini.local"):
        name = ini_local_file.name
        if name.endswith(".ini.local"):
            stems.add(name[:-10])
    return sorted(stems)


def upsert_plugin_ini(
    ini_file: Path,
    ini_local_file: Path,
    plugin: str,
    table: str,
    host: str,
    port: str,
    user: str,
    password: str,
    db_name: str,
) -> tuple[int, int, int, int]:
    # Injecte un plugin dans sa table cible.
    # Retourne des compteurs:
    # (traitées, insérées, mises à jour, inchangées)
    #
    # Règle de fusion des sources:
    # - sections = union des sections de plugin.ini et plugin.ini.local
    # - pour chaque section: clés du .local surchargent celles du .ini
    treated = 0
    inserted = 0
    updated = 0
    unchanged = 0

    sections: set[str] = set()
    if ini_file.exists():
        sections.update(get_ini_sections(ini_file))
    if ini_local_file.exists():
        sections.update(get_ini_sections(ini_local_file))

    for section in sorted(s for s in sections if s):
        section_values = read_ini_section_with_local_override(ini_file, section)
        for key, value in section_values.items():
            sql_section = sql_escape(section)
            sql_key = sql_escape(key)
            sql_value = sql_escape(value)
            sql_type = infer_type(value)
            sql_description = sql_escape(f"Import automatique depuis {plugin}.ini")

            sql = f"""
INSERT INTO {table} (section, nom, activer, type, valeur, valeur_defaut, description)
VALUES ('{sql_section}', '{sql_key}', 1, '{sql_type}', '{sql_value}', '{sql_value}', '{sql_description}')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = COALESCE({table}.valeur_defaut, VALUES(valeur_defaut)),
    description = IF({table}.description IS NULL OR {table}.description = '', VALUES(description), {table}.description);
SELECT ROW_COUNT();
""".strip()

            # Interprétation ROW_COUNT() avec ON DUPLICATE KEY UPDATE:
            # 1 = insertion, 2 = mise à jour, 0 = aucune différence (inchangé)

            code, out, err = mysql_exec(host, port, user, password, sql, db_name=db_name)
            if code != 0:
                raise RuntimeError(
                    f"Erreur SQL pour {plugin}.ini [{section}.{key}] dans {table}: {err or 'echec mysql'}"
                )
            treated += 1

            lines = [line.strip() for line in out.splitlines() if line.strip()]
            row_count = None
            if lines and re.fullmatch(r"-?\d+", lines[-1]):
                row_count = int(lines[-1])

            if row_count == 1:
                inserted += 1
            elif row_count == 2:
                updated += 1
            elif row_count == 0:
                unchanged += 1
            else:
                raise RuntimeError(
                    f"ROW_COUNT() inattendu pour {plugin}.ini [{section}.{key}] dans {table}: {lines[-1] if lines else 'vide'}"
                )

    return treated, inserted, updated, unchanged


def main() -> int:
    # Point d'entrée CLI.
    # - schema_sql est optionnel:
    #   * fourni -> tables extraites du fichier SQL
    #   * absent  -> tables *_conf détectées directement en base
    # - plugins_ini_dir défaut: /etc/mmc/plugins
    parser = argparse.ArgumentParser(
        description="Importe les fichiers INI plugins vers la base admin en s'appuyant sur un schema SQL.")
    parser.add_argument(
        "schema_sql",
        nargs="?",
        default=None,
        help="Fichier schema SQL optionnel (ex: services/contrib/admin/sql/schema-007.sql)",
    )
    parser.add_argument(
        "plugins_ini_dir",
        nargs="?",
        default="/etc/mmc/plugins",
        help="Dossier des fichiers .ini (defaut: /etc/mmc/plugins)",
    )
    args = parser.parse_args()

    try:
        # Dépendances système requises.
        require_binary("crudini")
        require_binary("mysql")

        plugins_dir = Path(args.plugins_ini_dir)
        if not plugins_dir.is_dir():
            raise RuntimeError(f"Dossier INI introuvable: {plugins_dir}")

        admin_ini = plugins_dir / "admin.ini"
        if not admin_ini.is_file():
            raise RuntimeError(f"Fichier admin.ini introuvable: {admin_ini}")

        db_name = os.environ.get("DB_NAME", "admin")
        db_host, db_port, db_user, db_password = get_db_from_admin_ini(admin_ini)

        # Vérification de connectivité SQL en amont.
        check_code, _, check_err = mysql_exec(db_host, db_port, db_user, db_password, "SELECT 1;")
        if check_code != 0:
            raise RuntimeError(
                f"Connexion MySQL impossible ({db_user}@{db_host}:{db_port}): {check_err or 'erreur de connexion'}"
            )

        schema_tables: set[str]
        if args.schema_sql:
            schema_sql = Path(args.schema_sql)
            if not schema_sql.is_file():
                raise RuntimeError(f"Schema SQL introuvable: {schema_sql}")
            schema_tables = parse_schema_tables(schema_sql)
            if not schema_tables:
                raise RuntimeError(f"Aucune table detectee dans le schema: {schema_sql}")
        else:
            schema_tables = get_conf_tables_from_db(db_host, db_port, db_user, db_password, db_name)
            if not schema_tables:
                raise RuntimeError(f"Aucune table _conf detectee dans la base: {db_name}")

        print(f"Connexion DB OK ({db_user}@{db_host}:{db_port}, base={db_name})")

        processed = 0
        skipped_no_schema = 0
        skipped_no_db_table = 0
        total_treated = 0
        total_inserted = 0
        total_updated = 0
        total_unchanged = 0

        # Boucle principale: un plugin -> une table _conf cible.
        for plugin in get_plugin_stems(plugins_dir):
            ini_file = plugins_dir / f"{plugin}.ini"
            ini_local_file = plugins_dir / f"{plugin}.ini.local"
            table = resolve_table_name(plugin, schema_tables)

            if table is None:
                print(f"[SKIP] {plugin}.ini -> aucune table correspondante dans le schema")
                skipped_no_schema += 1
                continue

            if not table_exists(db_host, db_port, db_user, db_password, db_name, table):
                print(f"[SKIP] {plugin}.ini -> table absente en base: {table}")
                skipped_no_db_table += 1
                continue

            treated, inserted, updated, unchanged = upsert_plugin_ini(
                ini_file=ini_file,
                ini_local_file=ini_local_file,
                plugin=plugin,
                table=table,
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                db_name=db_name,
            )
            print(
                f"[OK] {plugin}.ini -> {table} "
                f"(traitees={treated}, inserees={inserted}, maj={updated}, inchangees={unchanged})"
            )
            processed += 1
            total_treated += treated
            total_inserted += inserted
            total_updated += updated
            total_unchanged += unchanged

        # Résumé global de traitement.
        print()
        print(
            f"Termine: {processed} plugin(s) importe(s), "
            f"{skipped_no_schema} ignore(s) (pas dans schema), "
            f"{skipped_no_db_table} ignore(s) (table absente en DB), "
            f"traitees={total_treated}, inserees={total_inserted}, maj={total_updated}, inchangees={total_unchanged}."
        )
        return 0
    except RuntimeError as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())