from mmc.core.signals import Signal

# Signal sent when a ppolicy is applied on a user
ppolicy_applied = Signal(providing_args=["ppolicy_name"])
# Signal sent when a ppolicy is removed from a user
ppolicy_removed = Signal()

# Signal sent when a ppolicy attribute is changed
ppolicy_attr_changed = Signal(providing_args=["ppolicy_name", "ppolicy_attr", "ppolicy_attr_value"])
