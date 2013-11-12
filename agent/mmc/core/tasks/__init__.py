"""
Manage Looping, Scheduled and Delayed tasks.

If interval is specified a Looping task is created (in sec).
If delay is specified a Delayed task is created (in sec).
If cron_expression is specified a Scheduled task is created (ex: */5 * * * *).

Usage:

    from twisted.internet import reactor
    from datetime import datetime

    from mmc.core.tasks import TaskManager

    def hello(x, who=None):
        print "Hello %s !" % who
        print datetime.now()
        # throws an error
        y = 10 / x
        return y

    def err(failure):
        print "err"
        print datetime.now()
        failure.raiseException()

    def finish_delayed(call):
        print "finish_delayed"
        print datetime.now()
        print call
        print call.result
        print "End!"

    print datetime.now()
    TaskManager().addTask("my-task", [hello, [0], {"who": "world"}], interval=2).addErrback(err)
    TaskManager().addTask("my-task2", [hello, [2]], delay=4).addCallback(finish_delayed)

    reactor.run()

Output:

    2013-10-29 19:04:06.582204
    Hello world !
    2013-10-29 19:04:06.583475
    err
    2013-10-29 19:04:06.584037
    Unhandled error in Deferred:
    Unhandled Error
    Traceback (most recent call last):
      File "test2.py", line 25, in <module>
        TaskManager().add_task("my-task", [hello, [0], {"who": "world"}], interval=2).addErrback(err)
      File "/usr/lib/python2.7/site-packages/mmc/core/tasks/__init__.py", line 85, in add_task
        return self.tasks[label].start(interval)
      File "/usr/lib64/python2.7/site-packages/twisted/internet/task.py", line 163, in start
        self()
      File "/usr/lib64/python2.7/site-packages/twisted/internet/task.py", line 208, in __call__
        d = defer.maybeDeferred(self.f, *self.a, **self.kw)
    --- <exception caught here> ---
      File "/usr/lib64/python2.7/site-packages/twisted/internet/defer.py", line 134, in maybeDeferred
        result = f(*args, **kw)
      File "test2.py", line 10, in hello
        y = 10 / x
    exceptions.ZeroDivisionError: integer division or modulo by zero
    Hello None !
    2013-10-29 19:04:10.590451
    finish_delayed
    2013-10-29 19:04:10.590924
    <mmc.core.tasks.DelayedCall instance at 0x23ba950>
    5
    End!
"""

import logging
from twisted.internet import defer, reactor
from twisted.internet.task import LoopingCall
from twisted.python import reflect

from mmc.support.mmctools import SingletonN
from mmc.core.tasks.cron import CronSchedule


logger = logging.getLogger()


class TaskDoesNotExists(Exception):
    pass


class TaskManager(object):
    __metaclass__ = SingletonN

    tasks = {}

    def addTask(self, label, task=None, interval=None, cron_expression=None, delay=0):
        """
        Add a task to the task manager.

        If interval is set a looping call will be run every interval (in sec)
        If cron expression is set a scheduled call will be run according to the cron expression

        A deferred is returned to chain errback in case of exception of the task
        or other callbacks to run then when the task is done or stopped.

        If the task is already present, it will be restarted.

        @param label: task name
        @param task: tuple of (func, [func_args], {func_kwargs})
        @param interval: interval in seconds for a looping call
        @param cron_expression: cron expression for a scheduled call
        @param delay: delay in seconds for a delayed call

        @return: deferred object to chain errback or callbacks. Callbacks are
                 run when the task is finished. The callbacks take the task as
                 parameter. Errbacks take a twisted Failure instance.
        """
        if label in self.tasks:
            return self.tasks[label]._reschedule()

        if not task:
            raise Exception("Can't create any task!")

        tmp_task = [task[0]]
        try:
            tmp_task.append(task[1])
        except IndexError:
            tmp_task.append([])
        try:
            tmp_task.append(task[2])
        except IndexError:
            tmp_task.append({})

        if interval:
            self.tasks[label] = LoopingCall(tmp_task[0], *tmp_task[1], **tmp_task[2])
            logger.debug("Creating interval task %s (interval: %s)" % (label, interval))
            return self.tasks[label].start(interval)

        if cron_expression:
            self.tasks[label] = ScheduledCall(tmp_task[0], *tmp_task[1], **tmp_task[2])
            logger.debug("Creating cron task %s (cron: %s)" % (label, cron_expression))
            return self.tasks[label].start(CronSchedule(cron_expression))

        # If no delay nor interval nor cron_expression
        # a DelayedCall is run with a 0s delay
        logger.debug("Creating delayed task %s (delay: %i)" % (label, delay))
        self.tasks[label] = DelayedCall(tmp_task[0], *tmp_task[1], **tmp_task[2])
        return self.tasks[label].start(delay)

    def stopTask(self, label):
        """
        Stop a scheduled task

        @param label: task name
        """
        try:
            self.tasks[label].stop()
            del self.tasks[label]
        except KeyError:
            raise TaskDoesNotExists("Unknown task %s" % label)

    def getTask(self, label):
        try:
            return self.tasks[label]
        except KeyError:
            raise TaskDoesNotExists("Unknown task %s" % label)


class DelayedCall:
    """Call a function after a delay

    Store the function result in self.result
    """
    call = None
    running = False
    delay = None
    result = None

    def __init__(self, f, *a, **kw):
        self.f = f
        self.a = a
        self.kw = kw
        self.clock = reactor

    def start(self, delay):
        d = self.deferred = defer.Deferred()
        self.delay = delay
        self.call = self.clock.callLater(self.delay, self)
        self.running = True
        return d

    def __call__(self):
        def cb(result):
            d, self.deferred = self.deferred, None
            self.result = result
            d.callback(self)

        def eb(failure):
            self.running = False
            d, self.deferred = self.deferred, None
            d.errback(failure)

        self.call = None
        d = defer.maybeDeferred(self.f, *self.a, **self.kw)
        d.addCallback(cb)
        d.addErrback(eb)

    def stop(self):
        """Stop delayed function.
        """
        assert self.running, ("Tried to stop a DelayedCall that was "
                              "not running.")
        self.running = False
        if self.call is not None:
            self.call.cancel()
            self.call = None
            self.result = None
            d, self.deferred = self.deferred, None
            d.callback(self)

    def _reschedule(self):
        """Reschedule a the call with the same delay
        """
        return self.start(self.delay)

# ScheduledCall taken from http://code.google.com/p/twistedcronservice/
class ScheduledCall:
    """Call a function repeatedly.

    If C{f} returns a deferred, rescheduling will not take place until the
    deferred has fired. The result value is ignored.

    @ivar f: The function to call.
    @ivar a: A tuple of arguments to pass the function.
    @ivar kw: A dictionary of keyword arguments to pass to the function.
    @ivar clock: A provider of
        L{twisted.internet.interfaces.IReactorTime}.  The default is
        L{twisted.internet.reactor}. Feel free to set this to
        something else, but it probably ought to be set *before*
        calling L{start}.

    @type _lastTime: C{float}
    @ivar _lastTime: The time at which this instance most recently scheduled
        itself to run.
    """

    call = None
    running = False
    deferred = None
    schedule = None
    _lastTime = 0.0
    starttime = None

    def __init__(self, f, *a, **kw):
        self.f = f
        self.a = a
        self.kw = kw
        self.clock = reactor


    def start(self, schedule):
        """Start running function based on the provided schedule.

        @return: A Deferred whose callback will be invoked with
        C{self} when C{self.stop} is called, or whose errback will be
        invoked when the function raises an exception or returned a
        deferred that has its errback invoked.
        """
        assert not self.running, ("Tried to start an already running "
                                  "Scheduled.")

        self.schedule = schedule
        self.running = True
        d = self.deferred = defer.Deferred()
        self.starttime = self.clock.seconds()
        self._lastTime = None

        self._reschedule()

        return d

    def stop(self):
        """Stop running function.
        """
        assert self.running, ("Tried to stop a ScheduledCall that was "
                              "not running.")
        self.running = False
        if self.call is not None:
            self.call.cancel()
            self.call = None
            d, self.deferred = self.deferred, None
            d.callback(self)

    def __call__(self):
        def cb(result):
            if self.running:
                self._reschedule()
            else:
                d, self.deferred = self.deferred, None
                d.callback(self)

        def eb(failure):
            self.running = False
            d, self.deferred = self.deferred, None
            d.errback(failure)

        self.call = None
        d = defer.maybeDeferred(self.f, *self.a, **self.kw)
        d.addCallback(cb)
        d.addErrback(eb)


    def _reschedule(self):
        """
        Schedule the next iteration of this scheduled call.
        """
        if self.call is None:
            delay = self.schedule.getDelayForNext()
            self._lastTime = self.clock.seconds() + delay
            self.call = self.clock.callLater(delay, self)


    def __repr__(self):
        if hasattr(self.f, 'func_name'):
            func = self.f.func_name
            if hasattr(self.f, 'im_class'):
                func = self.f.im_class.__name__ + '.' + func
        else:
            func = reflect.safe_repr(self.f)

        return 'ScheduledCall<%s>(%s, *%s, **%s)' % (
            self.schedule, func, reflect.safe_repr(self.a),
            reflect.safe_repr(self.kw))


if __name__ == "__main__":
    from datetime import datetime

    def hello(x, who=None):
        print "Hello %s !" % who
        print datetime.now()
        # throws an error
        y = 10 / x
        return y

    def err(failure):
        print "err"
        print datetime.now()
        failure.raiseException()

    def finish_delayed(call):
        print "finish_delayed"
        print datetime.now()
        print call
        print call.result
        print "End!"

    print datetime.now()
    TaskManager().addTask("my-task", [hello, [0], {"who": "world"}], interval=2).addErrback(err)
    TaskManager().addTask("my-task2", [hello, [2]], delay=4).addCallback(finish_delayed)

    reactor.run()
