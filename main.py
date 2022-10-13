# Bibliotheken laden
from machine import ADC, PWM,  Pin, Timer, I2C
from utime import sleep
import math
import network
import time
import secrets
import bme280


#importing BME280 library
i2c=I2C(0,sda=Pin(16), scl=Pin(17), freq=400000)    #initializing the I2C method 
i=0
client=0
print("Prozessor Speed",machine.freq())
def tick(a):
    global client
    client.check_msg()
# Initialisierung des ADC4
 
 
intled = machine.Pin("LED", machine.Pin.OUT)
temp_sensor = ADC(4)
light_sensor= ADC(Pin(26))
pwm=PWM(Pin(18))

# pulsed LED for calibration
pwm.freq(8)
pwm.duty_u16(32000)

conversion_factor = 3.3 / (4095)


# Wiederholung einleiten (Schleife)
def read_ADC(sensor):
    samples=100
    readADC=sensor.read_u16
    s=0
    s2=0
    for i in range (samples):
    # Temparatur-Sensor als Dezimalzahl lesen
        sample = readADC()>>4
#        if sensor==temp_sensor: print(sample)
        s+=sample
        s2+=sample*sample
    return (s,s2)

from umqttsimple import MQTTClient
import json


for i in range(2):
    wlan = network.WLAN(network.STA_IF)
    wlan.config(pm = 0xa11140)        # do not shut down WLAN
    wlan.active(False)
    wlan.active(True)
    wlan.connect(secrets.ssid, secrets.password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        intled.toggle()
        print('waiting for connection...')
        time.sleep(1)

# Handle connection error
    if wlan.status() != 3:
        print('network connection failed, try once more')
        sleep(1)
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
        break
#         
# for i in range(2):
#     try:
#         netman.connectWiFi(secrets.ssid,secrets.password,"US")
#     except:
#         time.sleep(2)
#         print("Try once more")
        
mqtt_server = '44.194.245.171' 
client_id = ''
user_t = ''
password_t = ''
topic_pub = 'qualtinger/devices/me/telemetry'
topic_sub = 'qualtinger/devices/me/command'

last_message = 0
message_interval = 5
counter = 0


def sub_cb(topic, msg):
    print("New message on topic" + str(topic))
    print(msg.decode())
    commands={}
    commands=json.loads(str(msg.decode()))
    

#        print ("received malformed JSON string: "+ str(msg))
#    print(commands)
    for command in commands:
        if command=="duty":
            pwm.duty_u16(round(commands[command]))
#            print(f"Duty set to { pwm.duty_u16()}")
        if command=="pwmfreq":
#            pwm.freq(round(commands[command]))
            print(f"Frequency set to { pwm.freq()}")
        if command=="intled":
#             intled.value(commands[command])

def tick(a):
    global client
    client.check_msg()

def mqtt_connect():
    client_id="wetterstationrebstein"
    client = MQTTClient(client_id, mqtt_server, keepalive=60)
    client.connect()
    client.set_callback(sub_cb)

    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to MQTT Broker. Reconnecting...')
    time.sleep(1)
    machine.reset()
    
import math


def taupunkt_berechnen(temperatur, rel_luftfeuchte):
    a = a_bestimmen(temperatur)
    b = b_bestimmen(temperatur)
    saettigungsdampfdruck = saettigungsdampfdruck_berechnen(a, b, temperatur)
    v = v_berechnen(rel_luftfeuchte, saettigungsdampfdruck)
    taupunkt = b*v/(a-v)
    return round(taupunkt, 2)


def v_berechnen(rel_luftfeuchte, saettigungsdampfdruck):
    dampfdruck = dampfdruck_berechnen(rel_luftfeuchte, saettigungsdampfdruck)
    v = math.log10(dampfdruck/6.1078)
    return v


def dampfdruck_berechnen(rel_luftfeuchte, saettigungsdampfdruck):
    dampfdruck = rel_luftfeuchte / 100 * saettigungsdampfdruck
    return dampfdruck


def saettigungsdampfdruck_berechnen(a, b, temperatur):
    saettigungsdampfdruck = 6.1078 * 10 ** ((a * temperatur) / (b + temperatur))
    return saettigungsdampfdruck


def a_bestimmen(temperatur):
    if temperatur >= 0:
        a = 7.5
    else:
        a = 7.6
    return a


def b_bestimmen(temperatur):
    if temperatur >= 0:
        b = 237.3
    else:
        b = 240.7
    return b

    
i=1
measurements={}
while True:
    try:
        client = mqtt_connect()
        client.subscribe(topic_sub)
        Timer().init(freq=10, mode=Timer.PERIODIC, callback=tick)
        print ("Connected with client",str(client))
    except:
        print ("failed to connect. Try reconnecting")
        machine.reset()
    while True:
        s=0
        s2=0
        s,s2=read_ADC(temp_sensor)
        average = s*1.0/100
        noise   = (s2*1.0/100-average*average)**0.5
        voltage=average*conversion_factor
        temperature = 27 - (voltage - 0.706)/0.001721
        temperature = round(temperature*100)/100.
        # msg='{"temperature": '+str(temperature)+',"noise": '+str(noise)+', "LED": '+str(intled.value())+"}"
        
        
        bme = bme280.BME280(i2c=i2c)          #BME280 object created¨
#        print ("Survived BME")
        
        intled.toggle()
        sleep(0.001)
        intled.toggle()
        
        st,sp,sh=bme.values
        st = st.replace("C",'')
        sp = sp.replace("hPa","")
        sh = sh.replace("%","")
        ft,fp,fh=(float(st),float(sp),float(sh))
        fdp = taupunkt_berechnen(ft, fh)
 #       print(str(st),str(sp),str(sh))
        measurements={}
        measurements["roomtemp"],measurements["pressure"],  \
        measurements["humidity"], measurements["dewpoint"]= (ft,fp,fh,fdp)
        measurements["proctemp"]=temperature
        s,s2=read_ADC(light_sensor)
        measurements["light"]=s/100.
        measurements["pwmfreq"]=pwm.freq()
        measurements["duty"]=pwm.duty_u16()
        measurements["intled"]=intled.value()
        msg=json.dumps(measurements)
        try:
            client.publish(topic_pub, msg=msg)
            print('published: '+msg)
        except:
            print("publish failed")
            machine.reset()
            pass

    
  #      intled.toggle()
        
        sleep(1)
    client.disconnect()