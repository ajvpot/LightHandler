from twisted.web import resource

class FlashResource(resource.Resource):
    def __init__(self, interface):
        self.interface = interface
    def render_GET(self, request):
        r = int(request.args["r"][0])
        g = int(request.args["g"][0])
        b = int(request.args["b"][0])
        times = int(request.args["times"][0])
        delay = float(request.args["delay"][0])
        self.interface.queueEvent(["flash", r, g, b, times, delay])
        return "Appended flash event"