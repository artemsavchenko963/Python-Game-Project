"""
Weapon: a small data holder for one weapon's stats. It doesn't do
anything by itself -- no pygame, no drawing, no cooldown logic -- it's
just three numbers with a name attached. Player reads these numbers when
firing and when resetting its own cooldown timer.

Keeping this as plain data (rather than, say, giving each weapon its own
fire() method) means adding a third or fourth weapon later is just adding
another Weapon(...) with different numbers -- no new code paths.
"""


class Weapon:
    def __init__(self, name, damage, fire_interval, projectile_speed):
        self.name = name
        self.damage = damage
        self.fire_interval = fire_interval
        self.projectile_speed = projectile_speed