# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Qaction represents a qaction file
PULSE2_DEPRECATED
"""
import logging

log = logging.getLogger()

# class Qaction:
# keywords = ['command', 'titlefr', 'titleuk']
# r_qaction = re.compile(r'^\s*(?P<key>\S+)\s*=\s*(?P<value>.*)$')

# def __init__(self, filename):
# self.filename = filename
# self.fullfilename = os.path.join(MscConfig().qactionspath, filename)
# self.result = {}
# self._parse()

# def read(self):
# ret = {}
# for k in self.result:
# ret[k] = self.result[k]

# ret['fullfilename'] = self.fullfilename
# ret['filename'] = self.filename
# ret['titleen'] = self.result['title']
# ret['titleuk'] = self.result['title']
# return ret

# def _parse(self):
# f = open(self.fullfilename, 'r')

# for line in f:
# m = self.r_qaction.match(line)
# if m:
# self.result[m.group('key')] = m.group('value')
# else:
# log.debug('Ignore qaction line: %s' % line)
# f.close()

# def qa_list_files():
# path = MscConfig().qactionspath
# if not os.path.exists(path):
# return [False, "Quick action path don't exists", path]

# result = {}
# d = dircache.listdir(path)
# d = d[:]

# for filename in dircache.listdir(path):
# if filename != '..' and filename != '.' and os.path.exists(os.path.join(path, filename)) and re.compile('\.msc$').search(filename):
# result[filename] = Qaction(filename).read()

# return [True, result]

# def qa_detailled_info(filename):
# path = MscConfig().qactionspath
# if not os.path.exists(os.path.join(path, filename)):
# return [False, "This quick action don't exists!", filename]

# qa = Qaction(filename)
# qa = qa.read()
# return [True, qa]
