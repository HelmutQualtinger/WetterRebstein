from machine import Timer
import utime
m=0
def timer_routine(dummy):
     global m
     global button_pressed
     print("Welcome to Microcontrollerslab")
     print("Message "+str(m))
     print("Button pressed:"+str(button_pressed))
     m+=1
    
timer = Timer(period=5000, mode=Timer.PERIODIC, callback=timer_routine)
import _thread
button_pressed=1

def button_reader_thread():
    global button_pressed
    while True:
        button_pressed+=1
        utime.sleep(0.01)

_thread.start_new_thread(button_reader_thread, ())