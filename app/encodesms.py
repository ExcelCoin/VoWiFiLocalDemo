#!/usr/bin/env python3
import sys
import datetime
import socket
import time


# Yes, I know there are about a thousand SIM libraries, but I wanted to build one
# https://mobileforensics.files.wordpress.com/2007/06/understanding_sms.pdf
def bcd(a):
    b = str(a)
    if len(b) % 2 == 1:
        b += "f"
    c = [int(b[i], 16) | (int(b[i + 1], 16) << 4) for i in range(0, len(b), 2)]
    return bytes(c)


def rev(a):
    return "".join(reversed(a))


def gsmencode(s):
    s = s.encode("ascii")
    # yes I know you can do this more efficiently
    # convert to 7-digit binary, put into a string of (little endian) bits
    b = "".join([rev(bin(i | 0b10000000)[3:]) for i in s])
    # pad to 8 bits
    t = (len(b) + 7) & ~7
    b = b + "0" * (t - len(b))
    return bytes([int(rev(b[i:i + 8]), 2) for i in range(0, len(b), 8)])


def datebcd(a):
    return ((a % 10) << 4) | (a // 10)


def encodesim(fromnum, text, timestamp):
    if len(text) > 160:
        raise Exception("too long - >160 chars")
    textencoded = gsmencode(text)
    ts = timestamp.astimezone(datetime.timezone.utc)
    outbytes = bytes([
        0x04,  # "SMS-DELIVER, TP-MMS: no more messages waiting"
        len(str(fromnum)),
        0x91,  # no extension, international phone number format
    ]) + bcd(fromnum) + bytes([
        0x00,  # TP-PID
        0x00,  # TP-DCS
        datebcd(ts.year % 100),
        datebcd(ts.month),
        datebcd(ts.day),
        datebcd(ts.hour),
        datebcd(ts.minute),
        datebcd(ts.second),
        datebcd(0),  #utc
        len(text),
    ]) + textencoded
    return outbytes


def encode_rpdata(pdu):
    smsc_num = 1_555_555_5555
    smsc_num_enc = bcd(smsc_num)
    outbytes = bytes([
        0x01,  # RP-Data (network to MS)
        0x00,  # RP message reference
        len(smsc_num_enc) +
        1,  # oddly this is number of bytes, not digits, unlike inside the SMS PDU
        0x91,  # no extension, international phone number format
    ]) + smsc_num_enc + bytes([
        0x00,  # RP-Destination Address - none
        len(pdu)
    ]) + pdu
    return outbytes


def sendsip(smsdata, sipaddr):
    headers = "MESSAGE " + sipaddr + " SIP/2.0\r\n" + \
    "Via: SIP/2.0/UDP [::1];branch=0\r\n" + \
    "From: <sip:+15555555555@localhost>\r\n" + \
    "To: <" + sipaddr + ">\r\n" + \
    "Call-Id: " + str(time.time_ns()) + "\r\n" + \
    "CSeq: 1 MESSAGE\r\n" + \
    "Content-Length: " + str(len(smsdata)) + "\r\n" + \
    "Content-Type: application/vnd.3gpp.sms\r\n\r\n"
    payload = headers.encode("utf-8") + smsdata
    with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as s:
        s.connect(("::1", 5060))
        s.send(payload)


def main():
    if len(sys.argv) != 4:
        print("usage: encodesms <from> <to|emu> <text>")
        print("e.g. encodesms 15556667777 13334445555 \"hello\"")
        print(
            "send to emu for a hex dump to pass into Android Emulator's sms pdu command"
        )
        return
    fromaddr = sys.argv[1]
    fromnum = int(fromaddr)
    tonum = sys.argv[2]
    text = sys.argv[3]
    if tonum == "emu":
        print("00" + encodesim(fromnum, text, datetime.datetime.now()).hex())
        return
    rpdata = encode_rpdata(encodesim(fromnum, text, datetime.datetime.now()))
    sendsip(rpdata, "sip:+" + tonum + "@localhost")


if __name__ == "__main__":
    main()
