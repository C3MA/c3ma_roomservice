# coding=utf-8

'''
Created on 06.11.2010

@author: benedikt
'''
from threading import Thread
import time, rrdtool, os

class security(Thread):

    dataPool = None
    configPool = None
    updater = None   
 
    def __init__ (self, cp, dp, up):
        Thread.__init__(self)
        self.dataPool = dp
        self.config = cp
        self.updater = up
        
    def run(self):

        while 1:
            updateTime = time.time()
            try:  
                door = (1.0 if (self.dataPool['security']['door']) else 0.0)
                beweg = (1.0 if (self.dataPool['security']['motion']) else 0.0)
                rrdtool.update(self.config.get('security', 'rrdFile') , '%d:%f:%f' % (  updateTime ,  beweg, door))
            except:
                print "Security rrderror"
                pass
            self.updateState()
            time.sleep(1)


    current_state = 1
    trenshold_counter = 1
    keepalive_counter = 120
    lockstate = 1

    def updateState(self):
      lockstate_now = (1 if (self.dataPool['security']['door']) else 0)
      motion_detected = (1 if (self.dataPool['security']['motion']) else 0)
      
      open_trenshold = 1
      close_trenshold = 600 
      state_changed = 0 
      self.trenshold_counter = self.trenshold_counter - 1
      self.keepalive_counter = self.keepalive_counter - 1
      if motion_detected == 1:
#        print ('>>Motion_detected')
        if self.current_state == 0:
#          print ('>>current_state == 0')
          if self.trenshold_counter <= 0:
#            print ('>>trenshold_counter <= 0')
            self.current_state = 1
            state_changed = 1
        else:
          self.trenshold_counter = close_trenshold
#          print ('>>current_state == 1')
      else:
#        print ('>>NO Motion_detected')
        if self.current_state == 1:
#          print ('>>current_state == 1')
          if self.trenshold_counter <= 0:
#            print ('>>trenshold_counter <= 0')
            self.current_state = 0
            state_changed = 1
        else:
          self.trenshold_counter = open_trenshold
#          print ('>>current_state == 0')
      if (self.lockstate != lockstate_now):
        state_changed = 1
#        print ('>>lockstate :%i!=lockstate_now: %i' % (self.lockstate ,lockstate_now))
      self.lockstate = lockstate_now
      if ((state_changed == 1) or (self.keepalive_counter < 0)):
	print "Sec Upload"
        self.updater.upload()
	if (self.current_state == 1):
          self.dataPool['security']['motion_C'] = "OPEN"
        else:
          self.dataPool['security']['motion_C'] = "CLOSED"
        self.keepalive_counter = 120
