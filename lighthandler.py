from twisted.web import server, resource, static, script
from twisted.internet import reactor, task
from twisted.internet import threads

from time import sleep
import os
from random import randint

from flash import FlashResource
from scheme import SchemeResource
from color import ColorResource
from fadetime import FadetimeResource
from queue import QueueResource
from root import RootResource

from schemesettings import schemePresets, schemeDefault

from sys import stdout
from twisted.python.log import startLogging
startLogging(stdout)

class LightInterface():
    def __init__(self, queue):
        self.current = [0,0,0]
        self.scheme = schemePresets[schemeDefault]
        self.fadetime = 100
        self.queue = queue

    def setLights(self, r,g,b):
        self.current = [r,g,b]
        max = .5
        r = (max/255.0) * int(r)
        g = (max/255.0) * int(g)
        b = (max/255.0) * int(b)
        os.system("echo 5="+str(r)+" > /dev/pi-blaster" )
        os.system("echo 2="+str(g)+" > /dev/pi-blaster" )
        os.system("echo 6="+str(b)+" > /dev/pi-blaster" )
    
    def fadeTo(self, r, g, b, fadetime, interruptable = True):
        rstep = (r - self.current[0]) / float(fadetime)
        gstep = (g - self.current[1]) / float(fadetime)
        bstep = (b - self.current[2]) / float(fadetime)
        for i in range(fadetime):
            self.setLights(self.current[0] + rstep, self.current[1] + gstep, self.current[2] + bstep) 
            sleep(0.0001)
            if len(self.queue) > 0 and interruptable: #interrupt if there's more important stuff to do
                print "Fade interrupted by %s" % self.queue[0][0]
                return
        self.current = [r,g,b] #sometimes step doesn't quite set this correctly
        sleep(1)   

    def runHandler(self):
        while reactor.running:
            try:
                event = self.queue.pop()
            except IndexError:
                event = None
            #print event
            if event == None:
                if len(self.scheme) == 1:
                    if not self.scheme[0] == self.current:
                        print "Single color, needs update"
                        self.fadeTo(self.scheme[0][0], self.scheme[0][1], self.scheme[0][2], self.fadetime)
                    else:
                        print "Single color, no update"
                        sleep(1)
                else:
                    print "No actions in queue, doing random fade."
                    fadeto = randint(0,len(self.scheme)-1)
                    self.fadeTo(self.scheme[fadeto][0], self.scheme[fadeto][1], self.scheme[fadeto][2], self.fadetime)
            elif event[0] == "flash":
                print "running flash event"
                for i in range(event[4]):
                    self.setLights(0,0,0)
                    sleep(event[5])
                    self.setLights(event[1], event[2], event[3])
                    sleep(event[5])

            elif event[0] == "scheme":
                self.scheme = schemePresets[event[1]]
                print "scheme reset"
            elif event[0] == "fadetime":
                self.fadetime = event[1]
                print "fadetime reset to", fadetime 
            elif event[0] == "color":
                self.scheme = [[event[1], event[2], event[3]]]
                print "color reset"
            else:
                print "got unknown event"

lightQueue = []

root = static.File("static/")
root.putChild('flash', FlashResource(lightQueue))
root.putChild('scheme', SchemeResource(lightQueue))
root.putChild('color', ColorResource(lightQueue))
root.putChild('fadetime', FadetimeResource(lightQueue))
root.putChild('getqueue', QueueResource(lightQueue))
root.putChild('', RootResource(lightQueue))

reactor.listenTCP(8080, server.Site(root))

interface = LightInterface(lightQueue)
threads.deferToThread(interface.runHandler)

reactor.run()