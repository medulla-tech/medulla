#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file: services/bin/medulla-acl-manager.py
#
# CLI tool for managing ACL profiles and features.
#
# Usage:
#   medulla-acl-manager profiles list                     List all profiles
#   medulla-acl-manager profiles add <name>               Add a new profile
#   medulla-acl-manager profiles delete <name>            Delete a profile
#
#   medulla-acl-manager features list                     List all features
#   medulla-acl-manager features show <feature_key>       Show ACL entries for a feature
#   medulla-acl-manager features add <key> <label> <desc> <category> <access_type> <acl1,acl2,...>
#                                                         Add a new feature
#   medulla-acl-manager features add-acl <key> <acl_entry> <access_type>
#                                                         Add an ACL entry to an existing feature
#   medulla-acl-manager features remove-acl <key> <acl_entry>
#                                                         Remove an ACL entry from a feature
#
#   medulla-acl-manager scan                              Scan codebase for pages not in any feature
#   medulla-acl-manager build <profile>                   Show generated ACL string for a profile
#
# Deployed to: /usr/sbin/medulla-acl-manager

import sys
import os
import subprocess
import json
import re
import glob

# ============================================================================
# Database connection
# ============================================================================

def get_db_config():
    """Read DB credentials from xmppmaster.ini.local (same pattern as other scripts)."""
    def crudini_get(section, key, default=None):
        try:
            result = subprocess.check_output(
                ["crudini", "--get", "/etc/mmc/plugins/xmppmaster.ini.local", section, key],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            return result if result else default
        except:
            return default

    return {
        "host": crudini_get("database", "dbhost", "localhost"),
        "port": int(crudini_get("database", "dbport", "3306")),
        "user": crudini_get("database", "dbuser", "mmc"),
        "passwd": crudini_get("database", "dbpasswd", ""),
        "db": "admin",
        "charset": "utf8mb4",
    }


def get_db():
    import MySQLdb
    config = get_db_config()
    return MySQLdb.connect(**config)


def query(sql, params=None):
    """Execute a SELECT and return list of dicts."""
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params or ())
    columns = [desc[0] for desc in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    db.close()
    return rows


def execute(sql, params=None):
    """Execute an INSERT/UPDATE/DELETE."""
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params or ())
    db.commit()
    affected = cur.rowcount
    cur.close()
    db.close()
    return affected


# ============================================================================
# Colors
# ============================================================================

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
NC = "\033[0m"


# ============================================================================
# Profiles commands
# ============================================================================

def cmd_profiles_list():
    rows = query("SELECT profile_name, display_order FROM acl_profiles ORDER BY display_order")
    if not rows:
        print(f"{DIM}No profiles found.{NC}")
        return
    print(f"\n{BOLD}Profiles:{NC}")
    for r in rows:
        count = query(
            "SELECT COUNT(*) as c FROM acl_profile_features WHERE profile_name = %s",
            (r["profile_name"],)
        )[0]["c"]
        print(f"  {CYAN}{r['profile_name']}{NC} (order: {r['display_order']}, {count} features)")
    print()


def cmd_profiles_add(name):
    max_order = query("SELECT COALESCE(MAX(display_order), 0) as m FROM acl_profiles")[0]["m"]
    affected = execute(
        "INSERT IGNORE INTO acl_profiles (profile_name, display_order) VALUES (%s, %s)",
        (name, max_order + 1)
    )
    if affected:
        print(f"{GREEN}Profile '{name}' added.{NC}")
    else:
        print(f"{YELLOW}Profile '{name}' already exists.{NC}")


def cmd_profiles_delete(name):
    if name == "Super-Admin":
        print(f"{RED}Cannot delete Super-Admin profile.{NC}")
        return
    count = query(
        "SELECT COUNT(*) as c FROM acl_profile_features WHERE profile_name = %s", (name,)
    )[0]["c"]
    if count > 0:
        confirm = input(f"{YELLOW}Profile '{name}' has {count} feature(s). Delete anyway? (y/N) {NC}")
        if confirm.lower() != "y":
            print("Cancelled.")
            return
    execute("DELETE FROM acl_profile_features WHERE profile_name = %s", (name,))
    affected = execute("DELETE FROM acl_profiles WHERE profile_name = %s", (name,))
    if affected:
        print(f"{GREEN}Profile '{name}' deleted.{NC}")
    else:
        print(f"{RED}Profile '{name}' not found.{NC}")


# ============================================================================
# Features commands
# ============================================================================

def cmd_features_list():
    # Get category order from DB
    cat_rows = query("SELECT category_key, label FROM acl_categories ORDER BY display_order")
    cat_order = [(r["category_key"], r["label"]) for r in cat_rows]

    rows = query("""
        SELECT feature_key, label, description, category, superadmin_only, access_type,
               COUNT(*) as acl_count, MIN(id) as first_id
        FROM acl_feature_definitions
        GROUP BY feature_key, label, description, category, superadmin_only, access_type
        ORDER BY first_id
    """)
    if not rows:
        print(f"{DIM}No features found.{NC}")
        return

    # Group by category
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)

    print(f"\n{BOLD}Features:{NC}")
    seen = set()
    for cat_key, cat_label in cat_order:
        if cat_key not in by_cat:
            continue
        seen.add(cat_key)
        print(f"\n  {BOLD}{cat_label}{NC}")
        for r in by_cat[cat_key]:
            sa = f" {YELLOW}[superadmin]{NC}" if r["superadmin_only"] else ""
            print(f"    {CYAN}{r['feature_key']}{NC} ({r['access_type']}, {r['acl_count']} ACLs){sa}")
            print(f"      {DIM}{r['label']}{NC}")
    # Categories not in DB
    for cat_key in by_cat:
        if cat_key not in seen:
            print(f"\n  {BOLD}{cat_key.upper()}{NC}")
            for r in by_cat[cat_key]:
                sa = f" {YELLOW}[superadmin]{NC}" if r["superadmin_only"] else ""
                print(f"    {CYAN}{r['feature_key']}{NC} ({r['access_type']}, {r['acl_count']} ACLs){sa}")
                print(f"      {DIM}{r['label']}{NC}")
    print()


def cmd_features_show(feature_key):
    rows = query(
        "SELECT acl_entry, access_type FROM acl_feature_definitions WHERE feature_key = %s ORDER BY id",
        (feature_key,)
    )
    if not rows:
        print(f"{RED}Feature '{feature_key}' not found.{NC}")
        return
    # Get metadata from first row
    meta = query(
        "SELECT label, description, category, superadmin_only FROM acl_feature_definitions WHERE feature_key = %s LIMIT 1",
        (feature_key,)
    )[0]
    print(f"\n{BOLD}{feature_key}{NC}")
    print(f"  Label:       {meta['label']}")
    print(f"  Description: {meta['description'] or '-'}")
    print(f"  Category:    {meta['category']}")
    print(f"  Super-Admin: {'yes' if meta['superadmin_only'] else 'no'}")
    print(f"\n  {BOLD}ACL entries ({len(rows)}):{NC}")
    for r in rows:
        print(f"    [{r['access_type']}] {r['acl_entry']}")
    print()


def _insert_feature(key, label, description, category, access_type, acl_entries, superadmin=False):
    """Insert a feature with its ACL entries into the database."""
    count = 0
    for acl in acl_entries:
        execute(
            "INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (key, label, description, category, 1 if superadmin else 0, acl, access_type)
        )
        count += 1
    return count


def cmd_features_add(key, label, description, category, access_type, acl_entries_str, superadmin=False):
    """Add a new feature with its ACL entries (CLI args mode)."""
    acl_entries = [a.strip() for a in acl_entries_str.split(",") if a.strip()]
    if not acl_entries:
        print(f"{RED}No ACL entries provided.{NC}")
        return
    count = _insert_feature(key, label, description, category, access_type, acl_entries, superadmin)
    print(f"{GREEN}Feature '{key}' added with {count} ACL entries.{NC}")


def cmd_features_add_interactive():
    """Add a new feature interactively."""
    print(f"\n{BOLD}Add a new feature{NC}\n")

    # Key
    key = input(f"  {BOLD}Clé unique{NC} (ex: store_rw): ").strip()
    if not key:
        print(f"{RED}Clé requise.{NC}")
        return

    # Check if exists
    existing = query("SELECT COUNT(*) as c FROM acl_feature_definitions WHERE feature_key = %s", (key,))
    if existing and existing[0]["c"] > 0:
        print(f"{RED}La feature '{key}' existe déjà. Utilisez 'features add-acl' pour ajouter des ACLs.{NC}")
        return

    # Label
    label = input(f"  {BOLD}Label{NC} (ex: Store (catalogue, déploiement...)): ").strip()
    if not label:
        print(f"{RED}Label requis.{NC}")
        return

    # Description
    print(f"  {BOLD}Description{NC} (items séparés par |, ex: Catalogue|Abonnements|Déploiement)")
    description = input(f"  > ").strip()

    # Category
    cats = query("SELECT category_key, label FROM acl_categories ORDER BY display_order")
    cat_list = ", ".join([f"{c['category_key']}" for c in cats])
    print(f"  {BOLD}Catégorie{NC} [{cat_list}]")
    category = input(f"  > ").strip()
    if not category:
        print(f"{RED}Catégorie requise.{NC}")
        return
    known_cats = [c["category_key"] for c in cats]
    if category not in known_cats:
        confirm = input(f"  {YELLOW}Catégorie '{category}' n'existe pas. Créer ? (o/N){NC} ").strip()
        if confirm.lower() != "o":
            return
        cat_label = input(f"  Label de la catégorie: ").strip() or category.capitalize()
        max_order = query("SELECT COALESCE(MAX(display_order), 0) as m FROM acl_categories")[0]["m"]
        execute("INSERT INTO acl_categories (category_key, label, display_order) VALUES (%s, %s, %s)",
                (category, cat_label, max_order + 1))
        print(f"  {GREEN}Catégorie '{category}' créée.{NC}")

    # Access type
    access_type = input(f"  {BOLD}Type d'accès{NC} (ro/rw): ").strip().lower()
    if access_type not in ("ro", "rw"):
        print(f"{RED}Type d'accès invalide (ro ou rw).{NC}")
        return

    # Superadmin only
    sa_input = input(f"  {BOLD}Super-Admin uniquement{NC} (o/N): ").strip().lower()
    superadmin = sa_input == "o"

    # ACL entries
    print(f"  {BOLD}ACL entries{NC} (une par ligne ou séparées par des virgules, vide pour terminer):")
    acl_entries = []
    while True:
        entry = input(f"    > ").strip()
        if not entry:
            break
        # Accept comma-separated on a single line
        for acl in entry.split(","):
            acl = acl.strip()
            if acl:
                acl_entries.append(acl)

    if not acl_entries:
        print(f"{RED}Aucune ACL entry. Abandon.{NC}")
        return

    # Summary
    print(f"\n  {BOLD}Résumé :{NC}")
    print(f"    Clé:          {CYAN}{key}{NC}")
    print(f"    Label:        {label}")
    print(f"    Description:  {description}")
    print(f"    Catégorie:    {category}")
    print(f"    Type:         {access_type}")
    print(f"    Super-Admin:  {'oui' if superadmin else 'non'}")
    print(f"    ACL entries:  {len(acl_entries)}")
    for acl in acl_entries:
        print(f"      {DIM}{acl}{NC}")

    confirm = input(f"\n  {BOLD}Confirmer ? (o/N){NC} ").strip()
    if confirm.lower() != "o":
        print("Abandon.")
        return

    count = _insert_feature(key, label, description, category, access_type, acl_entries, superadmin)
    print(f"\n{GREEN}Feature '{key}' créée avec {count} ACL entries.{NC}\n")


def cmd_features_add_acl(feature_key, acl_entry, access_type):
    """Add an ACL entry to an existing feature."""
    meta = query(
        "SELECT label, description, category, superadmin_only FROM acl_feature_definitions WHERE feature_key = %s LIMIT 1",
        (feature_key,)
    )
    if not meta:
        print(f"{RED}Feature '{feature_key}' not found.{NC}")
        return
    m = meta[0]
    execute(
        "INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (feature_key, m["label"], m["description"], m["category"], m["superadmin_only"], acl_entry, access_type)
    )
    print(f"{GREEN}Added '{acl_entry}' ({access_type}) to feature '{feature_key}'.{NC}")


def cmd_features_remove_acl(feature_key, acl_entry):
    """Remove an ACL entry from a feature."""
    affected = execute(
        "DELETE FROM acl_feature_definitions WHERE feature_key = %s AND acl_entry = %s",
        (feature_key, acl_entry)
    )
    if affected:
        print(f"{GREEN}Removed '{acl_entry}' from feature '{feature_key}'.{NC}")
    else:
        print(f"{RED}ACL entry '{acl_entry}' not found in feature '{feature_key}'.{NC}")


# ============================================================================
# Scan command - find pages not covered by any feature
# ============================================================================

def cmd_scan():
    """Scan infoPackage.inc.php files to find pages not in any feature definition."""
    # Collect all ACL entries from DB
    db_acls = set()
    rows = query("SELECT DISTINCT acl_entry FROM acl_feature_definitions")
    for r in rows:
        db_acls.add(r["acl_entry"])

    # Modules disabled in config
    disabled_modules = set()
    conf_dir = "/etc/mmc/plugins"
    if os.path.isdir(conf_dir):
        import configparser
        for ini_file in glob.glob(os.path.join(conf_dir, "*.ini")):
            try:
                cp = configparser.ConfigParser()
                cp.read([ini_file, ini_file + ".local"])
                if cp.has_option("main", "disable") and cp.getboolean("main", "disable"):
                    mod_name = os.path.basename(ini_file).replace(".ini", "")
                    disabled_modules.add(mod_name)
            except:
                pass

    # Modules not relevant for ACL (framework/legacy/deprecated)
    ignored_modules = {'ppolicy', 'report', 'services', 'mobile', 'inventory',
                       'dyngroup', 'msc', 'backuppc', 'urbackup', 'guacamole'}

    # Scan infoPackage files
    web_root = "/usr/share/mmc/modules"
    if not os.path.isdir(web_root):
        web_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "modules")

    visible_pages = set()
    ajax_pages = set()
    scanned_modules = set()

    for info_file in sorted(glob.glob(os.path.join(web_root, "*/infoPackage.inc.php"))):
        module = os.path.basename(os.path.dirname(info_file))

        if module in disabled_modules or module in ignored_modules:
            continue

        scanned_modules.add(module)

        with open(info_file, "r") as f:
            content = f.read()

        # Find SubModule names
        submods = re.findall(r'new\s+SubModule\s*\(\s*["\'](\w+)["\']', content)
        submod = submods[0] if submods else module

        # Split by "new Page(" to get one chunk per page
        chunks = re.split(r'(?=new\s+Page\s*\()', content)

        for chunk in chunks:
            m = re.match(r'new\s+Page\s*\(\s*["\'](\w+)["\']', chunk)
            if not m:
                continue
            page_name = m.group(1)
            acl = f"{module}#{submod}#{page_name}"

            # Detect AJAX/hidden pages:
            # 1. Explicit setOptions with AJAX/visible/noHeader
            options = chunk[:600]
            is_ajax = bool(re.search(r'["\']AJAX["\']\s*=>\s*true', options))
            is_hidden = bool(re.search(r'["\']visible["\']\s*=>\s*false', options))
            is_noheader = bool(re.search(r'["\']noHeader["\']\s*=>\s*true', options))
            # 2. Name starts with "ajax" (convention)
            is_ajax_name = page_name.lower().startswith('ajax')

            if is_ajax or is_hidden or is_noheader or is_ajax_name:
                ajax_pages.add(acl)
            else:
                visible_pages.add(acl)

    # Find missing
    missing_visible = sorted(visible_pages - db_acls)
    covered = sorted((visible_pages | ajax_pages) & db_acls)

    print(f"\n{BOLD}Scan Results:{NC}")
    print(f"  Modules scanned:     {len(scanned_modules)} ({', '.join(sorted(scanned_modules))})")
    if disabled_modules:
        print(f"  Disabled:            {', '.join(sorted(disabled_modules))}")
    if ignored_modules:
        print(f"  Ignored:             {', '.join(sorted(ignored_modules))}")
    print(f"  Visible pages:       {len(visible_pages)}")
    print(f"  AJAX/hidden pages:   {len(ajax_pages)}")
    print(f"  Covered by features: {len(covered)}")

    if missing_visible:
        print(f"\n  {YELLOW}Visible pages NOT in any feature: {len(missing_visible)}{NC}")
        print(f"\n{BOLD}Missing pages:{NC}")
        current_module = None
        for acl in missing_visible:
            mod = acl.split("#")[0]
            if mod != current_module:
                current_module = mod
                print(f"\n  {BOLD}{mod}{NC}")
            print(f"    {YELLOW}{acl}{NC}")
    else:
        print(f"\n  {GREEN}All visible pages are covered!{NC}")

    print()


# ============================================================================
# Build command - show ACL string for a profile
# ============================================================================

def cmd_build(profile_name):
    """Build and display the ACL string for a profile."""
    # Get profile features
    features = query(
        "SELECT feature_key, access_level FROM acl_profile_features WHERE profile_name = %s",
        (profile_name,)
    )
    if not features:
        print(f"{RED}No features configured for profile '{profile_name}'.{NC}")
        return

    # Get all definitions
    defs = query("SELECT feature_key, acl_entry, access_type FROM acl_feature_definitions")
    # Group by feature_key
    feature_acls = {}
    for d in defs:
        feature_acls.setdefault(d["feature_key"], []).append(d)

    # Build ACL set
    acl_entries = set()
    for f in features:
        fkey = f["feature_key"]
        level = f["access_level"]
        for d in feature_acls.get(fkey, []):
            if d["access_type"] == "ro":
                acl_entries.add(d["acl_entry"])
            elif d["access_type"] == "rw" and level == "rw":
                acl_entries.add(d["acl_entry"])

    acl_string = ":" + ":".join(sorted(acl_entries)) + "/"

    print(f"\n{BOLD}ACL string for {CYAN}{profile_name}{NC}{BOLD}:{NC}")
    print(f"  {len(features)} features, {len(acl_entries)} ACL entries\n")
    print(acl_string)
    print()


# ============================================================================
# Usage
# ============================================================================

def usage():
    print(f"""
{BOLD}medulla-acl-manager{NC} - Manage ACL profiles and features

{BOLD}Usage:{NC}
  medulla-acl-manager profiles list                       List profiles
  medulla-acl-manager profiles add <name>                 Add a profile
  medulla-acl-manager profiles delete <name>              Delete a profile

  medulla-acl-manager features list                       List all features
  medulla-acl-manager features show <key>                 Show feature details
  medulla-acl-manager features add              Add a feature (interactive)
  medulla-acl-manager features add <key> <label> <desc> <category> <type> <acl1,acl2,...>
                                                          Add a feature (CLI args)
  medulla-acl-manager features add-acl <key> <acl> <type> Add ACL to feature
  medulla-acl-manager features remove-acl <key> <acl>     Remove ACL from feature

  medulla-acl-manager scan                                Find uncovered pages
  medulla-acl-manager build <profile>                     Show ACL string

{BOLD}Examples:{NC}
  medulla-acl-manager profiles add Hotliner
  medulla-acl-manager features show dashboard_user_widgets
  medulla-acl-manager features add-acl admin_superadmin admin#admin#aclFeatures rw
  medulla-acl-manager scan
  medulla-acl-manager build Super-Admin
""")


# ============================================================================
# Main
# ============================================================================

def main():
    args = sys.argv[1:]
    if len(args) < 1:
        usage()
        sys.exit(1)

    cmd = args[0]

    if cmd == "profiles":
        if len(args) < 2:
            usage()
            sys.exit(1)
        sub = args[1]
        if sub == "list":
            cmd_profiles_list()
        elif sub == "add" and len(args) >= 3:
            cmd_profiles_add(args[2])
        elif sub == "delete" and len(args) >= 3:
            cmd_profiles_delete(args[2])
        else:
            usage()
            sys.exit(1)

    elif cmd == "features":
        if len(args) < 2:
            usage()
            sys.exit(1)
        sub = args[1]
        if sub == "list":
            cmd_features_list()
        elif sub == "show" and len(args) >= 3:
            cmd_features_show(args[2])
        elif sub == "add" and len(args) >= 8:
            cmd_features_add(args[2], args[3], args[4], args[5], args[6], args[7],
                           "--superadmin" in args)
        elif sub == "add" and len(args) == 2:
            cmd_features_add_interactive()
        elif sub == "add-acl" and len(args) >= 5:
            cmd_features_add_acl(args[2], args[3], args[4])
        elif sub == "remove-acl" and len(args) >= 4:
            cmd_features_remove_acl(args[2], args[3])
        else:
            usage()
            sys.exit(1)

    elif cmd == "scan":
        cmd_scan()

    elif cmd == "build" and len(args) >= 2:
        cmd_build(args[1])

    else:
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
