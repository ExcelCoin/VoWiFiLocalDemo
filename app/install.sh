#!/bin/bash
set -e
cd /app
cp strongswan-send-p-cscf.conf /etc/strongswan.d/
cp ipsec.secrets /etc/
cp kamailio-local.cfg /etc/kamailio/
# enable ssh for root
cp ssh-permit-root-password.conf /etc/ssh/sshd_config.d/
echo "root:vowifi" | chpasswd
