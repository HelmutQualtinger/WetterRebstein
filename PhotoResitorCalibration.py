print("Fotowiderstandseichung")
from paho.mqtt import client as mqc
print("MQTT unportiert")
import random, json
import time
print("und was sonst noch so anfällt")
broker = '44.194.245.171'
port = 1883
topic_sub = "qualtinger/devices/me/telemetry"
topic_pub = "qualtinger/devices/me/command"
client_id = f'python-mqtt-{random.randint(0, 100000)}'
username = ''

light_intensity=[]
ADC_count=[]

def publish(client):
    msg_count = 0
    global ADC_count,light_intensity
 #    while True:

    message_dict = {
                "duty": 0,
                "pwmfreq": 10240
                }
    msg=json.dumps(message_dict)
    result = client.publish(topic_pub, msg)
    time.sleep(5.5)
    light_intensity=[]
    ADC_count=[]
    
    for duty in range(0,65536,int(65535/10)):
             time.sleep(5.5)
             message_dict = {
                "duty": duty,
                "pwmfreq": 10240
             }
             msg=json.dumps(message_dict)
             result = client.publish(topic_pub, msg)
             # result: [0, 1]
             status = result[0]
             if status == 0:
                 pass
                 print(f"Send `{msg}` to topic `{topic_pub}`")
             else:
                 print(f"Failed to send message to topic {topic_pub}")
             msg_count += 1



def measurement_arrived(client, userdata, msg): 
        measurements=json.loads(msg.payload)
        print(f'{measurements["duty"]} -> {measurements["light"]} at {measurements["pwmfreq"]}')
        light_intensity.append(measurements["duty"])
        ADC_count.append(measurements["light"])



def measure():
    global ADC, Widerstand, Licht,Leitwert
    client = mqc.Client(client_id)
    client.connect(broker, port)
    client.loop_start()
    client.subscribe(topic_sub)
    client.on_message = measurement_arrived
    publish(client)
    time.sleep(1)
    client.loop_stop()
    ADC=np.array(ADC_count)
    Widerstand= ADC/(4096-ADC)*10000
    Leitwert=1/Widerstand*1e6
    Licht = np.array(light_intensity)/65536.*100

print("Ein bisserl Mathematik brauch es noch")
import numpy as np
print("1/2")
import matplotlib.pyplot as plt
print("1")
import matplotlib
from matplotlib import rc

print("Jetzt geht es los")

def plot():

    fig, axis = plt.subplots(1, 1)
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10, 6, forward=True)

    plt.suptitle('Eichung eines Fotwiderstandes', fontsize=16)

    plt.xlabel("Licht (Lux)")
    plt.ylabel(r"Leitwert ($\mu$Siemens)")
 #   plt.scatter(Leitwert,Licht)
    s, l,c = np.polyfit(Leitwert[1:-1], Licht[1:-1], 2)
    plt.plot( Licht, Leitwert, 'yo', s*Leitwert**2+l*Leitwert+c, Leitwert, '-k')
    axis.set_title('Leitwert')
  
    fitparams=f"{s:.6f}*x^2+{l:.3f}*x+{c:.3f}"
    print(fitparams)
    plt.title(fitparams)
    plt.show()
print("Messung starten")
measure()
plot()

