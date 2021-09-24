# unifi-cleanup

This is a single-function tool to remove random MAC addresses accumulated in the Unifi controller. These clutter up the UI, as well as the Unifi integration for Home Assistant. This will not remove any manually named devices, nor devices with any nonzero Tx/Rx history.

**Example dependency setup:**

    sudo apt install python3 python3-pip
    pip install -r requirements.txt

**Example use:**

    python3 unifi-cleanup.py --port 443 192.168.10.10 myUsername myUnifiPassword

Note that the IP address is that of the controller, not (necessarily) the gateway. 

(Thanks to aiounifi repo for much of code handling auth/etc.)
