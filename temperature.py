# Bibliotheken laden
from machine import ADC
from utime import sleep
import time
# Initialisierung des ADC4
sensor = ADC(4)
conversion_factor = 3.3 / (4095)
samples=1000
# Wiederholung einleiten (Schleife)
s=0
s2=0
t1=time.ticks_ms()
for i in range (samples):
    # Temparatur-Sensor als Dezimalzahl lesen
    sample = sensor.read_u16()>>4
    s+=sample
    s2+=sample*sample
t2=time.ticks_ms()
print ("time ", t2-t1)
average = s*1.0/samples
noise   = s2*1.0/samples-average*average
    
print ("s",s)
print ("s2",s2)

    # Dezimalzahl in eine reele Zahl umrechnen
spannung = average * conversion_factor
    # Spannung in Temperatur umrechnen
temperatur = 27 - (spannung - 0.706) / 0.001721
    # Ausgabe in der Kommandozeile/Shell
print("Dezimalzahl: ", average)
print("Spannung (V): ", spannung)
print("Temperatur (°C): ", temperatur)
print("Noise :",(noise**0.5)*conversion_factor/0.001721)
print()
