# orno-modbus-mqtt
Read ORNO OR-WE-514 ModbusRTU energy meter via RS485 serial and publish values to MQTT broker

The script reads the values every 10 seconds from the energy meter and publish them to the MQTT broker. Read-out and publish takes about 1 second for all values @ 9600 Baud speed and 2-3 seconds @ 2400 Baud speed.
Additionally, it publishes the CPU temperature of the Raspberry Pi and a timestamp to MQTT.
I've changed the serial setting in the meter to 9600 Baud / 8N1 with the vendor provided Windows software. Without doing this, the settings in modbus-mqtt.py must be altered to the vendor settings: 9600 Baud / 8E1.

# Parts List
- ORNO OR-WE-514 Modbus RTU Energy Meter (https://www.amazon.de/Orno-Wechselstromz%C3%A4hler-1-Phasen-Stromz%C3%A4hler-Zertifikat-Energieverbrauch/dp/B07Q1J1GJ4/ref=sr_1_1)
![Pic1](pics/OR-WE-514.jpg)
- USB-RS485 ch341-uart converter (https://www.makershop.de/module/kommunikation-module/rs485-adapter/)
![Pic2](pics/rs485-usb.PNG)

# Dependencies
Python libraries
- io
- minimalmodbus
- serial
- struct
- paho.mqtt.client
- time
- timeloop
- datetime

# Intallation:
```
pip3 install io minimalmodbus serial paho.mqtt.client time timeloop datetime
```
other:
- MQTT broker of your choice
- Linux Platform (testet on Raspian Stretch)
copy the script to a location of your choice. I've chosen /opt/modbus-mqtt/.

```
cp modbus-mqtt.py /opt/modbus-mqtt/
```

# Starting the scipt
```
# change directory
cd /opt/modbus-mqtt/
# first make the script executable:
chmod +x modbus-mqtt.py
# executing:
./modbus-mqtt.py
```
I've created a systemd service to make it running in the backround
