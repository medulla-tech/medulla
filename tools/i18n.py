#!/usr/bin/env python3
"""
Medulla i18n Tool - Unified translation management

Commands:
    extract [module]     Extract translatable strings from PHP → .pot
    init [module]        Initialize .po files from .pot template
    translate [module]   Translate empty strings via DeepL API
    compile [module]     Compile .po → .mo (for local testing only)
    all [module]         Full workflow: extract → init → translate

Usage:
    python3 tools/i18n.py extract                    # All modules
    python3 tools/i18n.py extract store              # Single module
    python3 tools/i18n.py translate --key=DEEPL_KEY  # Translate all
    python3 tools/i18n.py translate store --key=KEY  # Translate one module
    python3 tools/i18n.py all store --key=DEEPL_KEY  # Full workflow

Note: .mo files are compiled at installation time by autotools.
      The compile command is only for local testing.
"""

import os
import re
import sys
import argparse
import subprocess
import time
from pathlib import Path

# Base path (script should be run from repo root)
BASE_PATH = Path(__file__).parent.parent

# All known modules
ALL_MODULES = [
    'admin', 'backuppc', 'base', 'dashboard', 'dyngroup', 'glpi',
    'guacamole', 'imaging', 'inventory', 'kiosk', 'mastering',
    'medulla_server', 'mobile', 'msc', 'pkgs', 'ppolicy', 'report',
    'services', 'store', 'support', 'updates', 'urbackup', 'xmppmaster'
]

# Supported languages
LANGUAGES = ['fr_FR', 'es_ES']

# DeepL language mapping
DEEPL_LANG_MAP = {
    'fr_FR': 'FR',
    'es_ES': 'ES',
    'en_US': 'EN-US',
    'de_DE': 'DE',
    'it_IT': 'IT',
    'pt_PT': 'PT-PT',
    'pt_BR': 'PT-BR',
}


def get_module_path(module):
    """Get the path to a module directory."""
    return BASE_PATH / 'web' / 'modules' / module


def get_locale_path(module):
    """Get the path to a module's locale directory."""
    return get_module_path(module) / 'locale'


def get_pot_path(module):
    """Get the path to a module's .pot file."""
    return get_locale_path(module) / f'{module}.pot'


def get_po_path(module, lang):
    """Get the path to a module's .po file for a language."""
    return get_locale_path(module) / lang / 'LC_MESSAGES' / f'{module}.po'


def get_mo_path(module, lang):
    """Get the path to a module's .mo file for a language."""
    return get_locale_path(module) / lang / 'LC_MESSAGES' / f'{module}.mo'


def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)


# =============================================================================
# EXTRACT COMMAND
# =============================================================================

def cmd_extract(modules):
    """Extract translatable strings from PHP code → .pot files."""
    print("🔍 Extracting translatable strings...\n")

    for module in modules:
        module_path = get_module_path(module)
        pot_path = get_pot_path(module)

        if not module_path.exists():
            print(f"  ⚠️  Module '{module}' not found, skipping")
            continue

        # Create locale directory if needed
        pot_path.parent.mkdir(parents=True, exist_ok=True)

        # Special case: 'base' module uses _ instead of _T and scans root
        if module == 'base':
            search_path = BASE_PATH / 'web'
            keyword = '_'
        else:
            search_path = module_path
            keyword = '_T'

        # Remove old .pot file
        if pot_path.exists():
            pot_path.unlink()

        # Create empty .pot file
        pot_path.touch()

        # Run xgettext
        cmd = (
            f'find "{search_path}" -iname "*.php" -exec xgettext '
            f'--from-code=UTF-8 --language=PHP --keyword="{keyword}" '
            f'--output="{pot_path}" --join-existing {{}} +'
        )

        success, stdout, stderr = run_command(cmd)

        if success:
            # Count extracted strings
            try:
                with open(pot_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                count = content.count('\nmsgid "')
                print(f"  ✅ {module}: {count} strings")
            except:
                print(f"  ✅ {module}: extracted")
        else:
            print(f"  ❌ {module}: extraction failed")
            if stderr:
                print(f"      {stderr[:100]}")

    print("\n✅ Extraction complete")


# =============================================================================
# INIT COMMAND
# =============================================================================

def cmd_init(modules):
    """Initialize .po files from .pot templates."""
    print("📝 Initializing .po files...\n")

    for module in modules:
        pot_path = get_pot_path(module)

        if not pot_path.exists():
            print(f"  ⚠️  No .pot file for '{module}', run extract first")
            continue

        for lang in LANGUAGES:
            po_path = get_po_path(module, lang)

            # Create directory if needed
            po_path.parent.mkdir(parents=True, exist_ok=True)

            if po_path.exists():
                # Update existing .po with new strings from .pot
                cmd = f'msgmerge --update --no-fuzzy-matching "{po_path}" "{pot_path}"'
                success, _, _ = run_command(cmd)
                if success:
                    print(f"  ✅ {module}/{lang}: updated")
                else:
                    print(f"  ⚠️  {module}/{lang}: update failed")
            else:
                # Create new .po from .pot
                cmd = f'msginit --no-translator --locale={lang} --input="{pot_path}" --output="{po_path}"'
                success, _, stderr = run_command(cmd)
                if success:
                    print(f"  ✅ {module}/{lang}: created")
                else:
                    print(f"  ❌ {module}/{lang}: creation failed")

    print("\n✅ Initialization complete")


# =============================================================================
# TRANSLATE COMMAND
# =============================================================================

def parse_po_entries(po_path):
    """Parse PO file and return entries with their positions."""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    entries = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for start of entry (reference comment)
        if not line.startswith('#:'):
            i += 1
            continue

        entry_start = i

        # Skip all comments
        while i < len(lines) and lines[i].startswith('#'):
            i += 1

        # Parse msgid
        if i >= len(lines) or not lines[i].startswith('msgid '):
            i += 1
            continue

        msgid_parts = []
        match = re.match(r'msgid\s+"(.*)"', lines[i])
        if match:
            msgid_parts.append(match.group(1))
        i += 1

        # Continuation lines for msgid
        while i < len(lines) and lines[i].startswith('"'):
            match = re.match(r'"(.*)"', lines[i])
            if match:
                msgid_parts.append(match.group(1))
            i += 1

        # Parse msgstr
        if i >= len(lines) or not lines[i].startswith('msgstr '):
            continue

        msgstr_start = i
        msgstr_parts = []

        match = re.match(r'msgstr\s+"(.*)"', lines[i])
        if match:
            msgstr_parts.append(match.group(1))
        i += 1

        # Continuation lines for msgstr
        while i < len(lines) and lines[i].startswith('"'):
            match = re.match(r'"(.*)"', lines[i])
            if match:
                msgstr_parts.append(match.group(1))
            i += 1

        # Unescape strings
        msgid = ''.join(msgid_parts)
        msgid = msgid.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        msgstr = ''.join(msgstr_parts)
        msgstr = msgstr.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        if msgid:
            entries.append({
                'msgid': msgid,
                'msgstr': msgstr,
                'msgstr_empty': msgstr.strip() == '',
                'msgstr_start': msgstr_start,
                'msgstr_end': i,
            })

    return entries, lines


def escape_po_string(text):
    """Escape a string for PO format."""
    if not text:
        return ''
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '\\n')
    return text


def translate_with_deepl(translator, text, target_lang):
    """Translate text using DeepL API."""
    if not text or text.strip() == "":
        return text

    try:
        result = translator.translate_text(
            text,
            target_lang=target_lang,
            tag_handling='html',
            preserve_formatting=True
        )
        return result.text
    except Exception as e:
        print(f"      Translation error: {e}")
        return text


def cmd_translate(modules, api_key, force=False):
    """Translate empty msgstr in .po files using DeepL."""
    print("🌍 Translating strings with DeepL...\n")

    try:
        import deepl
    except ImportError:
        print("❌ DeepL library not installed. Run:")
        print("   pip install deepl")
        sys.exit(1)

    # Initialize DeepL
    try:
        translator = deepl.Translator(api_key)
        usage = translator.get_usage()
        print(f"DeepL API connected")
        print(f"Usage: {usage.character.count:,}/{usage.character.limit:,} chars")
        remaining = usage.character.limit - usage.character.count
        print(f"Remaining: {remaining:,} chars\n")
    except Exception as e:
        print(f"❌ Failed to connect to DeepL: {e}")
        sys.exit(1)

    total_translated = 0

    for module in modules:
        for lang in LANGUAGES:
            po_path = get_po_path(module, lang)

            if not po_path.exists():
                continue

            deepl_lang = DEEPL_LANG_MAP.get(lang)
            if not deepl_lang:
                continue

            print(f"  {module}/{lang}:")

            entries, lines = parse_po_entries(str(po_path))

            if force:
                to_translate = [e for e in entries if e['msgid']]
            else:
                to_translate = [e for e in entries if e['msgstr_empty']]

            if not to_translate:
                print(f"    All strings already translated")
                continue

            print(f"    Translating {len(to_translate)} strings...")

            translations = {}
            for i, entry in enumerate(to_translate):
                translated = translate_with_deepl(translator, entry['msgid'], deepl_lang)
                translations[entry['msgid']] = translated
                time.sleep(0.3)  # Rate limiting

            # Update lines in reverse order
            for entry in reversed(to_translate):
                if entry['msgid'] in translations:
                    translated = translations[entry['msgid']]
                    escaped = escape_po_string(translated)
                    del lines[entry['msgstr_start']:entry['msgstr_end']]
                    lines.insert(entry['msgstr_start'], f'msgstr "{escaped}"\n')

            # Write back
            with open(po_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"    ✅ {len(to_translate)} strings translated")
            total_translated += len(to_translate)

    print(f"\n✅ Translation complete ({total_translated} strings)")


# =============================================================================
# COMPILE COMMAND
# =============================================================================

def cmd_compile(modules):
    """Compile .po files to .mo (for local testing only)."""
    print("🔨 Compiling .po → .mo...\n")
    print("Note: .mo files are normally compiled at installation time.\n")

    for module in modules:
        for lang in LANGUAGES:
            po_path = get_po_path(module, lang)
            mo_path = get_mo_path(module, lang)

            if not po_path.exists():
                continue

            cmd = f'msgfmt "{po_path}" -o "{mo_path}"'
            success, _, stderr = run_command(cmd)

            if success:
                print(f"  ✅ {module}/{lang}")
            else:
                print(f"  ❌ {module}/{lang}: {stderr[:50] if stderr else 'failed'}")

    print("\n✅ Compilation complete")


# =============================================================================
# ALL COMMAND
# =============================================================================

def cmd_all(modules, api_key):
    """Run full workflow: extract → init → translate."""
    print("🚀 Running full i18n workflow...\n")
    print("=" * 60)

    cmd_extract(modules)
    print("\n" + "=" * 60 + "\n")

    cmd_init(modules)
    print("\n" + "=" * 60 + "\n")

    cmd_translate(modules, api_key)
    print("\n" + "=" * 60)

    print("\n✨ Full workflow complete!")
    print("\nNote: .mo files are NOT compiled (they're generated at installation)")


# =============================================================================
# MAIN
# =============================================================================

def get_modules(module_arg):
    """Get list of modules to process."""
    if module_arg:
        if module_arg not in ALL_MODULES:
            print(f"⚠️  Module '{module_arg}' not in known list, but will try anyway")
        return [module_arg]
    return ALL_MODULES


def main():
    parser = argparse.ArgumentParser(
        description='Medulla i18n Tool - Unified translation management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Commands:
  extract [module]     Extract _T() strings from PHP → .pot
  init [module]        Create/update .po files from .pot
  translate [module]   Translate empty strings via DeepL
  compile [module]     Compile .po → .mo (local testing only)
  all [module]         Full workflow: extract → init → translate

Examples:
  python3 tools/i18n.py extract store
  python3 tools/i18n.py translate store --key=YOUR_DEEPL_KEY
  python3 tools/i18n.py all store --key=YOUR_DEEPL_KEY
'''
    )

    parser.add_argument('command', choices=['extract', 'init', 'translate', 'compile', 'all'],
                        help='Command to run')
    parser.add_argument('module', nargs='?', default=None,
                        help='Module name (default: all modules)')
    parser.add_argument('--key', dest='api_key',
                        help='DeepL API key (required for translate/all)')
    parser.add_argument('--force', action='store_true',
                        help='Force re-translate all strings (translate command)')

    args = parser.parse_args()

    # Change to repo root
    os.chdir(BASE_PATH)

    modules = get_modules(args.module)

    if args.command == 'extract':
        cmd_extract(modules)

    elif args.command == 'init':
        cmd_init(modules)

    elif args.command == 'translate':
        if not args.api_key:
            print("❌ DeepL API key required. Use --key=YOUR_KEY")
            sys.exit(1)
        cmd_translate(modules, args.api_key, args.force)

    elif args.command == 'compile':
        cmd_compile(modules)

    elif args.command == 'all':
        if not args.api_key:
            print("❌ DeepL API key required. Use --key=YOUR_KEY")
            sys.exit(1)
        cmd_all(modules, args.api_key)


if __name__ == '__main__':
    main()
