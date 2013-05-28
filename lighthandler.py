from twisted.web import server, resource, static
from twisted.internet import reactor, task
from twisted.internet import threads

from flash import FlashResource
from scheme import SchemeResource
from color import ColorResource
from fadetime import FadetimeResource
from queue import QueueResource
from root import RootResource
from getcolor import GetColorResource
from setintensity import SetIntensityResource

from settings import schemePresets, schemeDefault
from lightinterface import LightInterface

from sys import stdout
from twisted.python.log import startLogging
startLogging(stdout)

interface = LightInterface()

root = static.File("static/")
root.putChild('flash', FlashResource(interface))
root.putChild('scheme', SchemeResource(interface))
root.putChild('color', ColorResource(interface))
root.putChild('fadetime', FadetimeResource(interface))
root.putChild('getqueue', QueueResource(interface))
root.putChild('getcolor', GetColorResource(interface))
root.putChild('setintensity', SetIntensityResource(interface))
root.putChild('', RootResource(interface))

reactor.listenTCP(8080, server.Site(root))
threads.deferToThread(interface.runHandler)

reactor.addSystemEventTrigger("before", "shutdown", interface.stopHandler)

reactor.run()