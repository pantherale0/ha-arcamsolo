# pylint: disable=line-too-long
"""Constants for arcam_solo."""

NAME = "Arcam Solo"
DOMAIN = "arcam_solo"

COMMAND_BUTTONS = [
    {
        "name": "CD Eject",
        "unique_id": "cd-eject",
        "icon": "mdi:eject",
        "ir_command": "cd_eject"
    }
]

DEFAULT_CONF_SCAN_INTERVAL = 1800 # Every 30 mins
CONF_ENABLED_FEATURES = "enabled_features"
CONF_ENABLED_BUTTONS = "enabled_buttons"

DEFAULT_CONF_ENABLED_FEATURES = [
    "virtual_remote",
    "sound_controls",
    "display_controls",
    "radio_controls",
    "virtual_buttons"
]
