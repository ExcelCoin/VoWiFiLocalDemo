#!/bin/bash
set -e
ifconfig lo add fdad:dabb:ed::1
kamailio
ipsec start --nofork --conf=/app/ipsec.conf
