#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

import melopero_samm8q as mp
import melopero_ubx as ubx
import time

gps = mp.SAM_M8Q()

#Set the communication protocol to ubx for input and output
gps.ubx_only()
gps.wait_for_acknowledge(ubx.CFG_CLASS, ubx.CFG_PRT)

#Set the navigation message to be sent every time there is a navigation solution
gps.set_message_frequency(ubx.NAV_CLASS, ubx.NAV_PVT, 1)
gps.wait_for_acknowledge(ubx.CFG_CLASS ,ubx.CFG_MSG)

#Set the measurement frequency to 50 ms and send a navigation solution every second measurement
# this results in a navigation solution every 100ms 
gps.set_measurement_frequency(50, 2)
gps.wait_for_acknowledge(ubx.CFG_CLASS, ubx.CFG_RATE)

# Let's configure the gps device as we need it!
# For example we want to put the gps on an air balloon
# that reaches altitudes higher than 12000m (altitude limit
# for default configuration).
# We want to change the dynamic platform model 
# from the default portable model to the airborne<1g
# model. This model allows a maximum altitude of 50000m.
# If you are wondering, all this information and all available 
# messages come from the ubx protocol documentation:
# https:#www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf
# 
# Ubx messages can be written(set) and read(get/poll) to and from the device.
# In this case we want to set some configuration and then poll
# the configuration message to see if the device is setup correctly.

# 1) set desired configuration
#    the length of the payload is 36 bytes
#    note: all numbers are in little endian format!
#    payload[0:2] =  2 bytes mask that tells which parameters to set
#                    we only want the dynamic platform model: 0x0001
payload = [0] * 36
payload[0] = 0x01
payload[1] = 0x00
#    payload[2:3] =  1 byte specifying which dynamic platform model 
#                    to use: 0x06 for airborne<1g 
payload[2] = 0x06
#    to set the dynamic platform model we need to use the message 
#    with class=CFG and id=0x24, 
msg = ubx.compose_message(ubx.CFG_CLASS, 0x24, payload=payload)

# Now we can send the messgae:
gps.write_message(msg)
gps.wait_for_acknowledge(CFG_CLASS, 0x24)

# 2) read the device configuration to see if all settings are correct.
#    To poll a message we only set class and id and then we call pollUbxMessage.
#    If there are no errors the message will be populated.
msg2_payload = ubx.payload_from_message(gps.poll_message(ubx.CFG_CLASS, 0x24))

dynamic_platform_model = msg2_payload[2]
if dynamic_platform_model == 0x06:
    print("Dynamic platform model changed succesfully.")
else: 
    print("Error while changing dynamic platform model.")


#take a measurement every 0.1 seconds for an hour 
for i in range(36000):
    info = gps.get_pvt()
    
    #if there is a valid measurement
    if info:
        print("Valid time : {}, Valid date : {}".format(info[gps.VALID_TIME_TAG], info[gps.VALID_DATE_TAG]))
        print("[{}/{}/{}] {}h:{}m:{}s".format(info[gps.DAY_TAG], info[gps.MONTH_TAG], info[gps.YEAR_TAG],
              info[gps.HOUR_TAG], info[gps.MINUTE_TAG], info[gps.SECOND_TAG]))
        print("GNSS Fix: {}".format(info[gps.GNSS_FIX_TAG]))
        print("Coordinates: {} N {} E".format(info[gps.LATITUDE_TAG], info[gps.LONGITUDE_TAG]))
    
    else :
        print("Something went wrong and no measurement was taken")
    
