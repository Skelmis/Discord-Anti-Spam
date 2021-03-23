Extension Framework
===================

This package features/will feature a built in extensions framework soon.
This framework can be used to hook into the ``propagate`` method and run
as either a **pre-invoke** or **after-invoke** (Where **invoke** is
the built in **propagate**)

An extension can do anything, from AntiProfanity to AntiInvite.
Assuming it is class based and follows the required schema you
can easily develop your own extension that can be run whenever the
end developer calls ``await AntiSpamHandler.propagate()``

Some extensions don't need to be registered as an extension.
A good example of this is the ``AntiSpamTracker`` class.
This class does not need to be invoked with ``propagate`` as
it can be handled by the end developer for finer control.
However, it can also be used as an extension if users are
happy with the default behaviour.