import usocket as socket
import time
import machine
import secrets
import network
from machine import Pin
 
intled = machine.Pin("LED", machine.Pin.OUT)
# 
wlan = network.WLAN(network.STA_IF)
wlan.config(pm = 0xa11140)        # do not shut down WLAN
wlan.active(True)
wlan.connect(secrets.ssid, secrets.password)

# begiining part of HTML page sent by server
html_b = """<!DOCTYPE html>
<html>
<head><title>From Pico W</title>
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
<META HTTP-EQUIV="Expires" CONTENT="-1"></head>
<body>
<h1>Page sent from Pico W</h1>
<p>Turn the Onboard Led ON or OFF</p>
<p><a href='/light/on'>Turn Light On</a></p>
<p><a href='/light/off'>Turn Light Off</a></p>
<br>
"""
# end part of HTML page sent by server
html_e = "</body></html>"
 
# wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() == 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
 
# open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
 
s = socket.socket()
s.bind(('',80))
s.listen(5)
 
print('listening on', addr)
 
# Listen for page requests
while True:
    try:
        print("waiting for a page request")
        cl, addr = s.accept()
        print('client connected from', addr)
        time.sleep(0.1)
        request = cl.recv(2048)
        print("bytes received: ", len(request))
        
        if len(request) == 0:   # should not happen, but it does sometimes with safari
            print("zero bytes received, but accept terminated")
            continue
            
        request = str(request)[0:50]           # extract URL from receive buffer
        request = request.split()
        print('requested URL: ', request[1])
        
        if request[1] == '/favicon.ico':
            response = "<!DOCTYPE html><html><head><title>no icon</title></head><body></body></html>"
            # Pico W has no favicon.ico sends fake page
            
        elif request[1] == '/light/on':
            intled.value(1)
            response = html_b + "<p>LED is ON</p>" + "<p>URL: " + request[1] + "</p>" + html_e

        elif request[1] == '/light/off':
            intled.value(0)
            response = html_b + "<p>LED is OFF</p>" + "<p>URL: " + request[1] + "</p>" + html_e
     
        else:
            response = html_b + "<p>Unrecognized Page Request</p>" + "<p>URL: " + request[1] + "</p>" + html_e
            
        # print(response)
            
        # cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        
        print("page sent")
 
    except OSError as e:
        cl.close()
        print('connection closed')