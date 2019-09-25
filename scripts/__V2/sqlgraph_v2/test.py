import sys,time
for i in range(100):
    k = i + 1
    str = '>'*i+' '*(100-k)
    sys.stdout.write('\r'+str+'[%s%%]'%(i+1))
    sys.stdout.flush()
    time.sleep(0.1)