'''
Created on 06.11.2010

@author: benedikt
'''
from threading import Thread
import socket, re

class service(Thread):

    dataPool = None
    s = None # socket
    shouldStop = False
    
    def __init__ (self, dp):
        Thread.__init__(self)
        self.dataPool = dp
        
    def run(self):
        HOST = ''
        PORT = 3434
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen(1)
        
        while self.shouldStop != True:
            conn, addr = self.s.accept()
            print 'Connected by %s. Starting worker Thread...' % str(addr)
            serviceWorker(self.dataPool, conn, addr).start()
            
    def stop():
        self.shouldStop = True
        self.s.close()

class serviceWorker(Thread):

    dataPool = None
    connection = None
    address = None
    matchPat = re.compile("(regen|bewegung|tuer):(on|off|1|0)", re.IGNORECASE)
    
    def __init__ (self, dp, con, addr):
        Thread.__init__(self)
        self.dataPool = dp
        self.connection = con
        self.address = addr
        
    def run(self):
        while 1:
            data = self.connection.recv(1024)
            if not data: break
    
            tmp = re.match(self.matchPat, data)
    
            if tmp:
                key1 = None
                key2 = None
                if(tmp.group(1).lower() == "regen"):
                    key1 = 'weather'
                    key2 = 'rain'
                elif(tmp.group(1).lower() == "bewegung"):
                    key1 = 'security'
                    key2 = 'motion'
                elif(tmp.group(1).lower() == "tuer"):
                    key1 = 'security'
                    key2 = 'door'
                                            
                if(key1 and key2):
                    if(tmp.group(2).lower() == "on" or tmp.group(2).lower() == "1"):
                        self.dataPool[key1][key2] = True
                    else:
                        self.dataPool[key1][key2] = False
            else:
                print data
            
        self.connection.close()
        print 'Disconnected %s' % str(self.address)
