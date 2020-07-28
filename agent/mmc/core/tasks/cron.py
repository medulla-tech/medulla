"""Copyright (c) 2008 Texas A&M University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import time
import datetime
import re


class CronSchedule(object):
    _minutes = None
    _hours = None
    _doms = None # days of the month
    _months = None
    _dows = None # days of the week

    def __init__(self,cron_line):
        kwargs = parseCronLine(cron_line)

        self._minutes = kwargs.get('minutes')
        self._hours = kwargs.get('hours')
        self._doms = kwargs.get('doms')
        self._months = kwargs.get('months')
        self._dows = kwargs.get('dows')

    def __eq__(self,other):
        if not isinstance(other,CronSchedule):
            return False

        return (self._minutes == other._minutes and
                self._hours   == other._hours and
                self._doms    == other._doms and
                self._months  == other._months and
                self._dows    == other._dows)

    def _getNextMonth(self, current):
        # If the current month is a valid option, try to parse for the next valid day
        if current.month in self._months:
            try:
                return self._getNextDay(current)
            except NoMatch:
                pass

        # Find the next month if it occurs in the current year
        for month in self._months:
            if month > current.month:
                return self._getFirstDay(current.replace(month=month,
                                                         day=1,
                                                         hour=self._hours[0],
                                                         minute=self._minutes[0]))

        # No remaining months this year, go to next year
        return self._getFirstDay(current.replace(year=current.year+1,
                                                 month=self._months[0],
                                                 day=1,
                                                 hour=self._hours[0],
                                                 minute=self._minutes[0]))

    def _getFirstDay(self,current):
        all_doms = False
        all_dows = False
        fdom = current.replace(day=1)

        if len(self._doms) == 31:
            all_doms = True

        if len(self._dows) == 7:
            all_dows = True

        # All days of the week and days of the month, return day = 1
        if all_doms and all_dows:
            return fdom

        # All days of the week, return first day of the month
        if all_dows:
            return current.replace(day=self._doms[0])

        dows = self._dows

        if dows[0] == 0:
            import copy
            dows = copy.copy(dows)
            del dows[0]
            dows.append(7)

        current_dow = fdom.isoweekday()

        # If the current day of the week is in the days of the week, return
        if not all_dows and current_dow in dows:
            return fdom

        # If the first day of the month is specifically listed, return it
        if not all_doms and self._doms[0] == 1:
            return fdom

        dow_distance = None
        dom_distance = None

        distance = None

        if not all_dows:
            for dow in dows:
                if dow > current_dow:
                    dow_distance = dow-current_dow
                    break

        if dow_distance is None:
            dow_distance = dows[0]+7-current_dow

        if not all_doms:
            dom_distance = self._doms[0] - 1

        if not dow_distance is None and not dom_distance is None:
            if dow_distance <= dom_distance:
                distance = dow_distance
            else:
                distance = dom_distance

        if distance is None and not dow_distance is None:
            distance = dow_distance

        if distance is None and not dom_distance is None:
            distance = dom_distance

        return current.replace(day=distance + 1)

    def _getNextDay(self, current):
        all_doms = False
        all_dows = False

        if len(self._doms) == 31:
            all_doms = True

        if len(self._dows) == 7:
            all_dows = True

        dows = self._dows

        if dows[0] == 0:
            import copy
            dows = copy.copy(dows)
            del dows[0]
            dows.append(7)

        # If the current day is a valid option, try to parse for the next valid hour
        if ((all_doms and all_dows) or
            (current.day in self._doms and all_dows) or
            (current.isoweekday() in dows and not all_dows)):
            try:
                return self._getNextHour(current)
            except NoMatch:
                pass

        distance = None

        if all_doms and all_dows:
            distance = 1
        else:
            dow_distance = None
            dom_distance = None

            if not all_dows:
                current_dow = current.isoweekday()

                for dow in dows:
                    if dow > current_dow:
                        dow_distance = dow-current_dow
                        break

                if dow_distance is None:
                    dow_distance = dows[0]+7-current_dow

            if not all_doms:
                for dom in self._doms:
                    if dom > current.day:
                        dom_distance = dom - current.day
                        break

            if not dow_distance is None and dom_distance is not None:
                if dow_distance <= dom_distance:
                    distance = dow_distance
                else:
                    distance = dom_distance

            if distance is None and dow_distance is not None:
                distance = dow_distance

            if distance is None and dom_distance is not None:
                distance = dom_distance

            if distance is None or distance <= 0:
                raise NoMatch('no matching days in month')

        next_day = (current.replace(hour=self._hours[0],
                                    minute=self._minutes[0]) +
                    distance * datetime.timedelta(days=1))

        if next_day.month != current.month:
          raise NoMatch('no remaining days in the current month')

        return next_day

    def _getNextHour(self, current):
        if current.hour in self._hours:
            try:
                return self._getNextMinute(current)
            except NoMatch:
                pass

        for hour in self._hours:
            if hour > current.hour:
                return current.replace(hour=hour,minute=self._minutes[0])

        raise NoMatch('no remaining hours in the current day')

    def _getNextMinute(self, current):
        for minute in self._minutes:
            if minute > current.minute:
                return current.replace(minute=minute)

        raise NoMatch('no remaining minutes in the current hour')

    def getNextEntry(self,current=None):
        if current is None:
            current = datetime.datetime.now()

        if not isinstance(current,datetime.datetime):
            raise ValueError('current value must be a datetime.datetime object')

        return self._getNextMonth(current.replace(second=0,microsecond=0))

    def getDelayForNext(self):
        next = self.getNextEntry()

        return time.mktime(next.timetuple()) - time.time()


class InvalidCronLine(Exception):
  pass

class InvalidCronEntry(Exception):
  pass

class NoMatch(Exception):
  pass

_cronStepRe = re.compile('^\*/(?P<step>\d{1,2})$')
_cronRangeRe = re.compile('^(?P<begin>\d{1,2})-(?P<end>\d{1,2})$')
_cronRangeStepRe = re.compile('^(?P<begin>\d{1,2})-(?P<end>\d{1,2})/(?P<step>\d{1,2})$')

def parseCronLine(line):
      """
      Parse a standard cron string (minus the command) and return them as a
      dictionary. The syntax for this was pulled from the
      Wikipedia page: http://en.wikipedia.org/wiki/Cron
      Currently, there is no support for textual days of the week
      (i.e. Monday,Tuesday).
      """
      if not line:
          raise InvalidCronLine('Empty cron line provided')

      try:
          line = re.split('\s+',line.strip())
      except:
          raise InvalidCronLine('Cron line must be a string type')

      if len(line) != 5:
          raise InvalidCronLine('Improper number of elements encountered: %s' % len(line))

      schedule = {}

      schedule['minutes'] = parseCronEntry(line[0],0,59)
      schedule['hours']   = parseCronEntry(line[1],0,23)
      schedule['doms']    = parseCronEntry(line[2],1,31)
      schedule['months']  = parseCronEntry(line[3],1,12)
      schedule['dows']    = parseCronEntry(line[4],0,6)

      return schedule

def parseCronEntry(entry,min,max):
    """Parse a single cron entry for something like hours or minutes from a cron
    scheduling line.  The given min and max are used to verify that results are
    in the proper range. The following formats are supports:
    * => All in the available range
    */5 => Only those values in the available range that are divisible by five
    1-5 => The range of 1-5
    And any combination of the above using commas to separate the entries.
    """

    if not entry:
        raise InvalidCronEntry('Empty cron entry')

    try:
        min = int(min)
        max = int(max)
    except ValueError:
        raise ValueError('minimum and maximum should be convertible to integers')

    if min > max:
        raise ValueError('minimum must be less than or equal to maximum')

    if min < 0:
        raise ValueError('minimum must be non-negative')

    try:
        entry = entry.split(',')
    except AttributeError:
        raise InvalidCronEntry('Non-string cron-entry')

    total = set()

    for e in entry:
        try:
            int_val = int(e)
        except ValueError:
            pass
        else:
            total.add(int_val)
            continue

        begin = None
        end = None
        step = 1

        if e == '*':
            begin = min
            end = max + 1

        if begin is None:
            #If this match works, then it is of the form */int
            match = _cronStepRe.search(e)

            if not match is None:
                begin = min
                end = max + 1
                step = int(match.group('step'))

        if begin is None:
            match = _cronRangeRe.search(e)

            if not match is None:
                begin = int(match.group('begin'))
                end = int(match.group('end')) + 1
                step = 1

        if begin is None:
            match = _cronRangeStepRe.search(e)

            if not match is None:
                begin = int(match.group('begin'))
                end = int(match.group('end')) + 1
                step = int(match.group('step'))

        if (begin is not None and begin < end and step > 0 and
            begin >= min and end <= max + 1):

            # need to align the start properly
            while begin % step != 0 and begin < end:
                begin += 1

            if begin == end and begin % step != 0:
                raise InvalidCronEntry('Invalid range or step specified: %s-%s/%s' % (begin,end,step))

            total.update(range(begin,end,step))
        elif not begin is None:
            raise InvalidCronEntry('Invalid range or step specified: %s-%s/%s' % (begin,end,step))

    if len(total) == 0:
        raise InvalidCronEntry('Empty cron entry')

    total = list(total)
    total.sort()

    if total[0] < min or total[len(total)-1] > max:
        raise InvalidCronEntry('Value, %s-%s, out of allowed range: %s-%s' % (total[0],total[len(total)-1],min,max))

    return total
