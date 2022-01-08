#!/usr/bin/env python3

import sys
import datetime
import socket

# it's like encodesms.py but CDMA! :D
# https://www.3gpp2.org/Public_html/Specs/X.S0048-0_v1.0_071111.pdf
# ("The payload of the SIP MESSAGE shall contain a binary encoded SMS transport layer SMS Point-to-Point message [C.S0015]")
# https://www.3gpp2.org/Public_html/Specs/C.S0015-A_v2.0_051006.pdf
# https://www.cnblogs.com/leolcao/archive/2013/02/06/2904591.html
# https://cs.android.com/android/platform/superproject/+/master:frameworks/base/telephony/java/com/android/internal/telephony/cdma/sms/CdmaSmsAddress.java;l=203;drc=master


def rev(a):
    return "".join(reversed(a))


def bitascii(instr):
    return "".join(bin(i | 0x100)[3:] for i in instr)


def bitstrtobytes(instr):
    return bytes([int(instr[i:i + 8], 2) for i in range(0, len(instr), 8)])


# actually ASCII-7, lol, because I'm too lazy to build a proper gsm encoder
# see encodesms.py
def gsmencode(s):
    s = s.encode("ascii")
    # yes I know you can do this more efficiently
    # convert to 7-digit binary, put into a string of (little endian) bits
    b = "".join([rev(bin(i | 0b10000000)[3:]) for i in s])
    # pad to 8 bits
    t = (len(b) + 7) & ~7
    b = b + "0" * (t - len(b))
    return bytes([int(rev(b[i:i + 8]), 2) for i in range(0, len(b), 8)])


def bitpad8(frombitstr):
    frombitstr += "0" * (((len(frombitstr) + 0x7) & ~0x7) - len(frombitstr))
    return frombitstr


def datebcd(a):
    return ((a // 10) << 4) | (a % 10)


def encodesms(fromnum, text, timestamp):
    text_encoded = gsmencode(text)
    # GSM 7-bit encoding. (ok I'm lying I don't have a GSM 7-bit encoder, so I should use ASCII-7 (00010), but who cares)
    text_encoded_bitstr = "01001" + bin(len(text_encoded) |
                                        0x100)[3:] + bitascii(text_encoded)
    user_data_bytes = bitstrtobytes(bitpad8(text_encoded_bitstr))
    ts = timestamp.astimezone(datetime.timezone.utc)
    bearer_data = bytes([
        0x00,  # SUBPARAMETER_ID = Message Identifier
        0x03,  # SUBPARAMETER_LEN
        0b00010000,  # MESSAGE_TYPE = 0001 (Deliver), MESSAGE_ID = 0x0000
        0b00000000,
        0b00000000,  # HEADER_IND = 0 (user data has no header)
        0x01,  # SUBPARAMETER_ID = User Data
        len(user_data_bytes),  # SUBPARAMETER_LEN
    ]) + user_data_bytes + bytes([
        0x03,  # SUBPARAMETER_ID = Message Center Time Stamp
        0x06,  # SUBPARAMETER_LEN = 6
        datebcd(ts.year % 100),
        datebcd(ts.month),
        datebcd(ts.day),
        datebcd(ts.hour),
        datebcd(ts.minute),
        datebcd(ts.second),
    ])

    fromnumbytes = fromnum.encode("ascii")
    # DIGIT_MODE = 1 (8-bit ASCII), NUMBER_MODE = 0 (phone number), NUMBER_TYPE = 001 (international number), NUMBER_PLAN = 0001 (telephone)
    frombitstr = "100010001" + bin(len(fromnumbytes) |
                                   0x100)[3:] + bitascii(fromnumbytes)
    frombytes = bitstrtobytes(bitpad8(frombitstr))
    outbytes = bytes([
        0x00,  # SMS_MSG_TYPE = Point-to-Point
        0x00,  # PARAMETER_ID = Teleservice identifier
        0x02,  # PARAMETER_LEN = 16 bits (2 bytes)
        # https://cs.android.com/android/platform/superproject/+/master:frameworks/base/telephony/java/com/android/internal/telephony/cdma/sms/SmsEnvelope.java;l=35;drc=master
        0x10,  # Wireless Messaging Teleservice
        0x02,
        # we skip service category since we're not doing an emergency broadcast
        0x02,  # PARAMETER_ID = Originating Address
        len(frombytes),  # PARAMETER_LEN
    ]) + frombytes + bytes([
        # we skip Bearer Acknowledge since we don't need an ACK
        0x08,  # PARAMETER_ID = Bearer Data
        len(bearer_data),  # PARAMETER_LEN
    ]) + bearer_data
    return outbytes


def sendsip(smsdata, sipaddr):
    headers = "MESSAGE " + sipaddr + " SIP/2.0\r\n" + \
    "Via: SIP/2.0/UDP [::1];branch=0\r\n" + \
    "From: <sip:+15555555555@localhost>\r\n" + \
    "To: <" + sipaddr + ">\r\n" + \
    "Call-Id: 0\r\n" + \
    "CSeq: 1 MESSAGE\r\n" + \
    "Content-Length: " + str(len(smsdata)) + "\r\n" + \
    "Content-Type: application/vnd.3gpp2.sms\r\n\r\n"
    payload = headers.encode("utf-8") + smsdata
    with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as s:
        s.connect(("::1", 5060))
        s.send(payload)


def main():
    if len(sys.argv) != 4:
        print("usage: encodesms <from|emerg> <to|emu> <text>")
        print("e.g. encodesms 15556667777 13334445555 \"hello\"")
        print("send from emerg for a cell broadcast alert")
        print("send to emu for a Java array dump")
        return
    fromaddr = sys.argv[1]
    tonum = sys.argv[2]
    text = sys.argv[3]
    smsdata = encodesms(fromaddr, text, datetime.datetime.now())
    if tonum == "emu":
        header = bytes([
            0x01,  # RECEIVED_READ
            len(smsdata)
        ])
        print(",".join("(byte)" + hex(a) for a in (header + smsdata)))
        return
    sendsip(smsdata, "sip:+" + tonum + "@localhost")


if __name__ == "__main__":
    main()
