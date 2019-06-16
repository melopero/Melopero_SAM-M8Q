#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca

UBX MESSAGE STRUCTURE:
        each part of the message consist of 1 byte, the length of the payload 
        (only the payload) is an unsigned 16 bit integer (little endian)
        sync char 1 | sync char 2 | class | id | lenght of payload (2 byte little endian) | payload | checksum A | checksum B
    
    NUMBER FORMATS:
        All multi-byte values are ordered in Little Endian format, unless 
        otherwise indicated. All floating point values are transmitted in 
        IEEE754 single or double precision.
    
    UBX CHECKSUM:
        The checksum is calculated over the Message, starting and including 
        the CLASS field, up until, but excluding,the Checksum Field.
        The checksum algorithm used is the 8-Bit Fletcher Algorithm:
"""

'''
NAV 0x01 Navigation Results Messages: Position, Speed, Time, Acceleration, Heading, DOP, SVs used
RXM 0x02 Receiver Manager Messages: Satellite Status, RTC Status
INF 0x04 Information Messages: Printf-Style Messages, with IDs such as Error, Warning, Notice
ACK 0x05 Ack/Nak Messages: Acknowledge or Reject messages to UBX-CFG input messages
CFG 0x06 Configuration Input Messages: Set Dynamic Model, Set DOP Mask, Set Baud Rate, etc.
UPD 0x09 Firmware Update Messages: Memory/Flash erase/write, Reboot, Flash identification, etc.
MON 0x0A Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status
AID 0x0B AssistNow Aiding Messages: Ephemeris, Almanac, other A-GPS data input
TIM 0x0D Timing Messages: Time Pulse Output, Time Mark Results
ESF 0x10 External Sensor Fusion Messages: External Sensor Measurements and Status Information 
MGA 0x13 Multiple GNSS Assistance Messages: Assistance data for various GNSS
LOG 0x21 Logging Messages: Log creation, deletion, info and retrieval
SEC 0x27 Security Feature Messages
HNR 0x28 High Rate Navigation Results Messages: High rate time, position, speed, heading
'''
NAV_CLASS = 0x01
RXM_CLASS = 0x02
INF_CLASS = 0x04
ACK_CLASS = 0x05
CFG_CLASS = 0x06
UPD_CLASS = 0x09
MON_CLASS = 0x0A
AID_CLASS = 0x0B
TIM_CLASS = 0x0D
ESF_CLASS = 0x10
MGA_CLASS = 0x13
LOG_CLASS = 0x21
SEC_CLASS = 0x27
HNR_CLASS = 0x28

SYNC_CHAR_1 = 0xB5
SYNC_CHAR_2 = 0x62

#********* NAV MESSAGE SECTION **********
NAV_PVT = 0x07

#********* ACK MESSAGE SECTION **********
ACK_ACK = 0x01
ACK_NAK = 0x00

#********* CFG MESSAGE SECTION **********
CFG_PRT = 0x00
CFG_MSG = 0x01
CFG_RATE = 0x08

#******* DEBUG/HELPING CONSTANTS ********
MAX_MESSAGE_LENGTH = 1000


#********* GNSS FIX TYPE **********
GNSS_FIX_TYPE = {0 : "no fix", 1 : "dead reckoning only", 2 : "2D-fix",
                 3 : "3D-fix", 4 : "GNSS + dead reckoning combined", 
                 5 : "time only fix"}

def compose_message(msg_class, msg_id, length = 0, payload = None):
    """returns a UBX message with given message class and id (sync chars and 
    checksum included). If a length is specified the message will be populated with
    0x00. If a payload is specified the message will be populated with the payloads
    content.
    """
    byte_length = int_to_u2(length)
    message = [SYNC_CHAR_1, SYNC_CHAR_2, msg_class, msg_id, byte_length[0], byte_length[1]]
    if payload:
        message.extend(payload)
    else:
        message.extend([0x00]*length)
    ck_a, ck_b = compute_checksum(message[2:])
    message.append(ck_a)
    message.append(ck_b)
    
    return message

def compute_checksum(message):
    ck_a = 0x00
    ck_b = 0x00
    
    for byte in message:
        ck_a += byte
        ck_b += ck_a
        ck_a &= 0xFF
        ck_b &= 0xFF
    
    return ck_a, ck_b

def msg_class_to_string(msg_cls):
    if msg_cls == NAV_CLASS:
        return "Navigation"
    elif msg_cls == RXM_CLASS:
        return "Receiver Manager"
    elif msg_cls == INF_CLASS:
        return "Information"
    elif msg_cls == ACK_CLASS:
        return "ACK/NAK"
    elif msg_cls == CFG_CLASS:
        return "Configuration"
    elif msg_cls == UPD_CLASS:
        return "Firmware update"
    elif msg_cls == MON_CLASS:
        return "Monitoring"
    elif msg_cls == AID_CLASS:
        return "AssistNow messages"
    elif msg_cls == TIM_CLASS:
        return "Timing"
    elif msg_cls == ESF_CLASS:
        return "External Sensor Fusion Messages"
    elif msg_cls == MGA_CLASS:
        return "Multiple GNSS Assistance Messages"
    elif msg_cls == LOG_CLASS:
        return "Logging"
    elif msg_cls == SEC_CLASS:
        return "Security"
    elif msg_cls == HNR_CLASS:
        return "High rate navigation results"
    
    return str(msg_cls)

def msg_id_to_string(msg_id):
    return str(msg_id)

def u2_to_int(little_endian_bytes):
    return little_endian_bytes[1] << 8 | little_endian_bytes[0]

def u4_to_int(little_endian_bytes):
    return little_endian_bytes[3] << 24 | little_endian_bytes[2] << 16 | little_endian_bytes[1] << 8 | little_endian_bytes[0]

def i2_to_int(little_endian_bytes):
    return int.from_bytes(little_endian_bytes, byteorder = 'little', signed = True)
    
def i4_to_int(little_endian_bytes):
    return int.from_bytes(little_endian_bytes, byteorder = 'little', signed = True)

def int_to_u2(integer):
    return (integer).to_bytes(2, byteorder = "little")

def int_to_u4(integer):
    return (integer).to_bytes(4, byteorder = "little")

def int_to_i2(integer):
    return (integer).to_bytes(2, byteorder = "little", signed = True)

def int_to_i4(integer):
    return (integer).to_bytes(4, byteorder = "little", signed = True)

def get_gnss_fix_type(fix_flag):
    return GNSS_FIX_TYPE.get(fix_flag, "reserved / no fix")