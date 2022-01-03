#!/bin/bash
set -e
ip address add dev lo fdad:dabb:ed::1
mkdir /run/sshd || true
/usr/sbin/sshd
kamailio
ipsec start --nofork --conf /app/ipsec.conf
