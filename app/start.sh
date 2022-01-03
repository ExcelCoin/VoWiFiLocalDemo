#!/bin/bash
set -e
ip address add dev lo fdad:dabb:ed::1
kamailio
ipsec start --nofork --conf /app/ipsec.conf
