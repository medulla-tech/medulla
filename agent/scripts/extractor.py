# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Babel PO extractor for report template XML files
"""
from xml.sax import ContentHandler, make_parser


# A decorator function that takes care of starting a coroutine
# automatically on call.
def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


class StringExtractor(ContentHandler):
    _current_ch_line = None
    _current_ch = False

    def __init__(self, target, attrs, elems):
        self.valid_attrs = attrs
        self.valid_elems = elems
        self.target = target

    def startelement(self, name, attrs):
        for attr in list(attrs.keys()):
            if attr in self.valid_attrs:
                self.target.send((self._locator.getLineNumber(), None, attrs[attr], ""))

        if name in self.valid_elems:
            self._current_ch = ""
            self._current_ch_line = self._locator.getLineNumber()

    def characters(self, ch):
        if isinstance(self._current_ch, str):
            self._current_ch += ch

    def endelement(self, name):
        if self._current_ch:
            self.target.send((self._current_ch_line, None, self._current_ch, ""))
        self._current_ch = False
        self._current_ch_line = None

    def enddocument(self):
        self.target.close()


def extract_report(fileobj, keywords, comment_tags, options):
    attrs = options["include_attrs"].split(",")
    elems = options["include_elems"].split(",")
    results = []

    @coroutine
    def extract():
        while True:
            event = yield
            results.append(event)

    parser = make_parser()
    parser.setContentHandler(StringExtractor(extract(), attrs, elems))
    parser.parse(fileobj)

    for result in results:
        yield result
