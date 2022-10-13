from machine import Pin, I2C        #importing relevant modules & classes
from time import sleep
import bme280       #importing BME280 library

i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=3000000)    #initializing the I2C method 

measurements={"roomtemp":None,"pressure":None,"humidity":None,}
while True:
  bme = bme280.BME280(i2c=i2c)          #BME280 object created
  measurements["roomtemp"],measurements["pressure"],  measurements["humidity"]= bme.values
  print(str(measurements))
  sleep(0.1)           #delay of 10s