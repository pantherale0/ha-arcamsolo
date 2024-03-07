# Integration Blueprint

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Integration to integrate with Arcam Solo Hi-Fi units_

**This integration will set up the following platforms.**

| Platform       | Description                                          |
| -------------- | ---------------------------------------------------- |
| `media_player` | Represents the master zone for the connected device. |

## Installation

1. The module this integration uses assumes you have created a serial to IP bridge to connect the RS232 port (using a null modem configuration) to your local network. If you haven't done this already, see the bottom of the readme for further guidance.
1. Add repository to HACS as an integration
1. Search and install "Arcam Solo"
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Arcam Solo"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[ha-arcamsolo]: https://github.com/pantherale0/ha-arcamsolo
[buymecoffee]: https://www.buymeacoffee.com/pantherale0
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/pantherale0/ha-arcamsolo.svg?style=for-the-badge
[commits]: https://github.com/pantherale0/ha-arcamsolo/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/pantherale0/ha-arcamsolo.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-pantherale0-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/pantherale0/ha-arcamsolo.svg?style=for-the-badge
[releases]: https://github.com/pantherale0/ha-arcamsolo/releases
