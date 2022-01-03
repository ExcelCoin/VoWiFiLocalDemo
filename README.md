Docker container for demoing Wi-Fi calling stack.

## Usage:

```
docker-compose build
docker-compose up
```

Point [RedirectVoWiFiTweak](https://github.com/ExcelCoin/RedirectVoWiFiTweak)
to your computer's IP address.

Install it on a jailbroken phone, enable Wi-Fi calling, and you should see a
VPN connection into the container.

There's a ssh daemon on port 22222 for debugging: the password is
`root:vowifi`. It's useful for using sshdump from Wireshark.

[baresip](https://github.com/baresip/baresip), a popular command line SIP VoIP
app, is also preinstalled. If you ssh in, you can run:

```
ssh -p 22222 root@localhost
baresip
/uanew sip:+15554443333@localhost
/dial sip:+19085823275@localhost
```

to ring your connected phone (replace +1 908-582-3275 with its number).

_be careful!_ do not expose the ssh daemon or the VPN to untrusted devices.

## Setup

Currently the Kamailio config is set up for a Verizon SIM, with domain set to
`vzims.com`.

For other providers, capture a SIP REGISTER from the phone (using rvictl on a
Mac), look at the domain, and edit app/kamailio-local.cfg.

For more info, see [the blog post](https://worthdoingbadly.com/vowifi2/).
