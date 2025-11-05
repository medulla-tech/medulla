#!/usr/bin/env python3
"""
Script to synchronize translations from .pot to .po files using DeepL API.
Only translates missing/untranslated strings to optimize API usage.

Usage:
    python sync_translations.py <DEEPL_API_KEY> [--module MODULE_NAME] [--lang fr_FR,es_ES] [--force] [--compile]

Examples:
    # Sync all modules for fr_FR and es_ES (only new strings)
    python sync_translations.py YOUR_API_KEY

    # Force re-translate all strings in admin module
    python sync_translations.py YOUR_API_KEY --module admin --force

    # Sync only to French
    python sync_translations.py YOUR_API_KEY --lang fr_FR

    # Sync and compile to .mo files (for local testing only)
    python sync_translations.py YOUR_API_KEY --compile

Note: .mo files are NOT needed in git. They're compiled during server installation.
"""

import os
import re
import sys
import argparse
import time
import subprocess
from pathlib import Path

try:
    import deepl
except ImportError:
    print("❌ DeepL library not installed. Install it with:")
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

# Plural forms for each language
PLURAL_FORMS = {
    'fr_FR': 'nplurals=3; plural=(n == 0 || n == 1) ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2;',
    'es_ES': 'nplurals=2; plural=(n != 1);',
    'en_US': 'nplurals=2; plural=(n != 1);',
    'de_DE': 'nplurals=2; plural=(n != 1);',
    'it_IT': 'nplurals=2; plural=(n != 1);',
    'pt_PT': 'nplurals=2; plural=(n != 1);',
    'pt_BR': 'nplurals=2; plural=(n != 1);',
}


class POEntry:
    """Represents a PO entry"""
    def __init__(self, references, flags, msgid, msgstr=""):
        self.references = references
        self.flags = flags
        self.msgid = msgid
        self.msgstr = msgstr

    def __str__(self):
        """Format as PO entry"""
        lines = []
        for ref in self.references:
            lines.append(f"#: {ref}")
        for flag in self.flags:
            lines.append(f"#, {flag}")
        lines.append(f'msgid "{self._escape(self.msgid)}"')
        lines.append(f'msgstr "{self._escape(self.msgstr)}"')
        return '\n'.join(lines) + '\n'

    @staticmethod
    def _escape(text):
        """Escape text for PO format"""
        if not text:
            return ""
        return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def parse_pot_file(pot_path):
    """Parse a .pot file and extract all msgid entries."""
    with open(pot_path, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line or not line.startswith('#:'):
            i += 1
            continue

        references = []
        flags = []

        # Collect references
        while i < len(lines) and lines[i].strip().startswith('#:'):
            references.append(lines[i].strip()[3:].strip())
            i += 1

        # Collect flags
        while i < len(lines) and lines[i].strip().startswith('#,'):
            flags.append(lines[i].strip()[3:].strip())
            i += 1

        # Read msgid
        if i >= len(lines) or not lines[i].strip().startswith('msgid'):
            i += 1
            continue

        msgid_lines = []
        msgid_match = re.match(r'msgid\s+"(.*)"', lines[i].strip())
        if msgid_match:
            msgid_lines.append(msgid_match.group(1))
            i += 1

        while i < len(lines) and lines[i].strip().startswith('"'):
            match = re.match(r'"(.*)"', lines[i].strip())
            if match:
                msgid_lines.append(match.group(1))
            i += 1

        # Skip msgstr
        if i < len(lines) and lines[i].strip().startswith('msgstr'):
            i += 1
            while i < len(lines) and lines[i].strip().startswith('"'):
                i += 1

        msgid = ''.join(msgid_lines).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        if msgid:
            entries.append(POEntry(references, flags, msgid))

    return entries


def parse_po_file(po_path):
    """Parse existing .po file and return dict of msgid -> msgstr."""
    if not os.path.exists(po_path):
        return {}

    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations = {}
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line or not line.startswith('#:'):
            i += 1
            continue

        # Skip references and flags
        while i < len(lines) and (lines[i].strip().startswith('#:') or lines[i].strip().startswith('#,')):
            i += 1

        # Read msgid
        if i >= len(lines) or not lines[i].strip().startswith('msgid'):
            i += 1
            continue

        msgid_lines = []
        msgid_match = re.match(r'msgid\s+"(.*)"', lines[i].strip())
        if msgid_match:
            msgid_lines.append(msgid_match.group(1))
            i += 1

        while i < len(lines) and lines[i].strip().startswith('"') and not lines[i].strip().startswith('msgstr'):
            match = re.match(r'"(.*)"', lines[i].strip())
            if match:
                msgid_lines.append(match.group(1))
            i += 1

        # Read msgstr
        msgstr_lines = []
        if i < len(lines) and lines[i].strip().startswith('msgstr'):
            msgstr_match = re.match(r'msgstr\s+"(.*)"', lines[i].strip())
            if msgstr_match:
                msgstr_lines.append(msgstr_match.group(1))
                i += 1

            while i < len(lines) and lines[i].strip().startswith('"'):
                match = re.match(r'"(.*)"', lines[i].strip())
                if match:
                    msgstr_lines.append(match.group(1))
                i += 1

        msgid = ''.join(msgid_lines).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
        msgstr = ''.join(msgstr_lines).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        if msgid:
            translations[msgid] = msgstr

    return translations


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
        print(f"    ⚠️  Translation error: {e}")
        return text


def create_po_header(language):
    """Create PO file header."""
    plural_form = PLURAL_FORMS.get(language, PLURAL_FORMS['en_US'])

    return f'''msgid ""
msgstr ""
"Project-Id-Version: medulla\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Language: {language}\\n"
"Plural-Forms: {plural_form}\\n"

'''


def compile_po_to_mo(po_file):
    """
    Compile a .po file to .mo using msgfmt.

    Args:
        po_file: Path to the .po file

    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(po_file):
        print(f"    ⚠️  PO file not found: {po_file}")
        return False

    mo_file = po_file.replace('.po', '.mo')

    try:
        result = subprocess.run(
            ['msgfmt', po_file, '-o', mo_file],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"    ✅ Compiled {os.path.basename(mo_file)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Compilation failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"    ⚠️  msgfmt not found. Install gettext tools: brew install gettext (macOS) or apt-get install gettext (Linux)")
        return False


def sync_translations(translator, module_name, target_lang, base_path, force=False, compile_mo=False):
    """
    Synchronize translations from .pot to .po file.
    Only translates missing strings unless force=True.

    Args:
        translator: DeepL Translator instance
        module_name: Name of the module
        target_lang: Target language code (e.g., 'fr_FR')
        base_path: Base path to medulla directory
        force: If True, re-translate all strings
        compile_mo: If True, compile .po to .mo after translation

    Returns:
        True if successful, False otherwise
    """
    pot_file = os.path.join(base_path, f"web/modules/{module_name}/locale/{module_name}.pot")
    po_file = os.path.join(base_path, f"web/modules/{module_name}/locale/{target_lang}/LC_MESSAGES/{module_name}.po")

    if not os.path.exists(pot_file):
        print(f"  ⚠️  POT file not found: {pot_file}")
        return False

    print(f"  📖 Reading {module_name}.pot...")
    pot_entries = parse_pot_file(pot_file)
    print(f"  🔤 Found {len(pot_entries)} strings in source")

    # Parse existing .po file to get already translated strings
    existing_translations = parse_po_file(po_file)
    print(f"  📝 Found {len(existing_translations)} existing translations")

    # Get DeepL language code
    deepl_lang = DEEPL_LANG_MAP.get(target_lang)
    if not deepl_lang:
        print(f"  ❌ Unsupported language: {target_lang}")
        return False

    # Determine which strings need translation
    to_translate = []
    for entry in pot_entries:
        if force or entry.msgid not in existing_translations or not existing_translations[entry.msgid]:
            to_translate.append(entry)
        else:
            # Keep existing translation
            entry.msgstr = existing_translations[entry.msgid]

    if not to_translate:
        print(f"  ✅ All strings already translated! Nothing to do.")
        # Even if nothing to translate, still compile if requested
        if compile_mo and os.path.exists(po_file):
            compile_po_to_mo(po_file)
        return True

    print(f"  🌍 Need to translate {len(to_translate)} strings to {target_lang} ({deepl_lang})")

    # Calculate estimated characters
    total_chars = sum(len(entry.msgid) for entry in to_translate)
    print(f"  📊 Estimated characters to translate: {total_chars:,}")

    # Translate missing strings
    translated_count = 0
    for i, entry in enumerate(to_translate):
        if (i + 1) % 10 == 0:
            print(f"    Progress: {i + 1}/{len(to_translate)} strings translated...")

        entry.msgstr = translate_text_deepl(translator, entry.msgid, deepl_lang)
        translated_count += 1

        # Small delay to avoid rate limiting (0.5s = max 2 requests/sec)
        time.sleep(0.5)

    print(f"  ✅ Translated {translated_count} new strings")

    # Create output directory if needed
    os.makedirs(os.path.dirname(po_file), exist_ok=True)

    # Write PO file
    print(f"  💾 Writing to {module_name}.po...")
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(create_po_header(target_lang))
        for entry in pot_entries:
            f.write(str(entry) + '\n')

    print(f"  ✅ Successfully updated {po_file}")

    # Compile to .mo if requested
    if compile_mo:
        compile_po_to_mo(po_file)

    return True


def get_all_modules(base_path):
    """Get list of all modules with .pot files."""
    modules_dir = os.path.join(base_path, "web/modules")
    modules = []

    if not os.path.exists(modules_dir):
        return modules

    for module_name in os.listdir(modules_dir):
        module_path = os.path.join(modules_dir, module_name)
        pot_file = os.path.join(module_path, f"locale/{module_name}.pot")

        if os.path.isdir(module_path) and os.path.exists(pot_file):
            modules.append(module_name)

    return sorted(modules)


def detect_target_languages(base_path, module_name):
    """Detect existing language directories for a module."""
    locale_dir = os.path.join(base_path, f"web/modules/{module_name}/locale")
    languages = []

    if not os.path.exists(locale_dir):
        return languages

    for item in os.listdir(locale_dir):
        item_path = os.path.join(locale_dir, item)
        if os.path.isdir(item_path) and item in DEEPL_LANG_MAP:
            languages.append(item)

    return sorted(languages)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Sync translations from .pot to .po using DeepL API (only translates new strings)',
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
    parser.add_argument('--lang', help='Target languages (comma-separated). If not specified, auto-detect from existing locale directories.')
    parser.add_argument('--force', action='store_true', help='Force re-translate all strings (default: only translate missing)')
    parser.add_argument('--compile', action='store_true', help='Compile .po files to .mo after translation (requires msgfmt)')
    parser.add_argument('--base-path', default='.',
                        help='Base path to medulla directory (default: current directory)')

    args = parser.parse_args()

    # Initialize DeepL translator
    print("🔑 Initializing DeepL translator...")
    try:
        translator = deepl.Translator(args.api_key)
        usage = translator.get_usage()
        print(f"✅ DeepL API connected")
        print(f"📊 Usage: {usage.character.count:,}/{usage.character.limit:,} characters")
        remaining = usage.character.limit - usage.character.count
        print(f"💡 Remaining: {remaining:,} characters")
    except Exception as e:
        print(f"❌ Failed to initialize DeepL: {e}")
        sys.exit(1)

    # Get base path
    base_path = os.path.abspath(args.base_path)
    if not os.path.exists(os.path.join(base_path, "web/modules")):
        print(f"❌ Invalid base path: {base_path}")
        print(f"   web/modules directory not found")
        sys.exit(1)

    # Get modules to sync
    if args.module:
        modules = [args.module]
    else:
        modules = get_all_modules(base_path)

    if not modules:
        print("❌ No modules found to sync")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"📦 Modules to sync: {', '.join(modules)}")
    print(f"🔄 Mode: {'FORCE (re-translate all)' if args.force else 'SMART (only new strings)'}")
    if args.compile:
        print(f"🔨 Compile: Will generate .mo files after translation")
    print(f"{'='*60}\n")

    # Sync each module
    success_count = 0
    total_count = 0

    for module in modules:
        # Determine target languages
        if args.lang:
            target_langs = [lang.strip() for lang in args.lang.split(',')]
        else:
            # Auto-detect from existing locale directories
            target_langs = detect_target_languages(base_path, module)
            if not target_langs:
                # Default to fr_FR and es_ES if no directories exist
                target_langs = ['fr_FR', 'es_ES']
                print(f"  💡 No locale directories found, using default: {', '.join(target_langs)}")

        for target_lang in target_langs:
            total_count += 1
            print(f"🔄 Syncing: {module} → {target_lang}")
            if sync_translations(translator, module, target_lang, base_path, args.force, args.compile):
                success_count += 1
            print()

    # Final summary
    print(f"{'='*60}")
    print(f"✨ Sync complete!")
    print(f"📊 Successfully synced: {success_count}/{total_count}")

    # Show final usage
    try:
        usage = translator.get_usage()
        print(f"📊 DeepL usage: {usage.character.count:,}/{usage.character.limit:,} characters")
        remaining = usage.character.limit - usage.character.count
        print(f"💡 Remaining: {remaining:,} characters")
    except:
        pass

    print(f"{'='*60}")


if __name__ == '__main__':
    main()
