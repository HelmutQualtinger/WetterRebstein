# Bibliotheken laden
from machine import ADC
from machine import Pin, Timer
from utime import sleep
import network
import time
import secrets
i=0
client=0
def tick(a):
    global client
    client.check_msg()
# Initialisierung des ADC4
 
intled = machine.Pin("LED", machine.Pin.OUT)
sensor = ADC(4)
conversion_factor = 3.3 / (4095)
# Wiederholung einleiten (Schleife)
def read_ADC():
    samples=1000
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

mqtt_server = 'thingsboard.cloud'
client_id = 'wetterstation'
user_t = 'rebstein'
password_t = ''
topic_pub = 'v1/devices/me/telemetry'

last_message = 0
message_interval = 5
counter = 0
mqtt_server = 'thingsboard.cloud'
client_id = ''
topic_sub =  'v1/devices/me/telemetry'


def sub_cb(topic, msg):
    print("New message on topic" + str(topic))
    msg = msg.decode('utf-8')
    print(msg)
    if msg == "on":
        intled.on()
    elif msg == "off":
        intled.off()

def mqtt_connect():
    client_id="wetterstation"
    client = MQTTClient(client_id, mqtt_server, keepalive=60)
    client.connect()
    client.set_callback(sub_cb)

    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()
    
i=1
while True:
    try:
        client = mqtt_connect()
        client.subscribe(topic_sub)
        Timer().init(freq=10, mode=Timer.PERIODIC, callback=tick)
        print ("Connected with client",str(client))
    except:
        print ("failed to connect")
    while True:
        s=0
        s2=0
        t1=time.ticks_ms()
        s,s2= read_ADC()
        t2=time.ticks_ms()
        print ("time ", t2-t1)
        average = s*1.0/1000
        noise   = (s2*1.0/1000-average*average)**0.5
        voltage=average*conversion_factor
        temperature = 27 - (voltage - 0.706)/0.001721
        msg="{temperature:"+str(temperature)+",noise:"+str(noise)+",LED:"+str(intled.value())+"}"
        try:
            client.publish(topic_pub, msg=msg)
        except:
            print("publish failed")
            client=mqtt_connect()
            pass
        print('published: '+msg)
    
        intled.toggle()
        
        sleep(1)
    client.disconnect()