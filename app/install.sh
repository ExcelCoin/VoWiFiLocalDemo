#!/bin/bash
set -e
cp strongswan-send-p-cscf.conf /etc/strongswan.d/
cp ipsec.secrets /etc/
cp kamailio-local.cfg /etc/kamailio/
