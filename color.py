from twisted.web import resource


class ColorResource(resource.Resource):

    def __init__(self, interface):
        self.interface = interface

    def render_GET(self, request):
        r = int(request.args["r"][0])
        g = int(request.args["g"][0])
        b = int(request.args["b"][0])
        self.interface.queueEvent(["color", r, g, b])
        return "Appended color event"
