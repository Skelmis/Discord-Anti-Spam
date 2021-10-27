Member Reference
================

*You should not be creating this object yourself.
It is just useful to understand how they work for say,
plugin development.*

Internally this object provides a way of storing
Messages as well as maintaining the required data to
track and punish spammers.

Please note, if you plan on working with any of the duplicate counter
values you **need** to minus 1 in order to get the **actual** value.
This is due to the fact the counter starts at 1 since we don't mark
the first message as spam due to some internal conflicts.

.. currentmodule:: antispam.dataclasses.member

.. autoclass:: Member
    :members:
    :undoc-members:
    :special-members: __init__
