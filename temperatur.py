# coding=utf-8

'''
Created on 06.11.2010

@author: benedikt
'''
from threading import Thread
#import pycurl
import re, StringIO, urllib, time, rrdtool, json, socket

class temperatur(Thread):

    dataPool = None
    configPool = None
    host = None
    matchpattern = None
    devices = None
    command = None
    
    def __init__ (self, cp, dp):
        Thread.__init__(self)
        self.dataPool = dp
        self.config = cp
        
        settings = json.loads(cp.get('weather', 'temperature'))
        
        self.host = str(settings['host'])
        self.matchpattern = re.compile(settings['matchpattern'], re.IGNORECASE)
        self.devices = settings['devices']
        self.command = settings['command']
        
    # Function um einen befehl an ein Gerät zu schicken.
    def sendCmd(self, devid, cmd):
    
        #params = { 'unit_id':devid, 'PW':"login12", 'cmd':cmd }
        
        #c = pycurl.Curl()
        #c.setopt(pycurl.URL, "http://%s/command" % self.host)
        #c.setopt(pycurl.POST, True)
        #c.setopt(pycurl.POSTFIELDS, urllib.urlencode(params))
        #b = StringIO.StringIO()
        #c.setopt(pycurl.WRITEFUNCTION, b.write)
        #try:
        #    c.ptringIO.erform()
        #    response = b.getvalue()
        #    match = re.search(self.matchpattern, response)
        #    if not match:
        #        return False
        #    return match.groupdict()       
        #except pycurl.error:
        #    return False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((self.host, 1000))
            s.send("%s%s\r" % (devid, cmd))
            response = s.recv(512)
            s.close()
            match = re.search(self.matchpattern, response)
            if not match:
                return False
            return match.groupdict()
        except socket.error:
            return False
        except socket.timeout:
            return False

    def getTempFromDevice(self, dev):

	temp = self.sendCmd(dev, self.command)
        if not temp:
            temp = {'val': '-99'}

	return temp
   
    def getTemps(self):
	temps = []
        for k in self.devices:
            temp = self.getTempFromDevice(k)
            temps.append(temp)
            time.sleep(1)
	return temps
 
    def run(self):

        while 1:
            temps = self.getTemps()    
		
	    timeOffset = 0

            tempIn = float(temps[0]['val'])
            tempOut = float(temps[1]['val'])

            self.dataPool['weather']['in'] = tempIn
            self.dataPool['weather']['out'] = tempOut
            
            updateTime = int(int(time.time())/60)*60
            
	    if tempIn < -50:
		time.sleep(5)
		timeOffset = timeOffset + 5
		tmpTemp = self.getTempFromDevice(self.devices[0])
		tempIn = float(temps[0]['val'])

	    if tempOut < -50:
		time.sleep(5)
		timeOffset = timeOffset + 5
                tmpTemp = self.getTempFromDevice(self.devices[1])
                tempOut = float(temps[1]['val'])

            if tempIn > -50 and tempOut > -50:
                try:  
                    rrdtool.update(self.config.get('weather', 'rrdFile') , '%d:%f:%f' % (  updateTime ,  tempIn , tempOut))
		    print "Temperatur: %d In - %f  Out - %f" % (  updateTime ,  tempIn , tempOut)
                except:
                    print "Temperatur rrderror"
                time.sleep(60-timeOffset)
            else:
                print "Temperatur: %f - %f " % (tempIn, tempOut)                 
                
                
