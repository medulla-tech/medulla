# -*- coding: utf-8; -*-
#
# (c) 2008-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import re

# match HH:MM:SS
RE_VALIDHOURMINSEC = '(([0-9]|[0-1][0-9]|[2][0-3]):([0-5][0-9]):([0-5][0-9]))'
# match HH:MM
RE_VALIDHOURMIN = '(([0-9]|[0-1][0-9]|[2][0-3]):([0-5][0-9]))'
# match HH
RE_VALIDHOUR = '(([0-9]|[1][0-9]|[2][0-3]))'
# match full interval
RE_VALIDSEGMENT = "^(%s|%s|%s)-(%s|%s|%s)$" % (RE_VALIDHOURMINSEC, RE_VALIDHOURMIN, RE_VALIDHOUR, RE_VALIDHOURMINSEC, RE_VALIDHOURMIN, RE_VALIDHOUR)

# minimum value of a time point
TP_MIN = "00:00:00"
# max value of a time point
TP_MAX = "23:59:59"

class TimePoint:
    """ This class represents a single time value """
    value = TP_MIN  # TP value
    valid = False   # TP validity

    def __init__(self, value = TP_MIN):
        if self._valid(value):
            self.value = self._normalize(value)
            self.valid = True

    def __str__(self):
        return self.value or ''

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def _valid(self, value):
        """ Checks for value validity """
        if value:
            return re.compile("^(%s|%s|%s)$" % (RE_VALIDHOURMINSEC, RE_VALIDHOURMIN, RE_VALIDHOUR)).match(value) != None
        return False

    def _normalize(self, value):
        """ Attempt to represent value always the same manner """
        if re.compile("^%s$" % RE_VALIDHOURMINSEC).match(value):
            matched = re.compile("^%s$" % RE_VALIDHOURMINSEC).match(value).groups()
            return "%.2d:%.2d:%.2d" % (int(matched[1]), int(matched[2]), int(matched[3]))
        elif re.compile("^%s$" % RE_VALIDHOURMIN).match(value):
            matched = re.compile("^%s$" % RE_VALIDHOURMIN).match(value).groups()
            return "%.2d:%.2d:00" % (int(matched[1]), int(matched[2]))
        elif re.compile("^%s$" % RE_VALIDHOUR).match(value):
            matched = re.compile("^%s$" % RE_VALIDHOUR).match(value).groups()
            return "%.2d:00:00" % (int(matched[1]))

TimePointMin = TimePoint(TP_MIN)
TimePointMax = TimePoint(TP_MAX)

class TimeSegment:
    """ This class represents a single time value """
    start = TimePointMin
    end = TimePointMax

    def __init__(self, start=TimePointMin, end=TimePointMax):
        self.start = start
        self.end = end

    def __str__(self):
        return "%s-%s" % (self.start.__str__(), self.end.__str__())

class TimeInterval:
    segments = []

    def __str__(self):
        return ','.join(map(lambda a: a.__str__(), self.segments))

    def add(self, segment):
        if segment.start <= segment.end:
            self.segments = self._merge_r(TimeSegment(segment.start, segment.end))
        else:
            self.segments = self._merge_r(TimeSegment(segment.start, TimePoint("23:59:59")))
            self.segments = self._merge_r(TimeSegment(TimePoint("00:00:00"), segment.end))

    def _merge_r(self, new_segment):
        """ Merges new_segment in self.segments """
        if new_segment == None:
            return self.segments
        if len(self.segments) == 0:  # nothing to be merged to, return seed
            return [new_segment]
        # try to merge
        poped_segment = self.segments.pop()
        merged_segment = _merge(poped_segment, new_segment)
        if len(merged_segment) == 1: # got one new segment after merging => ovelap
            return self._merge_r(merged_segment[0])
        if len(merged_segment) == 2: # got 2 segments after merging => no overlap
            # as there was no overlap, merged segment contains poped_segment and new_segment
            # we attempts to merge new_segment with remaining values from segments,
            # and returns poped_segment appart
            ret = self._merge_r(new_segment)
            ret.append(poped_segment)
            return ret

def _merge(s1, s2):
    """ Merges 2 TimeSegment() together
    May return 1 array of 1 segment (in case of merge)
    or 1 array of 2 segments (no merge occured)
    in this case segments are in the same order as given
    """
    # start point are the same, return the bigger one
    if s1.start == s2.start:
        if s1.end >= s2.end:
            return [s1]
        else:
            return [s2]
    # end point are the same, return the bigger one
    elif s1.end == s2.end:
        if s1.start <= s2.start:
            return [s1]
        else:
            return [s2]
    # things are getting complicated, now s1 starts before s2
    elif s1.start < s2.start:                       # s1 "starts" before s2 "starts
        if s1.end < s2.start:
            return [s1, s2]                         # s1 "finished" before s2 "starts", merge is s1, s2
        elif s1.end < s2.end:
            return [TimeSegment(s1.start, s2.end)]  # s1 "finished" before s2 "end", merge is s1.start, s2.end
        elif s1.end >= s2.end:
            return [s1]                             # s1 "finished" after s2 "end", merge is s1
    # last case: s2 starts before s1
    elif s2.start < s1.start:                       # s2 "starts" before s1 "starts
        if s2.end < s1.start:
            return [s2, s1]                         # s2 "finished" before s1 "starts", merge is s1, s2
        elif s2.end < s1.end:
            return [TimeSegment(s2.start, s1.end)]  # s2 "finished" before s1 "end", merge is s2.start, s1.end
        elif s2.end >= s1.end:
            return [s2]                             # s2 "finished" after s1 "end", merge is s2

def string2timeinterval(string):
    """ handle conversion from string to timeinterval """
    if not string:
        return None
    tp = TimeInterval()
    for segment in string.split(','):
        split = segment.split('-')
        if len(split) == 2:
            (start, end) = map(TimePoint, split)
            if not (start.valid and end.valid):
                return None
            tp.add(TimeSegment(start, end))
        else:
            return None
    return tp

def timeinterval2string(tp):
    """ handle conversion from timeinterval to string """
    if tp:
        return tp.__str__()
    return None

def normalizeinterval(string):
    tp = string2timeinterval(string)
    if tp:
        return timeinterval2string(tp)
    return None

def intimeinterval(interval, point):
    """ used to say if a point is in an interval
        interval is a regular string
        point is the "hour" value of a date
    """
    interval = string2timeinterval(interval)
    point = TimePoint(point)

    if not interval:
        return False
    if not point:
        return False

    for segment in interval.segments:
        if point >= segment.start and point <= segment.end:
            return True
    return False
