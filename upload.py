'''
Created on 04.01.2011

@author: ollo

This module pushes the data to the server.
'''

from threading import Thread
import pycurl, time, urllib

class UploadDeamon(Thread):
    
    dataPool = None
    
    def __init__ (self, cp, dp):
        Thread.__init__(self)
        self.dataPool = dp
        self.config = cp

    def upload(self):

        if len(self.dataPool['security']) <= 0 or len(self.dataPool['weather']) <= 0:
            print "Pool Empty"
            print self.dataPool
            return 

        try:
            params = { 'newState' : self.dataPool['security']['motion_C'], #TODO ist das der richtige status?  
                       'tempInnen' : self.dataPool['weather']['in'],
                       'tempAussen' : self.dataPool['weather']['out'],
                       'timestamp' : int(time.time() ),
                       'door' : (1 if (self.dataPool['security']['door']) else 0),
                       'rain' : (1 if (self.dataPool['weather']['rain']) else 0)
                      }

        except Exception:
            params = {}

        c = pycurl.Curl()
        c.setopt(pycurl.URL, self.config.get('upload', 'service_endpoint'))
        c.setopt(pycurl.POST, True)
        c.setopt(pycurl.POSTFIELDS, urllib.urlencode(params))
        try:
            c.perform()
            print params
            print "Data is uploaded"
        except pycurl.error:
            print "An error occured"
	    print params
	    raise
        
    def run(self):
        
        while 1:
            
            #sleep and wait for the next cycle
            time.sleep(300) # 300 = 5 minutes
            print "Timed Upload"
            self.upload()

        
