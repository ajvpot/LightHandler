from twisted.web import server, resource
from twisted.internet import reactor, task
from twisted.internet import threads

from time import sleep
import os
from random import randint
from urllib import quote_plus

from schemes import schemePresets, schemeDefault

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
        

class SimpleHTTP(resource.Resource):
    isLeaf = True
    def __init__(self, handler):
        self.queue=handler

    def render_GET(self, request):
        if request.path == "/":
            out = """
<LINK href="http://bgrins.github.com/spectrum/spectrum.css" rel="stylesheet" type="text/css">
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
<script src="http://bgrins.github.com/spectrum/spectrum.js"></script>
<style>
body{background-color:black;}
</style>
<input type='text' class="basic" id="pick"/>
<br />
<div style="background-color:white">
"""
            for key in schemePresets.keys():
                out += '<input type="button" url="/scheme?preset=%s" class="ajaxify" value="%s" /> ' % (quote_plus(key), key)
            out += """
<br />
<input type="button" url="/flash?r=255&g=0&b=0&times=2&delay=0.25" class="ajaxify" value="Flash Red" /> 
<input type="button" url="/flash?r=0&g=255&b=0&times=2&delay=0.25" class="ajaxify" value="Flash Green" /> 
<input type="button" url="/flash?r=0&g=0&b=255&times=2&delay=0.25" class="ajaxify" value="Flash Blue" /> 
</div>
<div id="response" style="background-color:white">test</div>
<script>
function hexToR(h) {return parseInt((cutHex(h)).substring(0,2),16)}
function hexToG(h) {return parseInt((cutHex(h)).substring(2,4),16)}
function hexToB(h) {return parseInt((cutHex(h)).substring(4,6),16)}
function cutHex(h) {return (h.charAt(0)=="#") ? h.substring(1,7):h}
$("#pick").spectrum({
    color: "#f00",
    change: function(color) {
        $('#response').load('/color?r='+hexToR(color.toHexString())+'&g='+hexToG(color.toHexString())+'&b='+hexToB(color.toHexString()))
    },
	flat: true
	
});
$('.ajaxify').click(function(e) {
    e.preventDefault();
    $('#response').load($(this).attr('url'));
});
</script>"""
            return out
        elif request.path == "/flash":
            r = int(request.args["r"][0])
            g = int(request.args["g"][0])
            b = int(request.args["b"][0])
            times = int(request.args["times"][0])
            delay = float(request.args["delay"][0])
            self.queue.append(["flash", r, g, b, times, delay])
            return "Appended flash event"
        elif request.path == "/scheme":
            preset = request.args["preset"][0]
            if not preset in schemePresets:
                request.setResponseCode(500)
                return "Unknown preset"
            self.queue.append(["scheme", preset])
            return "Appended scheme update event to %s" % preset
        elif request.path == "/color":
            r = int(request.args["r"][0])
            g = int(request.args["g"][0])
            b = int(request.args["b"][0])
            self.queue.append(["color", r, g, b])
            return "Appended color event"
        elif request.path == "/fadetime":
            fadetime = int(request.args["fadetime"][0])
            self.queue.append(["fadetime", fadetime])
            return "Appended fadetime update"
        elif request.path == "/getqueue":
            return "%s" % (self.queue)
        else:
            request.setResponseCode(404)
            return "U R A 404 MMK?"


lightQueue = []
site = server.Site(SimpleHTTP(lightQueue))
reactor.listenTCP(8080, site)
interface = LightInterface(lightQueue)
threads.deferToThread(interface.runHandler)

reactor.run()