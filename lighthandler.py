from twisted.web import server, resource
from twisted.internet import reactor, task
from twisted.web.error import Error
from twisted.internet import threads
from time import sleep
import os
from random import randint

from sys import stdout
from twisted.python.log import startLogging
startLogging(stdout)

def setLights(r,g,b):
    max = .5
    r = (max/255.0) * int(r)
    g = (max/255.0) * int(g)
    b = (max/255.0) * int(b)
    os.system("echo 5="+str(r)+" > /dev/pi-blaster" )
    os.system("echo 2="+str(g)+" > /dev/pi-blaster" )
    os.system("echo 6="+str(b)+" > /dev/pi-blaster" )

def lightHandler(queue):
    current = [0,0,0]
    scheme = [[232,95,13],[255,130,14],[255,89,27],[232,39,0],[255,30,14]] #red
    fadetime = 100
    while reactor.running:
        try:
            event = queue.pop()
        except IndexError:
            event = None
        #print event
        if event == None:
            print "Doing random fade"
            fadeto = randint(0,len(scheme)-1)
            rstep = (scheme[fadeto][0] - current[0]) / float(fadetime)
            gstep = (scheme[fadeto][1] - current[1]) / float(fadetime)
            bstep = (scheme[fadeto][2] - current[2]) / float(fadetime)
            for i in range(fadetime):
                current[0] += rstep
                current[1] += gstep
                current[2] += bstep
                setLights(current[0], current[1], current[2]) 
                sleep(0.0001)
                if len(queue) > 0: #interrupt if there's more important stuff to do
                    print "interrupted"
                    break
            if len(queue) > 0: #interrupt if there's more important stuff to do
                print "second interrupt triggered"
                continue
            else:
                sleep(1)         
        elif event[0] == "flash":
            print "flash that shit"
            for i in range(event[4]):
                setLights(0,0,0)
                sleep(event[5])
                setLights(event[1], event[2], event[3])
                current = [event[1], event[2], event[3]]
                sleep(event[5])

        elif event[0] == "scheme":
            if event[1] == 1:
                scheme = [[232,95,13],[255,130,14],[255,89,27],[232,39,0],[255,30,14]] #red
            print "scheme reset"
        elif event[0] == "fadetime":
            fadetime = event[1]
            print "fadetime reset to", fadetime 
        elif event[0] == "color":
            scheme = [[event[1], event[2], event[3]]] #red
            print "color reset"
        else:
            print "got unknown event"
        

class SimpleHTTP(resource.Resource):
    isLeaf = True
    def __init__(self, handler):
        self.queue=handler

    def render_GET(self, request):
        if request.path == "/":
            return """
<LINK href="http://bgrins.github.com/spectrum/spectrum.css" rel="stylesheet" type="text/css">
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
<script src="http://bgrins.github.com/spectrum/spectrum.js"></script>
<style>
body{background-color:black;}
</style>
<input type='text' class="basic" id="pick"/>
<script>
function hexToR(h) {return parseInt((cutHex(h)).substring(0,2),16)}
function hexToG(h) {return parseInt((cutHex(h)).substring(2,4),16)}
function hexToB(h) {return parseInt((cutHex(h)).substring(4,6),16)}
function cutHex(h) {return (h.charAt(0)=="#") ? h.substring(1,7):h}
$("#pick").spectrum({
    color: "#f00",
    change: function(color) {
        $.get('/color?r='+hexToR(color.toHexString())+'&g='+hexToG(color.toHexString())+'&b='+hexToB(color.toHexString()))
    },
	flat: true
	
});
</script>"""
        elif request.path == "/flash":
            r = int(request.args["r"][0])
            g = int(request.args["g"][0])
            b = int(request.args["b"][0])
            times = int(request.args["times"][0])
            delay = float(request.args["delay"][0])
            self.queue.append(["flash", r, g, b, times, delay])
            return "Appended flash action"
        elif request.path == "/scheme":
            preset = int(request.args["preset"][0])
            self.queue.append(["scheme", preset])
            return "Updated scheme"
        elif request.path == "/color":
            r = int(request.args["r"][0])
            g = int(request.args["g"][0])
            b = int(request.args["b"][0])
            self.queue.append(["color", r, g, b])
            return "Updated color"
        elif request.path == "/fadetime":
            fadetime = int(request.args["fadetime"][0])
            self.queue.append(["fadetime", fadetime])
            return "Updated fadetime"
        elif request.path == "/getqueue":
            return "%s" % (self.queue)
        else:
            request.setResponseCode(404)
            return "U R A 404 MMK?"


lightQueue = []
site = server.Site(SimpleHTTP(lightQueue))
reactor.listenTCP(8080, site)
threads.deferToThread(lightHandler, lightQueue)

reactor.run()