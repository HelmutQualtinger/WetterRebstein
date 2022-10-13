# Bibliotheken laden
from machine import ADC
from machine import Pin, PWM, Timer
from utime import sleep
import random as r
import json  as json
import network
import time
import secrets
import umqttsimple
i=0
client=0
def tick(a):
    global client
    client.check_msg()
    
    
intled = PWM(Pin(13,3))
intled.freq(1000)


# Initialisierung des ADC4
 
#intled = machine.Pin("LED", machine.Pin.OUT)

sensor = ADC(28)  # GPIO28 on pin 34
conversion_factor = 3.3 / (4095)
# Wiederholung einleiten (Schleife)
def read_ADC():
    samples=10
    readADC=sensor.read_u16
    s=0
    s2=0
    for i in range (samples):
    # Temparatur-Sensor als Dezimalzahl lesen
        sample = readADC()>>4
        s+=sample
        s2+=sample*sample
    return (s,s2)

from umqttsimple import MQTTClient

 
led = machine.Pin("LED", machine.Pin.OUT)

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
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
time.sleep(2)

mqtt_server = '44.194.245.171'
client_id = 'calib' + str(r.randrange(2**12))
print (f"client_id {client_id}")
user_t = ''
password_t = ''

topic_pub = 'qualtinger/calib/results'
topic_sub =  'qualtinger/calib/commands'

last_message = 0
message_interval = 5
counter = 0


commands_fromhost = {}

def sub_cb(topic, msg):
    global commands_fromhost, intled
    print("New message on topic" + str(topic))
    msg = msg.decode('utf-8')
    print(msg)
    try:
        commands_fromhost = json.loads(msg)
        print(commands_fromhost)
    except:
        print(f"malformed command {msg} received")
    print (commands_fromhost.keys())
    try:
        intled.duty_u16(int(commands_fromhost["duty"]))
    except:
        pass
    try:
        intled.freq(commands_fromhost["pwmfreq"])
    except:
        pass

def mqtt_connect():
    print ("mqtt_connect")
    client = MQTTClient(client_id, mqtt_server, keepalive=60)
    print(client)
    client.connect()
    print("connected")
    client.set_callback(sub_cb)
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to MQTT Broker. Reconnecting...')
    time.sleep(5)

    
i=1
while True:
    print("Loop 1" )
    try:
        client = mqtt_connect()
        client.subscribe(topic_sub)
        Timer().init(freq=10, mode=Timer.PERIODIC, callback=tick)
        print ("Connected with client",str(client))
    except:
        print ("failed to connect")
    while True:
        print("Loop")
        s=0
        s2=0
        t1=time.ticks_ms()
        s,s2= read_ADC()
        t2=time.ticks_ms()
        print ("time ", t2-t1)
        average = s*1.0/10
        noise   = (s2*1.0/10-average*average)**0.5
        voltage=average*conversion_factor
        temperature = 27 - (voltage - 0.706)/0.001721
        msg='{"light" : '+str(average)+', "noise": '+str(noise)+', "LEDduty" : '+str(intled.duty_u16()) + ',"LEDfreq" : '+str(intled.freq()) + '}'
        try:
            client.publish(topic_pub, msg=msg)
        except:
            print("publish failed")
            pass
        print('published: '+msg)
        sleep(0.5)

    client.disconnect()