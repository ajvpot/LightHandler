from twisted.web import resource

class SetIntensityResource(resource.Resource):
    def __init__(self, interface):
        self.interface = interface
    def render_GET(self, request):
        self.interface.max = int(request.args["intensity"][0])/float(100)
        return "Set intensity to %s" % self.interface.max