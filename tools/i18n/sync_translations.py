#!/usr/bin/env python3
"""
Script to translate only empty msgstr in .po files using DeepL API.
Does NOT modify existing translations or file structure - only fills empty msgstr.

Usage:
    python sync_translations.py <DEEPL_API_KEY> [--module MODULE_NAME] [--lang fr_FR,es_ES] [--force] [--compile]

Examples:
    # Translate empty strings in all modules
    python sync_translations.py YOUR_API_KEY

    # Force re-translate all strings in admin module (OVERWRITES existing!)
    python sync_translations.py YOUR_API_KEY --module admin --force

    # Translate only French
    python sync_translations.py YOUR_API_KEY --lang fr_FR

Note: This script only modifies msgstr that are empty. It preserves all formatting,
comments, and existing translations.
"""

import os
import re
import sys
import argparse
import time

try:
    import deepl
except ImportError:
    print("DeepL library not installed. Install it with:")
    print("   pip install deepl")
    sys.exit(1)


# Language mapping: locale code -> DeepL language code
DEEPL_LANG_MAP = {
    'fr_FR': 'FR',
    'es_ES': 'ES',
    'en_US': 'EN-US',
    'de_DE': 'DE',
    'it_IT': 'IT',
    'pt_PT': 'PT-PT',
    'pt_BR': 'PT-BR',
}


def parse_po_entries(po_path):
    """
    Parse PO file and return list of entries with empty msgstr.
    Handles multi-line format where msgstr "" is followed by "actual translation".
    """
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

        msgid_start = i
        msgid_parts = []

        # First line of msgid
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

        # First line of msgstr
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

        entry_end = i

        # Unescape strings
        msgid = ''.join(msgid_parts)
        msgid = msgid.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        msgstr = ''.join(msgstr_parts)
        msgstr = msgstr.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        # Only add non-header entries
        if msgid:
            entries.append({
                'msgid': msgid,
                'msgstr': msgstr,
                'msgstr_empty': msgstr.strip() == '',
                'entry_start': entry_start,
                'entry_end': entry_end,
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


def translate_text_deepl(translator, text, target_lang):
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
        print(f"    Translation error: {e}")
        return text


def sync_translations(translator, module_name, target_lang, base_path, force=False):
    """
    Translate empty msgstr in .po file.

    - Does NOT use msgmerge
    - Does NOT modify file structure
    - Only replaces empty msgstr with translations
    """
    po_file = os.path.join(base_path, f"web/modules/{module_name}/locale/{target_lang}/LC_MESSAGES/{module_name}.po")

    if not os.path.exists(po_file):
        print(f"  PO file not found: {po_file}")
        return False

    # Get DeepL language code
    deepl_lang = DEEPL_LANG_MAP.get(target_lang)
    if not deepl_lang:
        print(f"  Unsupported language: {target_lang}")
        return False

    # Parse entries
    entries, lines = parse_po_entries(po_file)
    total_entries = len(entries)

    if force:
        to_translate = [e for e in entries if e['msgid']]
    else:
        to_translate = [e for e in entries if e['msgstr_empty']]

    print(f"  Found {total_entries} strings, {len(to_translate)} need translation")

    if not to_translate:
        print(f"  All strings already translated!")
        return True

    # Translate
    total_chars = sum(len(e['msgid']) for e in to_translate)
    print(f"  Translating {len(to_translate)} strings ({total_chars:,} chars)...")

    translations = {}
    for i, entry in enumerate(to_translate):
        if (i + 1) % 10 == 0:
            print(f"    Progress: {i + 1}/{len(to_translate)}...")

        translated = translate_text_deepl(translator, entry['msgid'], deepl_lang)
        translations[entry['msgid']] = translated

        # Rate limiting
        time.sleep(0.3)

    print(f"  Translated {len(translations)} strings")

    # Update lines - replace msgstr lines for translated entries
    # Process in reverse order to avoid index shifts
    for entry in reversed(to_translate):
        if entry['msgid'] in translations:
            translated = translations[entry['msgid']]
            escaped = escape_po_string(translated)

            # Remove old msgstr lines
            del lines[entry['msgstr_start']:entry['msgstr_end']]

            # Insert new msgstr line
            lines.insert(entry['msgstr_start'], f'msgstr "{escaped}"\n')

    # Write back
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"  Updated {po_file}")
    return True


def get_all_modules(base_path):
    """Get list of all modules with locale directories."""
    modules_dir = os.path.join(base_path, "web/modules")
    modules = []

    if not os.path.exists(modules_dir):
        return modules

    for module_name in os.listdir(modules_dir):
        module_path = os.path.join(modules_dir, module_name)
        locale_dir = os.path.join(module_path, "locale")

        if os.path.isdir(module_path) and os.path.exists(locale_dir):
            # Check if any .po files exist
            for lang_dir in os.listdir(locale_dir):
                po_path = os.path.join(locale_dir, lang_dir, "LC_MESSAGES", f"{module_name}.po")
                if os.path.exists(po_path):
                    modules.append(module_name)
                    break

    return sorted(modules)


def detect_target_languages(base_path, module_name):
    """Detect existing language directories for a module."""
    locale_dir = os.path.join(base_path, f"web/modules/{module_name}/locale")
    languages = []

    if not os.path.exists(locale_dir):
        return languages

    for item in os.listdir(locale_dir):
        item_path = os.path.join(locale_dir, item)
        po_file = os.path.join(item_path, "LC_MESSAGES", f"{module_name}.po")
        if os.path.isdir(item_path) and item in DEEPL_LANG_MAP and os.path.exists(po_file):
            languages.append(item)

    return sorted(languages)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Translate empty msgstr in .po files using DeepL API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s YOUR_API_KEY
  %(prog)s YOUR_API_KEY --module admin
  %(prog)s YOUR_API_KEY --lang fr_FR --force
        '''
    )

    parser.add_argument('api_key', help='DeepL API key')
    parser.add_argument('--module', help='Sync only this module (default: all modules)')
    parser.add_argument('--lang', help='Target languages (comma-separated). If not specified, auto-detect.')
    parser.add_argument('--force', action='store_true', help='Force re-translate ALL strings (OVERWRITES manual translations!)')
    parser.add_argument('--base-path', default='.', help='Base path to medulla directory')

    args = parser.parse_args()

    # Initialize DeepL translator
    print("Initializing DeepL translator...")
    try:
        translator = deepl.Translator(args.api_key)
        usage = translator.get_usage()
        print(f"DeepL API connected")
        print(f"Usage: {usage.character.count:,}/{usage.character.limit:,} characters")
        remaining = usage.character.limit - usage.character.count
        print(f"Remaining: {remaining:,} characters")
    except Exception as e:
        print(f"Failed to initialize DeepL: {e}")
        sys.exit(1)

    # Get base path
    base_path = os.path.abspath(args.base_path)
    if not os.path.exists(os.path.join(base_path, "web/modules")):
        print(f"Invalid base path: {base_path}")
        print(f"   web/modules directory not found")
        sys.exit(1)

    # Get modules to sync
    if args.module:
        modules = [args.module]
    else:
        modules = get_all_modules(base_path)

    if not modules:
        print("No modules found to sync")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Modules to sync: {', '.join(modules)}")
    print(f"Mode: {'FORCE (re-translate all)' if args.force else 'SMART (only empty msgstr)'}")
    print(f"{'='*60}\n")

    # Sync each module
    success_count = 0
    total_count = 0

    for module in modules:
        # Determine target languages
        if args.lang:
            target_langs = [lang.strip() for lang in args.lang.split(',')]
        else:
            target_langs = detect_target_languages(base_path, module)
            if not target_langs:
                print(f"  No .po files found for {module}, skipping")
                continue

        for target_lang in target_langs:
            total_count += 1
            print(f"Syncing: {module} -> {target_lang}")
            if sync_translations(translator, module, target_lang, base_path, args.force):
                success_count += 1
            print()

    # Final summary
    print(f"{'='*60}")
    print(f"Sync complete!")
    print(f"Successfully synced: {success_count}/{total_count}")

    try:
        usage = translator.get_usage()
        print(f"DeepL usage: {usage.character.count:,}/{usage.character.limit:,} characters")
        remaining = usage.character.limit - usage.character.count
        print(f"Remaining: {remaining:,} characters")
    except:
        pass

    print(f"{'='*60}")


if __name__ == '__main__':
    main()
