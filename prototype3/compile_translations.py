#!/usr/bin/env python
"""Compile translation files"""

import os
import sys
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

def compile_translations(translations_dir):
    """Compile all .po files to .mo files"""
    for lang_dir in os.listdir(translations_dir):
        lang_path = os.path.join(translations_dir, lang_dir)
        if not os.path.isdir(lang_path):
            continue
            
        lc_messages = os.path.join(lang_path, 'LC_MESSAGES')
        if not os.path.exists(lc_messages):
            continue
            
        po_file = os.path.join(lc_messages, 'messages.po')
        mo_file = os.path.join(lc_messages, 'messages.mo')
        
        if os.path.exists(po_file):
            print(f'Compiling {lang_dir}...')
            with open(po_file, 'rb') as f:
                catalog = read_po(f)
            with open(mo_file, 'wb') as f:
                write_mo(f, catalog)
            print(f'  ✓ {lang_dir} compiled')

if __name__ == '__main__':
    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
    compile_translations(translations_dir)
    print('All translations compiled successfully!')
