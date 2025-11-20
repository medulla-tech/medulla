#!/usr/bin/env python3
"""
Script to clean .pot file headers by removing placeholder values
and setting consistent metadata.

Usage:
    python clean_pot_headers.py [--module MODULE_NAME]

Examples:
    # Clean all .pot files
    python clean_pot_headers.py

    # Clean specific module
    python clean_pot_headers.py --module admin
"""

import os
import re
import sys
import argparse
from pathlib import Path


def clean_pot_header(pot_file, module_name):
    """
    Clean the header of a .pot file by removing placeholders
    and setting consistent values.

    Args:
        pot_file: Path to the .pot file
        module_name: Name of the module

    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(pot_file):
        print(f"  ⚠️  POT file not found: {pot_file}")
        return False

    print(f"  📖 Reading {module_name}.pot...")

    with open(pot_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the header block (from start to first real msgid)
    # The header is: msgid "" \n msgstr "" followed by header lines
    header_pattern = r'^(msgid ""\nmsgstr "")\n((?:"[^"]*"\n)+)'
    match = re.search(header_pattern, content, re.MULTILINE)

    if not match:
        print(f"  ⚠️  Could not find header in POT file")
        return False

    # Extract the header lines
    header_start = match.group(1)
    header_lines = match.group(2)

    # Parse header into dict
    header_dict = {}
    for line in header_lines.strip().split('\n'):
        line = line.strip('"')
        if ':' in line:
            key, value = line.split(':', 1)
            header_dict[key.strip()] = value.strip()

    # Get POT-Creation-Date from original if exists
    pot_creation_date = header_dict.get('POT-Creation-Date', '2025-01-01 00:00+0000')

    # Create clean header
    clean_header = f'''msgid ""
msgstr ""
"Project-Id-Version: medulla\\n"
"POT-Creation-Date: {pot_creation_date}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
'''

    # Replace old header with clean one
    new_content = re.sub(
        header_pattern,
        clean_header,
        content,
        count=1,
        flags=re.MULTILINE
    )

    print(f"  💾 Writing cleaned header...")
    with open(pot_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  ✅ Successfully cleaned {module_name}.pot")
    return True


def get_all_modules(base_path):
    """Get list of all modules with .pot files."""
    modules_dir = os.path.join(base_path, "web/modules")
    modules = []

    if not os.path.exists(modules_dir):
        return modules

    for item in os.listdir(modules_dir):
        module_dir = os.path.join(modules_dir, item)
        if os.path.isdir(module_dir):
            pot_file = os.path.join(module_dir, f"locale/{item}.pot")
            if os.path.exists(pot_file):
                modules.append(item)

    return sorted(modules)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Clean .pot file headers by removing placeholders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s
  %(prog)s --module admin
        '''
    )

    parser.add_argument('--module', help='Clean only this module (default: all modules)')
    parser.add_argument('--base-path', default='../..',
                        help='Base path to medulla directory (default: ../.. from tools/i18n/)')

    args = parser.parse_args()

    # Get base path (from tools/i18n/ we go up two levels)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.base_path))

    if not os.path.exists(os.path.join(base_path, "web/modules")):
        print(f"❌ Invalid base path: {base_path}")
        print(f"   web/modules directory not found")
        sys.exit(1)

    # Get modules to process
    if args.module:
        modules = [args.module]
    else:
        modules = get_all_modules(base_path)

    if not modules:
        print("❌ No modules found to clean")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"📦 Modules to clean: {', '.join(modules)}")
    print(f"{'='*60}\n")

    # Clean each module
    success_count = 0
    total_count = len(modules)

    for module in modules:
        print(f"🔄 Processing: {module}")
        pot_file = os.path.join(base_path, f"web/modules/{module}/locale/{module}.pot")
        if clean_pot_header(pot_file, module):
            success_count += 1
        print()

    # Final summary
    print(f"{'='*60}")
    print(f"✨ Cleaning complete!")
    print(f"📊 Successfully cleaned: {success_count}/{total_count}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
