Optimising Package Usage
========================

I'll be the first to admit it, this package could be better
when it comes to optimization for bigger bots or extended usage.

Going forward, I plan on adding things you *should* be using on a task
every day or so to cleanup caches. However, at the end of the day it
will entirely come down to the end user.

Implementation Notes
^^^^^^^^^^^^^^^^^^^^

This package heavily uses OOP to store data. This, tied in with
the fact any classes instances outside of ``Message`` instances
are not cleaned up (Exist forever) can lead to memory usage over time.
This will be remedied in the future through a method you call on a dpy task.


I do eventually plan/hope/want to allow for using redis, however, that is still
quite awhile away and likely will require a heavy rewrite. If this is something
you want in your bot however, please reach out to me. People wanting things is quite
a good motivator.