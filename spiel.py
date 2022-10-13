import array
import time
def array_test():  
    arr=array.array('B',[0]*20000)
    t1=time.ticks_ms()
    s=sum(arr)
#    for i in range(10000):
#        arr[i]=i
#    s=sum(arr)
    t2=time.ticks_ms()
    print (s,t2-t1)