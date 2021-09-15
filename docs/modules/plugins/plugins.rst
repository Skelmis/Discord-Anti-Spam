Package Plugin System
=====================

This package features feature a built in plugins framework soon.
This framework can be used to hook into the ``propagate`` method and run
as either a **pre_invoke** or **after_invoke** (Where **invoke** is
the built in **propagate**)

All registered extensions **must** subclass ``BasePlugin``

A plugin can do anything, from AntiProfanity to AntiInvite.
Assuming it is class based and follows the required schema you
can easily develop your own plugin that can be run whenever the
end developer calls ``await AntiSpamHandler.propagate()``

Some plugins don't need to be registered as an extension.
A good example of this is the ``AntiSpamTracker`` class.
This class does not need to be invoked with ``propagate`` as
it can be handled by the end developer for finer control.
However, it can also be used as a plugin if users are
happy with the default behaviour.

Any plugin distributed under the antispam package needs to be lib agnostic,
so as to not a dependency of something not in use.

Call Stack
----------

* Initially all checks are run, these are the checks baked into ``AntiSpamHandler``
    * You cannot avoid these checks, if you wish to mitigate them you should
      set them to values that will not be triggered
    * An option to run code before checks may be added in a future version,
      if this is something you would like, jump into discord and let me know!
      If I know people want features, they get done quicker
* Following that, all pre-invoke plugins will be run
    * The ordered that these are run is loosely based on the order that
      plugins were registered. Do not expect any form of runtime
      ordering however. You should build them around the idea that they
      are guaranteed to run before ``AntiSpamHandler.propagate``, not
      other plugins.
    * Returning ``cancel_next_invocation: True`` will result in ``propagate`` returning
      straight away. It will then return the dictionary of currently processed `pre_invoke_extensions`
* Run ``AntiSpamHandler.propagate``
    * If any pre-invoke plugin has returned a True value for ``cancel_next_invocation``
      then this method, and any after_invoke extensions will not be called.
* Run all after-invoke plugins
    * After_invoke plugins get output from both ``AntiSpamHandler``
      and all pre-invoke plugins as a method argument