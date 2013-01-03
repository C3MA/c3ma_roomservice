#!/usr/bin/python
'''
Created on 06.11.2010

@author: benedikt
'''

from service import service
from temperatur import temperatur
from upload import UploadDeamon
from security import security
from graph import graph

import rrdtool, os.path, time, ConfigParser, json, signal, sys#, pdb

def checkRRD(config):
    rrdFiles = [config.get('weather', 'rrdFile'), config.get('security', 'rrdFile')]
    for val in enumerate(rrdFiles):
        if not os.path.exists(val[1]):
            stime = int( ( int(time.time() ) - 60 * 86400 ) / 60 ) * 60
            if val[0] == 0:
                arg = json.loads(config.get('weather', 'rrdInit'))
            elif  val[0] == 1:
                arg = json.loads(config.get('security', 'rrdInit'))
            arg.insert(0, val[1])
            arg.insert(1, "--start")
            arg.insert(2, stime)
            
            # Doofer workaround. Liegt an Unicode Strings. Das mag rrdtool scheinbar net.
            i=0
            for a in arg:
                arg[i] = str(a)
                i+=1
                pass

            rrdtool.create(*arg)
            print "Created RRD Database: %s" % val[1]

# This Function fills some dummy-data into the pool
def fillDummyData(dataPool):
    print 'Creating dummy data'
    dataPool['security']['motion']  = True
    dataPool['weather']['in']       = -3.99
    dataPool['weather']['out']      =  10.99
    dataPool['weather']['rain']     = True
    dataPool['security']['door']    =  True
    

ser = None

def kill_signal_handler(signal, frame):
    print 'get Signal'
    ser.stop()
    sys.exit(0)

def main():
        
        config = ConfigParser.SafeConfigParser()
        config.read('/opt/raumServiceDeamon/src/deamon.cfg')
        
        dataPool = {'security': {'motion': False, 'door': False, 'motion_C': "CLOSED"}, 'weather': {'out': 0.0, 'rain': False, 'in': 0.0}}

        checkRRD(config)
        
        signal.signal(signal.SIGINT, kill_signal_handler)
        signal.signal(signal.SIGTERM, kill_signal_handler)
        
        #fillDummyData(dataPool) # DEBUG
#        pdb.set_trace()

        t = UploadDeamon(config, dataPool)
        t.start()
	time.sleep(2) #Quick n' Dirty-Hack, da sonst Exception

        tem = temperatur(config, dataPool)
        tem.start()
	time.sleep(2)
        
        sec = security(config, dataPool, t)
        sec.start()
	time.sleep(2)
        
        gra = graph(config)
        gra.start()
	time.sleep(2)
        
        global ser
        ser = service(dataPool)
        ser.start()
        #ser.join()
        
if __name__ == '__main__':
    main()
    pass
