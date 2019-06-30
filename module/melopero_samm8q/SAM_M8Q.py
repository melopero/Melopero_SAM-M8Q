#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""
from smbus2 import SMBus, i2c_msg, SMBusWrapper
import melopero_ubx as ubx
import time

class SAM_M8Q():
    
    _DEFAULT_I2C_ADDRESS = 0x42
    _DATA_STREAM_REGISTER = 0xFF
    
    YEAR_TAG = "year"
    MONTH_TAG = "month"
    DAY_TAG = "day"
    HOUR_TAG = "hour"
    MINUTE_TAG = "minute"
    SECOND_TAG = "second"
    
    VALID_TIME_TAG = "valid_time"
    VALID_DATE_TAG = "valid_date"
    FULLY_RESOLVED_TAG = "fully_resolved"
    VALID_MAG_DEC_TAG = "valid_magnetic_declination"
    
    GNSS_FIX_TAG = "GNSS_FIX"
    FIX_STATUS_FLAGS_TAG = "fix_flags"
    NUM_SATELLITES_TAG = "num_satellites"
    
    LATITUDE_TAG = "latitude"
    LONGITUDE_TAG = "longitude"
    ELLIPSOID_HEIGHT_TAG = "ellipsoid_height"
    MSL_HEIGHT_TAG = "MSL_height"
    HORIZONTAL_ACCURACY_TAG = "horizontal_accuracy"
    VERTICAL_ACCURACY_TAG = "vertical_accuracy"
    
    NED_VELOCITY_TAG = "NED_velocity"
    GROUND_SPEED_TAG = "ground_speed"
    VEHICLE_HEADING_TAG = "vehicle_heading"
    MOTION_HEADING_TAG = "motion_heading"
    SPEED_ACCURACY_TAG = "speed_accuracy"
    HEADING_ACCURACY_TAG = "heading_accuracy"
    
    MAGNETIC_DECLINATION_TAG = "magnetic_declination"
    MAG_DEC_ACCURACY_TAG = "mag_deg_acc"
  
    def __init__(self, i2c_addr = _DEFAULT_I2C_ADDRESS, i2c_bus = 1):
        self.curr_i2c_addr = i2c_addr
        self.curr_i2c_bus = i2c_bus
        self.pvt_data = dict()
        time.sleep(.1) # Allows the device to setup Avoids i2c error 5
        
    def ubx_only(self):
        """Sets the communication protocol to UBX (only) both for input and output"""
        payload = [0x00, 0x00, 0x00, 0x00, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00, 
                   0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = ubx.compose_message(ubx.CFG_CLASS, ubx.CFG_PRT, 20, payload)
        self.write_message(message)
    
    def set_message_frequency(self, msg_class, msg_id, freq = 0x01):
        """Send rate is relative to the event a message is registered on. 
        For example, if the rate of a navigation message is set to 2, 
        the message is sent every second navigation solution"""
        payload = [msg_class, msg_id, freq, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = ubx.compose_message(ubx.CFG_CLASS, ubx.CFG_MSG,8,payload)
        self.write_message(message)
        
    def set_measurement_frequency(self, measurement_period_ms = 1000, navigation_rate = 1, timeref = 0):
        """measurement_period:
            elapsed time between GNSS measurements, which defines the rate, 
            e.g. 100ms => 10Hz, Measurement rate should be greater than or
            equal to 25 ms.\n
        navigation_rate : 
            The ratio between the number of measurements and the number of 
            navigation solutions, e.g. 5 means five measurements for
            every navigation solution. Maximum value is 127. \n
        timeref : 
            The time system to which measurements are aligned:
            0: UTC time\n
            1: GPS time\n
            2: GLONASS time (not supported in protocol versions less than 18)\n
            3: BeiDou time (not supported in protocol versions less than 18)\n
            4: Galileo time (not supported in protocol versions less than 18)"""
        payload = []
        payload.extend(ubx.int_to_u2(measurement_period_ms))
        payload.extend(ubx.int_to_u2(navigation_rate))
        payload.extend(ubx.int_to_u2(timeref))
        message = ubx.compose_message(ubx.CFG_CLASS, ubx.CFG_RATE, 6, payload)
        self.write_message(message)
        
    def available_bytes(self):
        """ returns the number of bytes available if a timeout is specified it 
        tries to read the number of bytes for the given amount of millis"""
        with SMBusWrapper(self.curr_i2c_bus) as bus:
            msb = bus.read_byte_data(self.curr_i2c_addr, 0xFD)
            lsb = bus.read_byte_data(self.curr_i2c_addr, 0xFE)
        return msb << 8 | lsb
        
    def write_message(self, buffer):
        with SMBusWrapper(self.curr_i2c_bus) as bus:
            msg_out = i2c_msg.write(self.curr_i2c_addr, buffer)
            bus.i2c_rdwr(msg_out)

        
    def read_message(self):
        msg_length = self.available_bytes()
        msg = []
        if msg_length > ubx.MAX_MESSAGE_LENGTH:
            return msg
        
        with SMBusWrapper(self.curr_i2c_bus) as bus:
            for _ in range(msg_length):
                msg.append(bus.read_byte_data(self.curr_i2c_addr, self._DATA_STREAM_REGISTER))
                
        return msg
    
    def wait_for_message(self, time_out_s = 1, interval_s = 0.01, msg_cls = None, msg_id = None):
        """ waits for a message of a given class and id.\n
        time_out_s : 
            the maximum amount of time to wait for the message to arrive in seconds.
        interval_s :
            the interval in seconds between a two readings.
        msg_cls :
            the class of the message to wait for.
        msg_id :
            the id of the message to wait for."""
        start_time = time.time()
        to_compare = [ubx.SYNC_CHAR_1, ubx.SYNC_CHAR_2]
        if msg_cls:
            to_compare.append(msg_cls)
        if msg_id:
            to_compare.append(msg_id)
            
        while time.time() - start_time < time_out_s:
            msg = self.read_message()
            if len(msg) >= len(to_compare):
                if msg[:len(to_compare)] == to_compare:
                    return msg
            time.sleep(interval_s)
        return None
    
    def wait_for_acknowledge(self, msg_class, msg_id, verbose = True):
        """ An acknowledge message (or a Not Acknowledge message) is sent everytime
        after a configuration message is sent."""
        ack = False
        msg = self.wait_for_message(msg_cls = ubx.ACK_CLASS)
        if msg is None: 
            print("No ACK/NAK Message received")
            return ack
        
        if msg[3] == ubx.ACK_ACK:
            ack = True
        
        if verbose:
            print(" A message of class : {} and id : {} was {}acknowledged".format(
                    ubx.msg_class_to_string(msg[6]), msg[7], (not ack) * "not "))
        
        return ack
    
    def get_pvt(self, polling = True, time_out_s = 1):
        """updates and returns the pvt_data dictionary that contains the last received
        pvt data.\n 
        polling :
            if true the pvt message is polled, else waits for the next navigation solution
        time_out_s :
            the maximum time to wait for the message
            
        To reduce the time between pvt messages the frequency of the message can be 
        increased with set_message_frequency and set_measurement_freq
        """
        if polling:
            #send polling message
            message = ubx.compose_message(ubx.NAV_CLASS, ubx.NAV_PVT)
            self.write_message(message)
        
        #reads response
        read = self.wait_for_message(time_out_s = time_out_s, msg_cls = ubx.NAV_CLASS, msg_id = ubx.NAV_PVT)
        if read is not None:
            start_payload = 6
            #WARNING: POSITION_DOP AND ITOW ARE MISSING (NOT RETRIEVED)
            
            #Time solution
            year = ubx.u2_to_int(read[start_payload+4:start_payload+6])
            month = read[start_payload+6]
            day = read[start_payload+7]
            hour = read[start_payload+8]
            minutes = read[start_payload+9]
            sec = read[start_payload+10]
            valid_flag = read[start_payload+11]
            
            #clarifying flags
            valid_date = 0x01 & valid_flag == 0x01
            valid_time = 0x02 & valid_flag == 0x02
            fully_resolved = 0x04 & valid_flag == 0x04
            valid_mag = 0x08 & valid_flag == 0x08
            
            #GNSS fix and flags
            gnss_fix = ubx.get_gnss_fix_type(read[start_payload+20])
            fix_status_flags = read[start_payload+21:start_payload+23]
            num_satellites = read[start_payload+23]
            
            #longitude and latitude are in Degrees
            longitude = ubx.i4_to_int(read[start_payload+24: start_payload+28]) * 1e-07
            latitude = ubx.i4_to_int(read[start_payload+28: start_payload+32]) * 1e-07
            
            
            #height, mean sea level height in millimeters
            height = ubx.i4_to_int(read[start_payload+32: start_payload+36])
            height_MSL = ubx.i4_to_int(read[start_payload+36: start_payload+40])
            
            #horizontal and vertical accuracy estimates in millimeters
            h_acc = ubx.u4_to_int(read[start_payload+40: start_payload+44])
            v_acc = ubx.u4_to_int(read[start_payload+44: start_payload+48])
            
            #North East Down velocity in mm / s
            n_vel = ubx.i4_to_int(read[start_payload+48: start_payload+52])
            e_vel = ubx.i4_to_int(read[start_payload+52: start_payload+56])
            d_vel = ubx.i4_to_int(read[start_payload+56: start_payload+60])
            
            #Ground speed in mm / s and heading of motion in degrees + speed and heading accuracy estimates
            g_speed = ubx.i4_to_int(read[start_payload+60: start_payload+64])
            motion_heading = ubx.i4_to_int(read[start_payload+64: start_payload+68]) * 1e-05
            s_acc = ubx.u4_to_int(read[start_payload+68: start_payload+72])
            m_acc = ubx.u4_to_int(read[start_payload+72: start_payload+76]) * 1e-05
            
            #Heading of vehicle in degrees
            vehicle_heading = ubx.i4_to_int(read[start_payload+84: start_payload+88]) * 1e-05
            
            #Magnetic declination and magnetic declination accuracy both in degrees
            mag_deg = ubx.i2_to_int(read[start_payload+88: start_payload+90]) * 1e-02
            mag_deg_acc = ubx.u2_to_int(read[start_payload+90: start_payload+92]) * 1e-02
            
            #time
            self.pvt_data[self.YEAR_TAG] = year
            self.pvt_data[self.MONTH_TAG] = month
            self.pvt_data[self.DAY_TAG] = day
            self.pvt_data[self.HOUR_TAG] = hour
            self.pvt_data[self.MINUTE_TAG] = minutes
            self.pvt_data[self.SECOND_TAG] = sec
            
            #flags
            self.pvt_data[self.VALID_TIME_TAG] = valid_time
            self.pvt_data[self.VALID_DATE_TAG] = valid_date
            self.pvt_data[self.FULLY_RESOLVED_TAG] = fully_resolved
            self.pvt_data[self.VALID_MAG_DEC_TAG] = valid_mag
            
            #GNSS
            self.pvt_data[self.GNSS_FIX_TAG] = gnss_fix
            self.pvt_data[self.FIX_STATUS_FLAGS_TAG] = fix_status_flags
            self.pvt_data[self.NUM_SATELLITES_TAG] = num_satellites
            
            #Coordinates
            self.pvt_data[self.LONGITUDE_TAG] = longitude
            self.pvt_data[self.LATITUDE_TAG] = latitude
            self.pvt_data[self.ELLIPSOID_HEIGHT_TAG] = height
            self.pvt_data[self.MSL_HEIGHT_TAG] = height_MSL
            self.pvt_data[self.HORIZONTAL_ACCURACY_TAG] = h_acc
            self.pvt_data[self.VERTICAL_ACCURACY_TAG] = v_acc
            
            #Velocity and heading
            self.pvt_data[self.NED_VELOCITY_TAG] = (n_vel, e_vel, d_vel)
            self.pvt_data[self.GROUND_SPEED_TAG] = g_speed
            self.pvt_data[self.VEHICLE_HEADING_TAG] = vehicle_heading
            self.pvt_data[self.MOTION_HEADING_TAG] = motion_heading
            self.pvt_data[self.SPEED_ACCURACY_TAG] = s_acc
            self.pvt_data[self.HEADING_ACCURACY_TAG] = m_acc
            
            #Magnetic declination
            self.pvt_data[self.MAGNETIC_DECLINATION_TAG] = mag_deg
            self.pvt_data[self.MAG_DEC_ACCURACY_TAG] = mag_deg_acc
            
            return self.pvt_data
        
        return None
    