#!/usr/bin/env python3
import io
import minimalmodbus
import struct
import serial
import paho.mqtt.client as mqttClient
import time
from timeloop import Timeloop
from datetime import timedelta

smartmeter = minimalmodbus.Instrument('/dev/ttyUSB0', 1) # port name, slave address (in decimal)
smartmeter.serial.baudrate = 9600         # Baud
smartmeter.serial.bytesize = 8
smartmeter.serial.parity   = serial.PARITY_NONE # vendor default is EVEN
smartmeter.serial.stopbits = 1
smartmeter.serial.timeout  = 0.10          # seconds
smartmeter.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
smartmeter.clear_buffers_before_each_transaction = True
smartmeter.debug = False # set to "True" for debug mode

Connected = False #global variable for the state of the connection
broker_address= "broker.ritz.io"
port = 1883
user = "user"
password = "pass"

tl = Timeloop()
@tl.job(interval=timedelta(seconds=10))
def sample_job_every_10s():
    value = "{}".format(time.ctime()) #create timestamp
    client.publish("home/energy/solar/datetime",value) # publish timestamp
    f = open("/sys/class/thermal/thermal_zone0/temp", "r") # read Raspberry Pi CPU temperature
    t = f.readline ()
    t = float(t)/1000   # convert value
    client.publish("home/energy/solar/RaspPiCpuTemp",t) # publish cpu temperature in degree celsius
    try:
        Frequency = smartmeter.read_register(304, 2, 3, True)  # registeraddress, number_of_decimals=0, functioncode=3, signed=False
        client.publish("home/energy/solar/Frequency",Frequency) # publish Frequency in Hz
        Voltage = smartmeter.read_register(305, 2, 3, True)
        client.publish("home/energy/solar/Voltage",Voltage) # publish Voltage in V
        Current = smartmeter.read_long(313, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0) in mA
        Current = Current/1000
        client.publish("home/energy/solar/Current",Current) # publish Current in A
        ActivePower = smartmeter.read_long(320, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
        client.publish("home/energy/solar/ActivePower",ActivePower) # publish ActivePower in W
        ReactivePower =  smartmeter.read_long(328, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
        client.publish("home/energy/solar/ReactivePower",ReactivePower) # publish ReactivePower in Var
        ApparentPower = smartmeter.read_long(336, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
        client.publish("home/energy/solar/ApparentPower",ApparentPower) # publish ApparentPower in VA
        PowerFactor = smartmeter.read_register(344, 3, 3, True)
        client.publish("home/energy/solar/PowerFactor",PowerFactor) # publish PowerFactor
        ActiveEnergy = smartmeter.read_registers(40960, 10, 3) #read_registers(registeraddress, number_of_registers, functioncode=3)
        bits = (ActiveEnergy[0] << 16) + ActiveEnergy[1] # combining Total Energy valuepair
        s = struct.pack('>i', bits) # write to string an interpret as int
        tmp = struct.unpack('>L', s)[0] # extract from string and interpret as unsigned long
        tmpFloat = tmp/100 # needs to be converted
        client.publish("home/energy/solar/ActiveEnergy",float(tmpFloat)) # publish ActiveEnergy in kWh
        ReactiveEnergy = smartmeter.read_registers(40990, 10, 3) #read_registers(registeraddress, number_of_registers, functioncode=3)
        bits = (ReactiveEnergy[0] << 16) + ReactiveEnergy[1] # combining Total Energy valuepair
        s = struct.pack('>i', bits) # write to string an interpret as int
        tmp = struct.unpack('>L', s)[0] # extract from string and interpret as unsigned long
        tmpFloat = tmp/100 # needs to be converted
        client.publish("home/energy/solar/ReactiveEnergy",float(tmpFloat)) # publish ReactiveEnergy in kvarh
        if smartmeter.debug = True:
            FrequencyTxt = "Die Frequenz ist: %.2f Herz" % Frequency
            print (FrequencyTxt)
            VoltageTxt = "Die Spannung ist: %.2f Volt" % Voltage
            print (VoltageTxt)
            CurrentTxt = "Die Stromstärke ist: %.3f Ampere" % Current
            print (CurrentTxt)
            ActivePowerTxt = "Die Wirkleistung ist: %.2f W" % ActivePower
            print (ActivePowerTxt)
            ReactivePowerTxt = "Die Blindleistung ist: %.2f Var" % ReactivePower
            print (ReactivePowerTxt)
            ApparentPowerTxt = "Die Scheinleistung ist: %.2f VA" % ApparentPower
            print (ApparentPowerTxt)
            PowerFactorTxt = "Der Leistungsfaktor ist: %.3f " % PowerFactor
            print (PowerFactorTxt)
            #Response from meter is: [0, 130, 0, 130, 0, 0, 0, 0, 0, 0]
            #which means: Total Energy 1.3kWh, T1 Energy 1.3kWh, T2 Energy 0.0kWh, T3 Energy 0.0kWh, T4 Energy 0.0kWh
            ActiveEnergyTxt = "Zählerstand Energie ist: %.1f kWh" % tmpFloat
            print (ActiveEnergyTxt)
            ReactiveEnergyTxt = "Zählerstand Blindenergie ist: %.1f kvarh" % tmpFloat
            print (ReactiveEnergyTxt)            
        errorcode = "OK"
        client.publish("home/energy/solar/ModbusStatus",errorcode) # publish error status Modbus connection
    except:
        errorcode = "Modbus error. No connection to device"
        client.publish("home/energy/solar/ModbusStatus",errorcode) # publish error status Modbus connection
        return

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
    else:

        print("Connection failed")

client = mqttClient.Client("modbus-mqtt@raspberrypi")   #create new instance
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.connect(broker_address, port=port)          #connect to broker

client.loop_start()        #start the loop

while Connected != True:    #Wait for connection
    time.sleep(0.1)


if __name__ == "__main__":  #main loop
    tl.start(block=True)

client.disconnect()
client.loop_stop()
