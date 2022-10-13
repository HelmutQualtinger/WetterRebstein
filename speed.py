import time
import machine
print ("Machine frequence: ",machine.freq())
sum=0
t1= time.ticks_ms()
for i in range(100000):
    sum+=i
t2= time.ticks_ms()
print ("sum " +str(sum)+ """"
T:"""+str(t2-t1))
machine.freq(250000000)
print ("Machine frequence: ",machine.freq())
sum=0
t1= time.ticks_ms()
for i in range(100000):
    sum+=i
t2= time.ticks_ms()
print ("sum " +str(sum)+ """"
T:"""+str(t2-t1))
machine.freq(125000000)
