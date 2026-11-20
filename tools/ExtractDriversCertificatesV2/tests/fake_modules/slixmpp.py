# -*- coding: utf-8 -*-
"""
Shim de test : fait resoudre `import slixmpp` vers le faux client XMPP.

Ce dossier (`tests/fake_modules/`) doit etre place EN TETE de PYTHONPATH par
le banc de test, et uniquement par lui. Il n'est jamais deploye sur un poste :
le vrai slixmpp de l'agent (>= 1.8.5 sous Windows) reste celui utilise en
production.
"""

import os
import sys

_TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from fake_slixmpp import ClientXMPP, __version__  # noqa: E402,F401
