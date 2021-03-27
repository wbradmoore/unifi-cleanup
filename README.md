# unifi-cleanup

Code mostly yoinked from aiounifi repo.

Removes random MAC addresses that show up in Unifi controller (and clog up Home Assistant)

Example use:

python3 unifi-cleanup.py --port 443 192.168.10.10 ubnt myUnifiPassword