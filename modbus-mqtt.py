#!/usr/bin/env python3
import io
import minimalmodbus
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
smartmeter.debug = False

Connected = False #global variable for the state of the connection
broker_address= "broker.ritz.io"
port = 1883
user = "user"
password = "pass"

tl = Timeloop()

@tl.job(interval=timedelta(seconds=10))
def sample_job_every_10s():
    value = "{}".format(time.ctime())
    client.publish("home/energy/solar/datetime",value)
    f = open("/sys/class/thermal/thermal_zone0/temp", "r")
    t = f.readline ()
    t = float(t)/1000   # needs to be converted
    client.publish("home/energy/solar/RaspPiCpuTemp",t) # publish cpu temperature in degree celtigrade
    try:
        Frequency = smartmeter.read_register(304, 2, 3, True)  # registeraddress, number_of_decimals=0, functioncode=3, signed=False
        #FrequencyTxt = "Die Frequenz ist: %.2f Herz" % Frequency
        #print (FrequencyTxt)
        client.publish("home/energy/solar/Frequency",Frequency) # publish Frequency in Hz
        Voltage = smartmeter.read_register(305, 2, 3, True)
        #VoltageTxt = "Die Spannung ist: %.2f Volt" % Voltage
        #print (VoltageTxt)
        client.publish("home/energy/solar/Voltage",Voltage) # publish Voltage in V
        Current = smartmeter.read_long(313, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0) in mA
        Current = Current/1000
        #CurrentTxt = "Die Stromstärke ist: %.3f Ampere" % Current
        #print (CurrentTxt)
        client.publish("home/energy/solar/Current",Current) # publish Current in A
        ActivePower = smartmeter.read_long(320, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
        #ActivePowerTxt = "Die Wirkleistung ist: %.2f W" % ActivePower
        #print (ActivePowerTxt)
        client.publish("home/energy/solar/ActivePower",ActivePower) # publish ActivePower in W
        ReactivePower =  smartmeter.read_long(328, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
        #ReactivePowerTxt = "Die Blindleistung ist: %.2f Var" % ReactivePower
        #print (ReactivePowerTxt)
        client.publish("home/energy/solar/ReactivePower",ReactivePower) # publish ReactivePower in Var
        ApparentPower = smartmeter.read_long(336, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
        #ApparentPowerTxt = "Die Scheinleistung ist: %.2f VA" % ApparentPower
        #print (ApparentPowerTxt)
        client.publish("home/energy/solar/ApparentPower",ApparentPower) # publish ApparentPower in VA
        PowerFactor = smartmeter.read_register(344, 3, 3, True)
        #PowerFactorTxt = "Der Leistungsfaktor ist: %.3f " % PowerFactor
        #print (PowerFactorTxt)
        client.publish("home/energy/solar/PowerFactor",PowerFactor) # publish PowerFactor
        ActiveEnergy = smartmeter.read_float(40960, 3, 4, 0)  # registeraddress, functioncode, number_of_registers, byteorder
        #ActiveEnergyTxt = "Zählerstand Energie ist: %d kWh" % ActiveEnergy
        #print (ActiveEnergyTxt)
        client.publish("home/energy/solar/ActiveEnergy",int(ActiveEnergy)) # publish ActiveEnergy in kWh
        ReactiveEnergy = smartmeter.read_float(40990, 3, 4, 0)
        #ReactiveEnergyTxt = "Zählerstand Blindenergie ist: %d kvarh" % ReactiveEnergy
        #print (ReactiveEnergyTxt)
        client.publish("home/energy/solar/ReactiveEnergy",int(ReactiveEnergy)) # publish ReactiveEnergy in kvarh
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
