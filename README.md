# Melopero_SAM-M8Q_Arduino_Library
A library for interfacing the <b>Melopero SAM-M8Q Multi GNSS breakout board</b> with a Raspberry Pi.
<br> If you were looking for the Arduino library click [HERE](https://github.com/melopero/Melopero_SAM-M8Q_Arduino_Library)

# Melopero SAM M8Q
![melopero logo](images/Melopero-SAM-M8Q-diagonal.jpg?raw=true)

# Pinouts

<table style="width:100%">
  <tr>
    <th>Melopero SAM-M8Q</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>3V3</td>
    <td>Input power pin. Apply 3.3V to this pin</td>
  </tr>
  <tr>
    <td>SCL</td>
    <td>I2C Serial CLock pin</td>
  </tr>
  <tr>
    <td>SDA</td>
    <td>I2C Serial DAta pin</td>
  </tr>
  <tr>
    <td>GND</td>
    <td>Ground pin</td>
  </tr>
  <tr>
    <td>INT</td>
    <td>External Interrupt pin (INPUT)</td>
  </tr>
  <tr>
    <td>SAF</td>
    <td>SAFEBOOT_N pin, for future service, updates and reconfiguration </td>
  </tr>
  <tr>
    <td>RST</td>
    <td>RESET pin, INPUT, Active Low</td>
  </tr>
  <tr>
    <td>PPS</td>
    <td>Pulse Per Second pin, OUTPUT, connected to the Blue LED</td>
  </tr>
  <tr>
    <td>VBA</td>
    <td>V_BACKUP pin, INPUT. This pin accepts a voltage in the 3.3V-6V range. By applying a voltage to this pin, you will automatically disable the coin cell battery and avoid the installation of the optional CR1220 battery holder, while still allowing a warm start of the GNSS module.
      </td>
  </tr> 
</table>

# FTDI header
At the top of the board you'll find the pinout for connecting a FTDI cable (<b>only FTDI cables with 3.3V data and power line!</b>)

## Getting Started
### Prerequisites
You will need:
- a python3 version, which you can get here: [download python3](https://www.python.org/downloads/)
- the SAM M8Q gps: [buy here](https://www.melopero.com/shop/)

### Connect the sensor to the Raspberry Pi
You can find a description of the GPIO connector of the Raspberry Pi [HERE](https://www.raspberrypi.org/documentation/usage/gpio/)
<br>(use <b>only 3.3V power and logic</b>, DO NOT connect this sensor board directly to 5V)
<br>The SAM-M8Q communicates over I2C:
<table style="width:100%">
  <tr>
    <th>Melopero SAM-M8Q</th>
    <th>Raspberry Pi</th> 
  </tr>
  <tr>
    <td>3V3</td>
    <td>3.3V</td> 
  </tr>
  <tr>
    <td>SCL</td>
    <td>SCL</td> 
  </tr>
  <tr>
    <td>SDA</td>
    <td>SDA</td> 
  </tr>
  <tr>
    <td>GND</td>
    <td>GND</td> 
  </tr>
</table>

### Installing
You can install the melopero-samm8q module by typing this line in the terminal:
```python
sudo pip3 install melopero-samm8q
```

## Module description
The module contains a class to easily access the SAM m8Q's gps functions.

### Usage
First you need to import the module in your file:
```python
import melopero_samm8q as mp #nome provvisorio
```
Then you can create a SAM_M8Q object and access it's methods, the gps object will be initialized with the i2c address set to `0x42` and the i2c bus to `1` alias `(dev/i2c-1)` which is the standard i2c bus in a Raspberry pi.
```python
sensor = mp.SAM_M8Q()
```
Alternatively you can modify it's parameters by typing
```python
sensor = mp.SAM_M8Q(i2c_addr = myaddress, i2c_bus = mybus)
```
#### UBX protocol
The module uses the UBX protocol over I2C to comunicate with the device. The NMEA messages are not disabled by default, they can be disabled by calling `sensor.ubx_only()`. This method causes the device to comunicate only through the UBX protocol.

The most used/useful UBX messages are implemented in the module, if someone wants to send other/custom messages to the device they can be easily crafted and parsed through the `UBX_PROTOCOL` module.

##### Features
###### Communication
There are several methods to send and receive messages:
```python
#*** SENDING MESSAGES ***
device.write_message(message)

#*** RECEIVING MESSAGES ***
device.read_message()
device.wait_for_message(time_out_s = 1, interval_s = 0.01, msg_cls = None, msg_id = None)
device.wait_for_acknowledge(msg_cls, msg_id)
```
###### PVT
The results of a navigation solution are stored in a dictionary: `pvt_data`. The dictionary maps strings (the name of the attributes) to their respective values. For example this line returns the longitude :
`device.pvt_data["longitude"]`. To update the data stored in `pvt_data` the method `device.get_pvt(polling = True, time_out_s = 1)` must be called. This method updates the data and returns the `pvt_data` dictionary, therefore this two codes are equivalent:
```python
info = device.get_pvt()
print("We are in {}!".format(info["year"]))
```
```python
device.get_pvt()
print("We are in {}".format(device.pvt_data["year"]))
```

###### Crafting messages
To use the `melopero_ubx` module it must be imported by typing the following line :
```python
import melopero_ubx as ubx
```

Then a message can be created with the function:
```python
ubx.compose_message(msg_cls, msg_id, length = 0, payload = None)
```
The function returns the message which can be sent with the method : `sensor.write_message(message)`.
If the lenght and the payload are not specified a polling message (with no payload, used to poll messages and data) is created and returned.

## Example
The following example, will write to a file the coordinates and time of the device every 5 seconds for 25 minutes.
```python
import melopero_samm8q as mp
import melopero_ubx as ubx
import time
import sys

dev = mp.SAM_M8Q()
dev.ubx_only()
dev.wait_for_acknowledge(ubx.CFG_CLASS, ubx.CFG_PRT)
dev.set_message_frequency(ubx.NAV_CLASS, ubx.NAV_PVT, 1)
dev.wait_for_acknowledge(ubx.CFG_CLASS ,ubx.CFG_MSG)
dev.set_measurement_freq(500, 1)
dev.wait_for_acknowledge(ubx.CFG_CLASS, ubx.CFG_RATE)

#One Measurement every 5 seconds for 300 times
#means 5 * 300 seconds = 1500 seconds = 25 minutes
log_file_name = "log_{}.txt".format(int(time.time() % 1000))
for i in range(300):
    print("Measurement {} / 300".format(i))
    try:
        info = dev.get_pvt() #returns a dictionary containing the PVT data
        if info is not None:
            with open(log_file_name, 'a') as log_file:
              log_file.write("[{}/{}/{}] {}h:{}m:{}s".format(info['year'], info['month'], info['day'],
                                 info['hour'], info['minute'], info['second']))
              log_file.write('\n')
              log_file.write("Longitude : ")
              log_file.write(str(info["longitude"]))
              log_file.write('\n')
              log_file.write("Latitude : ")
              log_file.write(str(info["latitude"]))
              log_file.write('\n')
              log_file.write('\n')
              log_file.flush()
    except:
        print("Unexpected error:", sys.exc_info()[0])

    time.sleep(5)
```
![Connection with a Raspberry Pi](/images/Melopero-SAM-M8Q-with-Raspberry-Pi-4-B.jpg)
