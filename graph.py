# coding=utf-8

'''
Created on 06.11.2010

@author: benedikt
'''
from threading import Thread
import time, rrdtool

class graph(Thread):

    configPool = None    
    
    def __init__ (self, cp):
        Thread.__init__(self)
        self.config = cp
        
    def run(self):
        place = ['Innen', 'Aussen']
        
        hours = [1, 12, 24, ( 24 * 7 ), ( 24 * self.dmonth(1) ), ( 24* self.dmonth(2) ), ( 24 * self.dmonth(6) ), ( 24 * self.dmonth(12) ) ]

        while 1:
            
            i = 0
            for x in hours:
              self.mkSecGraph('Anwesend', 'tuer', x, self.config.get('security', 'graphFile') % (i, "Anwesend"), self.config.get('security', 'rrdFile'))
              for pl in place:
                  self.mkTempGraph(pl, x, self.config.get('weather', 'graphFile') % (i, pl), self.config.get('weather', 'rrdFile'))
              i = i+1
              
            time.sleep(60)

    def mkSecGraph (self, place1, place2, dauer, graph, file):
    
      actTime = int(time.time())
    
      if dauer >= 24:
        tempText = '%s (%f Tage)' % (place1, (dauer / 24))
      else:
        tempText = '%s (%f Stunden)' % (place1, dauer)
    
      dsname1 = place1.lower()
      dsname2 = place2.lower()
    
      rrdtool.graph(graph ,
            '--start' , str(int(actTime - (dauer * 3600))) ,
            '--end' , str(actTime) ,   
            '--imgformat' , 'PNG' ,
            '--title' , tempText ,  
            'DEF:ds0=%s:%s:MAX' % (file, dsname1) ,
            'DEF:ds1=%s:%s:MAX' % (file, dsname2) ,
            'CDEF:ds10=1,ds1,-',
            'AREA:ds10#67E667:%s' %place2,
            'AREA:ds1#FF0700:%s' % place2,
            'LINE2:ds0#0000FF:%s' % place1,
      )
    
    def dmonth (self, mback):
        azeit = time.localtime()
    
        amonth = azeit[1]-1
    
        dpmonth = [31,(28 + azeit[8]),31,30,31,30,31,30,31,30,31,30]
    
        lmonth = amonth - mback
    
        if lmonth < 0:
            lmonth = amonth - mback + 12
            dppmonth = dpmonth [:amonth:] + dpmonth [lmonth::]
        else:
            dppmonth = dpmonth [lmonth:amonth]
        
        dreturn = 0
    
        for y in dppmonth:
            dreturn = dreturn + y
        
        return dreturn
    


    def mkTempGraph (self, place, dauer, graph, file):
    
      actTime = int(time.time())
    
      if dauer >= 24:
        tempText = '%s Temperatur (%f Tage)' % (place, (dauer / 24))
      else:
        tempText = '%s Temperatur (%f Stunden)' % (place, dauer)
    
      CDEF12 = dauer * 300
      CDEF2 = dauer * 1800
    
      dsname = place.lower()
    
      rrdtool.graph(graph ,
            '--start' , str(int(actTime - (dauer * 3600))) ,
            '--end' , str(actTime) ,   
            '--vertical-label' , '°C' ,
            '--imgformat' , 'PNG' ,
            '--title' , tempText ,  
            'DEF:ds0=%s:%s:AVERAGE' % (file, dsname) ,
    
            'VDEF:valmax=ds0,MAXIMUM' ,
            'VDEF:valavg=ds0,AVERAGE' ,
            'VDEF:valmin=ds0,MINIMUM' ,
    
            'CDEF:val2Trend=ds0,%i,TREND' % CDEF12,  
            'CDEF:val12Trend=ds0,%i,TREND' % CDEF2,
    
            'LINE1:ds0#FF0000:%s (5 Min)' % place,
            'LINE1:val2Trend#00FF00:%s (1 Std)' % place ,   
            'LINE1:val12Trend#0000FF:%s (6 Std)' % place ,
    
            r'GPRINT:valmax:%s Max\: %%6.1lf °C' % place ,
            r'GPRINT:valavg:%s Avg\: %%6.1lf °C' % place ,  
            r'GPRINT:valmin:%s Min\: %%6.1lf °C\l' % place ,
       
      )

