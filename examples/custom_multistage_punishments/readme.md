#### An example usage for subclassing `AntiSpamTracker`

This example subclass's `AntiSpamTracker` so that we can add
custom punishments. We first mute the user, then if 
they spam again we kick them!