# Melopero SAM M8Q
![melopero logo](images/sensor.jpg?raw=true)

## Getting Started
### Prerequisites
You will need:
- a python3 version, which you can get here: [download python3](https://www.python.org/downloads/)
- the SAM M8Q gps: [buy here](https://www.melopero.com/shop/)

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
To use the `UBX_PROTOCOL` module it must be imported by typing the following line :
```python
import UBX_PROTOCOL as ubx
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
import SAM_M8Q
import ubx
import time
import sys

dev = SAM_M8Q()
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
