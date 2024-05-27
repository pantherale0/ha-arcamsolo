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
| `button`       | A virtual button to eject the CD drive               |
| `number`       | Creates entities to control balance, bass, treble and brightness. Radio frequency not yet supported fully. |
| `remote`       | Creates a virtual remote to send IR commands to. For a list of supported commands, please see [pyarcamsolo](https://github.com/pantherale0/pyarcamsolo/blob/e56d677abb3c54f7dd629d2f14db088647c691ec/pyarcamsolo/commands.py#L149) |

## Installation

1. The module this integration uses assumes you have created a serial to IP bridge to connect the RS232 port (using a null modem cable) to your local network. If you haven't done this already, please setup a ser2net bridge (or similar).
1. Add repository to HACS as an integration
1. Search and install "Arcam Solo"
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Arcam Solo"

## Helpful resources / notes

- [ser2net setup](https://wifizoo.org/2023/05/12/yet-another-ser2net-tutorial/)

The port speed of your amp may be different compared to what is in the manual, during testing I found that the RS232 protocol does not work reliably when the port speed is set to 9600, after a lot of trial and error I found port speed 38400 to work well. My ser2net settings are as follows:
```
connection: &con1096
  accepter: tcp,SERVER_IP_HERE,2000
  enable: on
  connector: serialdev,/dev/ttyUSB0,38400n81,local
```
This configuration will create a TCP listener on your host available on port 2000 (replace SERVER_IP_HERE with the IP address of the machine hosting ser2net) for the serial device available at `/dev/ttyUSB0`.

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