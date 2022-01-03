# syntax=docker/dockerfile:1
FROM ubuntu:impish
RUN apt update && apt install -y \
kamailio \
strongswan \
&& rm -rf /var/lib/apt/lists/*

COPY app app
RUN /app/install.sh

# TODO(zhuowei): deploy the configs

ENTRYPOINT ["/app/start.sh"]

LABEL \
      org.label-schema.name="VoWiFiLocalDemo" \
      org.label-schema.description="Docker container for demoing Wi-Fi calling stack" \
      org.label-schema.url="https://worthdoingbadly.com/vowifi2/" \
      org.label-schema.vcs-url="https://github.com/ExcelCoin/VoWiFiLocalDemo" \
      org.label-schema.vendor="Zhuowei Zhang" \
      org.label-schema.version=0.1 \
      org.label-schema.schema-version="1.0"

# These lines are for documentation only and have no effect.
# IPsec/IKEv2 ports
EXPOSE 500/udp 4500/udp

