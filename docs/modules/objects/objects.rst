Object Overview
===============

The purpose of this section is to inform developers
a bit more about how this package works Internally.
For the everyday user, this will not be needed. It is
aimed at plugin developers who need to interact with 
the internals.

Anyway, internally within the rewritten package all data
is stored within a slotted ``attrs`` dataclass. Thus was 
picked over regular class's to stop boiler plate. It is also
better for its given use case when compared to a dictionary
as it is a fairly set size.

In the initial versions, we also included logic wrapped in
the same class but after the move to dataclasses the logic
was abstracted out to reduce memory overhead.


Plugin developers
-----------------

You shouldn't in most cases be interacting directly with
these class's as the package provides an interface for 
getting and setting data. Your main focus is within the 
``addons`` variable which is a dictionary which maps
the name of your plugin class to the data you wish to store.